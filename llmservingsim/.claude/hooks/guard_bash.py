#!/usr/bin/env python3
"""PreToolUse hook for the Bash tool: block commands that break a never-break rule (AGENTS.md 0.3).

Reads the hook JSON on stdin ({"tool_name": "Bash", "tool_input": {"command": ...}, "cwd": ...}). Exits 2 with a
one-line reason on stderr to block; exits 0 otherwise. Precision over recall: text that only mentions a banned
command (grep patterns, heredoc bodies, commit messages, echo) is allowed, and any parse failure allows.

Blocked:
  - every `pkill` invocation (any flags, `--help` included), `killall`        (0.3 rule 5)
  - `git push` with --force / -f / --force-with-lease / a `+refspec`          (0.3 rule 7)
  - `git add -A` / `--all` / `.`                                             (I.16)
  - bare `git stash` (= `push`/`save`), `git stash pop` with no ref, every `git stash drop` (any ref or
    options), `git stash clear`                                               (I.16)
  - `timeout ... slotrun`                                                    (0.3 rule 4)
  - printing a token file (`cat gh_token`, `head hf_token`, ...)             (0.3 rule 7)
  - `--dangerously-bypass-approvals-and-sandbox`                             (I.4)
  - `git commit` whose change adds a secret or a token file                  (0.3 rule 7)
  - cleanup operands with an allow-rule prefix that contain `..` or leave `.wt/` (I.7)

Commands are found inside `;`, `&&`, `||`, `|`, newlines, `$(...)`, backticks, `bash -c`/`-lc`, `eval`, shell
keywords (`if/then/else/do/while/{/!`), wrappers (`sudo`, `env`, `nohup`, `time`, `xargs`, `timeout`,
`docker exec`). It is a safety net against mistakes, not against deliberate evasion: globs, variables,
command substitutions that produce a file name, and interpreter code are not followed.
"""
import json
import os
import re
import shlex
import subprocess
import sys

TOKEN_FILES = ("gh_token", "hf_token")
REPO_ROOT = "/home/asd/LLMServingSim"
WORKTREE_ROOT = REPO_ROOT + "/.wt"
# Commands that print a file operand to output.
PRINTERS = {"cat", "tac", "nl", "less", "more", "most", "head", "tail", "xxd", "od", "hexdump", "strings",
            "base64", "base32", "bat", "batcat", "view", "vi", "vim", "nano", "emacs", "pg", "column", "rev",
            "grep", "egrep", "fgrep", "rg", "sed", "awk", "gawk", "cut", "sort", "uniq", "paste"}
# Of the printers, those whose first positional argument is a pattern/script rather than a file (unless the
# pattern is given by an option such as -e / -f).
PATTERN_FIRST = {"grep", "egrep", "fgrep", "rg", "sed", "awk", "gawk"}
PATTERN_OPTS = {"e", "f", "--regexp", "--file", "--expression"}  # these give the pattern/script explicitly
# Options that take a value, per printer: short letters and long names (without `=`).
_GREP_S, _GREP_L = "ABCmefdD", {"--regexp", "--file", "--max-count", "--after-context", "--before-context",
                                "--context", "--include", "--exclude", "--exclude-dir", "--exclude-from",
                                "--label", "--binary-files", "--devices", "--directories", "--group-separator"}
_RG_S, _RG_L = "ABCmefgtTjMErd", {"--regexp", "--file", "--max-count", "--after-context", "--before-context",
                                  "--context", "--glob", "--iglob", "--type", "--type-not", "--type-add",
                                  "--type-clear", "--replace", "--max-depth", "--threads", "--encoding",
                                  "--max-columns", "--sort", "--sortr", "--pre", "--pre-glob", "--ignore-file",
                                  "--max-filesize", "--path-separator", "--colors", "--context-separator",
                                  "--field-match-separator", "--field-context-separator", "--dfa-size-limit",
                                  "--regex-size-limit", "--engine", "--color", "--hyperlink-format"}
VALUE_OPTS = {
    "grep": (_GREP_S, _GREP_L), "egrep": (_GREP_S, _GREP_L), "fgrep": (_GREP_S, _GREP_L), "rg": (_RG_S, _RG_L),
    "sed": ("efl", {"--expression", "--file", "--line-length"}),
    "awk": ("fvF", {"--file", "--assign", "--field-separator"}),
    "gawk": ("fvF", {"--file", "--assign", "--field-separator"}),
    "head": ("nc", {"--lines", "--bytes"}), "tail": ("ncs", {"--lines", "--bytes", "--sleep-interval", "--pid"}),
    "cut": ("bcdf", {"--bytes", "--characters", "--delimiter", "--fields", "--output-delimiter"}),
    "sort": ("kStT", {"--key", "--buffer-size", "--field-separator", "--temporary-directory", "--output"}),
    "od": ("AjNtw", set()), "xxd": ("cglos", set()), "nl": ("bdfhilnsvw", set()),
}
# Commands that only carry text; a banned flag inside their arguments is a mention, not a run.
TEXT_CMDS = {"echo", "printf", "grep", "egrep", "fgrep", "rg", "sed", "awk", "gawk", "cat", "tee", "git", "true",
             ":", "test", "["}
# Wrappers whose argument list is itself a command; value-taking options per wrapper.
WRAPPERS = {"sudo": "ugpChDrtUT", "env": "uCS", "nohup": "", "time": "fo", "exec": "a", "command": "",
            "nice": "n", "ionice": "cnpt", "stdbuf": "ioe", "xargs": "IPLndEsa", "builtin": "", "setsid": "",
            "chronic": "", "unbuffer": ""}
# Shell keywords that may precede a command in the same segment.
KEYWORDS = {"then", "do", "else", "elif", "if", "while", "until", "{", "!", "}", "fi", "done", "esac"}
# Segments starting with these hold no command to check (word lists, patterns).
NO_CMD = {"for", "select", "case", "in", "function"}
SHELLS = {"bash", "sh", "zsh", "dash", "ksh"}
SEPARATORS = {";", "&&", "||", "|", "&", "|&", "(", ")", "\n", ";;"}
BYPASS = "--dangerously-bypass-approvals-and-sandbox"
ASSIGN = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)=(.*)$", re.S)

SECRET_PATTERNS = [
    ("GitHub token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}")),
    ("GitHub fine-grained token", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{22,}")),
    ("Hugging Face token", re.compile(r"\bhf_[A-Za-z0-9]{20,}")),
    ("API key (sk-)", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}")),
    ("AWS access key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("private key", re.compile("-----BEGIN (?:[A-Z0-9]+ )*" + "PRIVATE KEY-----")),
]


class Block(Exception):
    pass


class Ctx:
    """Per-command-line state: the working directory (follows `cd`), for the commit scan."""

    def __init__(self, cwd=None):
        self.cwd = cwd or os.getcwd()


# --- parsing -------------------------------------------------------------------------------------------------


def strip_heredocs(text):
    """Drop heredoc bodies (they are data, not commands); keep the line that opens them."""
    out, lines, i = [], text.split("\n"), 0
    while i < len(lines):
        line = lines[i]
        out.append(line)
        delims = re.findall(r"<<(-?)\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\2", line)
        i += 1
        for dash, _, word in delims:
            while i < len(lines):
                body = lines[i].lstrip("\t") if dash else lines[i]
                i += 1
                if body == word:
                    break
    return "\n".join(out)


def tokenize(text):
    lex = shlex.shlex(text, posix=True, punctuation_chars=";&|()<>\n")
    lex.whitespace = " \t\r"
    lex.whitespace_split = True
    lex.commenters = ""  # comments handled in segments(): only a word that starts with #
    return list(lex)


def segments(tokens):
    seg, comment = [], False
    for t in tokens:
        if comment:
            if t == "\n":
                comment = False
            continue
        if t.startswith("#"):
            comment = True
            continue
        if t in SEPARATORS or (t and set(t) <= set(";&|()\n") and t not in (">", "<")):
            if seg:
                yield seg
            seg = []
        else:
            seg.append(t)
    if seg:
        yield seg


def substitutions(token):
    """Inner texts of $(...) and `...` inside a word, for recursive checking."""
    out, i = [], 0
    while True:
        j = token.find("$(", i)
        if j < 0:
            break
        depth, k = 1, j + 2
        while k < len(token) and depth:
            if token[k] == "(":
                depth += 1
            elif token[k] == ")":
                depth -= 1
            k += 1
        out.append(token[j + 2:k - 1] if depth == 0 else token[j + 2:])
        i = k
    out.extend(re.findall(r"`([^`]*)`", token))
    return out


def base(word):
    return os.path.basename(word)


def is_token_file(word):
    return base(word) in TOKEN_FILES


def skip_opts(args, valued):
    """Skip leading options of a wrapper; `valued` holds the short letters that take a value."""
    while args and args[0].startswith("-") and args[0] != "-":
        a, args = args[0], args[1:]
        if a == "--":
            break
        if not a.startswith("--") and a[-1] in valued and len(a) == 2 and args:
            args = args[1:]
    return args


def unwrap(argv):
    """Strip keywords, env assignments and wrapper commands; return the real argv (or [])."""
    while argv:
        a = argv[0]
        if a in KEYWORDS:
            argv = argv[1:]
            continue
        if a in NO_CMD:
            return []
        if ASSIGN.match(a):
            argv = argv[1:]
            continue
        b = base(a.lstrip("\\"))
        if b in WRAPPERS:
            argv = skip_opts(argv[1:], WRAPPERS[b])
            continue
        if b == "docker" and len(argv) > 1 and argv[1] == "exec":
            rest = argv[2:]
            while rest and rest[0].startswith("-"):
                opt = rest[0]
                rest = rest[1:]
                if opt in ("-e", "--env", "-w", "--workdir", "-u", "--user", "--env-file") and rest:
                    rest = rest[1:]
            argv = rest[1:]  # drop the container name
            continue
        return [a.lstrip("\\")] + argv[1:]
    return argv


def positionals(cmd, args):
    """Return (positional operands, pattern_given_by_option, redirect-input operands)."""
    shorts, longs = VALUE_OPTS.get(cmd, ("", set()))
    pos, redir, explicit, i, opts_done = [], [], False, 0, False
    while i < len(args):
        a = args[i]
        if a in ("<", "<<<") and i + 1 < len(args):
            redir.append(args[i + 1])
            i += 2
            continue
        if a in (">", ">>", ">&", "&>", ">|"):
            i += 2
            continue
        if opts_done or a == "-" or not a.startswith("-"):
            pos.append(a)
            i += 1
            continue
        if a == "--":
            opts_done = True
            i += 1
            continue
        if a.startswith("--"):
            name = a.split("=", 1)[0]
            if name in PATTERN_OPTS:
                explicit = True
            if "=" not in a and name in longs:
                i += 1
            i += 1
            continue
        # short cluster: -A3, -nA 3, -e pat, -epat
        for k, ch in enumerate(a[1:], 1):
            if ch in shorts:
                if ch in PATTERN_OPTS:
                    explicit = True
                if k == len(a) - 1:
                    i += 1  # value is the next argument
                break
        i += 1
    return pos, explicit, redir


def check_cleanup_paths(args):
    """Constrain the cleanup allow-rule prefixes using lexical paths, without following links."""
    paths, _, _ = positionals("", args)
    for path in paths:
        if not path.startswith((".wt/", WORKTREE_ROOT + "/")):
            continue
        normalized = os.path.normpath(os.path.join(REPO_ROOT, path))
        if ".." in path.split("/") or not normalized.startswith(WORKTREE_ROOT + "/"):
            raise Block("I.7: cleanup allow-rule paths must stay strictly inside .wt/ and contain no ..")


def check_argv(argv, ctx, depth):
    argv = unwrap(argv)
    if not argv:
        return
    cmd = base(argv[0])
    args = argv[1:]

    if cmd in SHELLS:
        i, has_c = 0, False
        while i < len(args):
            a = args[i]
            if a in ("-o", "+o", "-O", "+O"):
                i += 2
                continue
            if a.startswith("-") and not a.startswith("--") and "c" in a[1:]:
                has_c = True
            elif not a.startswith(("-", "+")):
                if has_c:
                    check_text(a, ctx, depth + 1)
                return
            i += 1
        return

    if cmd == "eval":
        check_text(" ".join(args), ctx, depth + 1)
        return

    if cmd == "timeout":
        if any(base(a) == "slotrun" for a in args):
            raise Block("0.3 rule 4: never wrap slotrun in timeout")
        rest = list(args)
        while rest and rest[0].startswith("-"):
            opt = rest.pop(0)
            if opt in ("-s", "--signal", "-k", "--kill-after") and rest:
                rest.pop(0)
        check_argv(rest[1:], ctx, depth)  # drop the duration
        return

    if cmd == "killall":
        raise Block("0.3 rule 5: never killall; kill by PID")
    if cmd == "pkill":
        raise Block("0.3 rule 5: never pkill; kill by PID")

    if BYPASS in args and cmd not in TEXT_CMDS:
        raise Block("I.4: never run Codex with " + BYPASS)

    if cmd in PRINTERS:
        pos, explicit, redir = positionals(cmd, args)
        if any(is_token_file(r) for r in redir):
            raise Block("0.3 rule 7: never print a token file")
        if cmd in PATTERN_FIRST and not explicit and pos:
            pos = pos[1:]
        for p in pos:
            if is_token_file(p):
                raise Block("0.3 rule 7: never print a token file (" + base(p) + ")")

    if cmd == "unlink":
        check_cleanup_paths(args)

    if cmd == "git":
        check_git(args)


def git_sub(args):
    """Split git's global options from the subcommand. Returns (opts dict, sub, subargs)."""
    opts, i = {"C": []}, 0
    while i < len(args):
        a = args[i]
        if a == "-C" and i + 1 < len(args):
            opts["C"].append(args[i + 1])
            i += 2
        elif a in ("-c", "--git-dir", "--work-tree", "--namespace", "--exec-path") and i + 1 < len(args):
            i += 2
        elif a.startswith("-"):
            i += 1
        else:
            return opts, a, args[i + 1:]
    return opts, None, []


def check_git(args):
    _, sub, sa = git_sub(args)
    if sub is None or "--help" in sa or "-h" in sa:
        return
    if sub == "worktree" and sa[:1] == ["remove"]:
        check_cleanup_paths(sa[1:])
    if sub == "push":
        for a in sa:
            if a in ("--force", "--force-with-lease", "--force-if-includes") or a.startswith("--force-with-lease="):
                raise Block("0.3 rule 7: never force-push")
            if re.match(r"^-[a-zA-Z]+$", a) and "f" in a[1:]:
                raise Block("0.3 rule 7: never force-push")
            if not a.startswith("-") and (a.startswith("+") or ":+" in a) and len(a) > 1:
                raise Block("0.3 rule 7: never force-push (+refspec)")
    elif sub == "add":
        opts_done = False
        for a in sa:
            if a == "--" and not opts_done:
                opts_done = True
                continue
            if a in (".", "./"):
                raise Block("I.16: stage only your own files; never git add -A / --all / .")
            if not opts_done and (a in ("--all", "-A") or (re.match(r"^-[a-zA-Z]+$", a) and "A" in a[1:])):
                raise Block("I.16: stage only your own files; never git add -A / --all / .")
    elif sub == "stash":
        rest = list(sa)
        if not rest or rest[0].startswith("-") or rest[0] in ("push", "save"):
            raise Block("I.16: the stash is shared; never bare git stash (prefer a WIP commit)")
        if rest[0] == "clear":
            raise Block("I.16: the stash is shared; never git stash clear")
        if rest[0] == "drop":
            raise Block("I.16: the stash is shared; never git stash drop")
        if rest[0] == "pop":
            refs = [a for a in rest[1:] if not a.startswith("-")]
            if not refs:
                raise Block(f"I.16: the stash is shared; never git stash {rest[0]} without an explicit ref")


def walk(text, ctx, depth=0):
    """Yield (segment, unwrapped argv) for every command segment; follows `cd`."""
    if depth > 4:
        return
    for seg in segments(tokenize(strip_heredocs(text))):
        argv = unwrap(seg)
        if argv[:1] == ["cd"] and len(argv) > 1:
            d = os.path.expanduser(argv[1])
            ctx.cwd = os.path.normpath(d if os.path.isabs(d) else os.path.join(ctx.cwd, d))
        yield seg, argv


def check_text(text, ctx=None, depth=0):
    if depth > 4:
        return
    ctx = ctx or Ctx()
    for seg, _ in walk(text, ctx, depth):
        for t in seg:
            for inner in substitutions(t):
                check_text(inner, Ctx(ctx.cwd), depth + 1)
        check_argv(seg, ctx, depth)


# --- secret scan on git commit -------------------------------------------------------------------------------


def commit_targets(text, cwd):
    """Yield (dir, commit_args) for each `git commit` in the command, following `cd` and `git -C`."""
    ctx = Ctx(cwd)
    for _, argv in walk(text, ctx):
        if argv and base(argv[0]) == "git":
            opts, sub, sa = git_sub(argv[1:])
            if sub == "commit":
                d = ctx.cwd
                for c in opts["C"]:
                    d = c if os.path.isabs(c) else os.path.join(d, c)
                yield d, sa


def git_out(d, *args):
    r = subprocess.run(["git", "-C", d] + list(args), capture_output=True, text=True, timeout=30)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip())
    return r.stdout


COMMIT_SHORT_VALUED = "mFCct"
COMMIT_LONG_VALUED = {"--message", "--file", "--author", "--date", "--reuse-message", "--reedit-message", "--fixup",
                      "--squash", "--template", "--cleanup", "--trailer", "--pathspec-from-file", "--untracked-files"}
COMMIT_WHOLE_LONG = {"--all", "--include", "--only", "--pathspec-from-file"}


def commit_scope(sa):
    """True when the commit takes working-tree content (-a, -i, -o, pathspecs), not just the index."""
    whole, i, opts_done = False, 0, False
    while i < len(sa):
        a = sa[i]
        if opts_done or not a.startswith("-") or a == "-":
            whole = True  # pathspec
        elif a == "--":
            opts_done = True
        elif a.startswith("--"):
            name = a.split("=", 1)[0]
            if name in COMMIT_WHOLE_LONG:
                whole = True
            if "=" not in a and name in COMMIT_LONG_VALUED and name != "--untracked-files":
                i += 1
        else:
            for k, ch in enumerate(a[1:], 1):
                if ch in "aio":
                    whole = True
                if ch in "uS":
                    break  # -u<mode>, -S<keyid>: the rest is an optional attached value
                if ch in COMMIT_SHORT_VALUED:
                    if k == len(a) - 1:
                        i += 1  # value is the next argument
                    break  # the rest of the cluster is the value
        i += 1
    return whole


def scan_commit(d, sa):
    """Return a block reason, or None. Never includes the matched secret."""
    if "--dry-run" in sa:
        return None
    rng = ["HEAD"] if commit_scope(sa) else ["--cached"]
    try:
        git_out(d, "rev-parse", "--verify", "-q", "HEAD")
    except RuntimeError:
        rng = ["--cached"]
    names = git_out(d, "diff", *rng, "--name-only", "--diff-filter=AM", "--no-renames").splitlines()
    for n in names:
        if base(n) in TOKEN_FILES:
            return f"0.3 rule 7: commit would add token file {n}; unstage it"
    diff = git_out(d, "diff", *rng, "-U0", "--no-color", "--no-ext-diff", "--diff-filter=AM", "--no-renames")
    path, ln, header = None, 0, False
    for line in diff.splitlines():
        if line.startswith("diff --git "):
            header = True
            continue
        if header:
            if line.startswith("+++ "):
                p = line[4:]
                path = p[2:] if p.startswith("b/") else p
            if line.startswith("@@"):
                header = False
            else:
                continue
        m = re.match(r"^@@ -\S+ \+(\d+)", line)
        if m:
            ln = int(m.group(1))
            continue
        if line.startswith("+") and path:
            for label, pat in SECRET_PATTERNS:
                if pat.search(line):
                    return f"0.3 rule 7: staged change adds a possible secret ({label}) at {path}:{ln}; remove it"
            ln += 1
    return None


def main():
    try:
        data = json.load(sys.stdin)
        if data.get("tool_name") not in (None, "Bash"):
            return 0
        cmd = (data.get("tool_input") or {}).get("command") or ""
        cwd = data.get("cwd") or os.getcwd()
    except Exception:
        return 0
    try:
        check_text(cmd, Ctx(cwd))
    except Block as b:
        print(f"BLOCKED by .claude/hooks/guard_bash.py ({b})", file=sys.stderr)
        return 2
    except Exception:
        pass  # unsure: allow
    if "commit" in cmd:
        try:
            for d, sa in commit_targets(cmd, cwd):
                reason = scan_commit(d, sa)
                if reason:
                    print(f"BLOCKED by .claude/hooks/guard_bash.py ({reason})", file=sys.stderr)
                    return 2
        except Exception:
            pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
