#!/usr/bin/env python3
"""Generate GENERAL.md from the sections marked `<!-- general -->` in AGENTS.md and agents/*.md.

Usage: python3 agents/gen_general.py [--check]

A marked section is the heading plus everything up to the next heading of the same or higher level; the marker
line is dropped and the text is copied verbatim (no substitutions: marked sections are written in general terms).
Each copied section gets a `Source:` line under its heading. --check exits non-zero when GENERAL.md is stale
(diff printed), when a marked section contains a repository-specific token (DENY), or when a marked section cites
a section id that GENERAL.md does not contain (file:line printed for each).

--check also runs the pointer check (AGENTS.md 0.5 item 4: the target of every pointer must exist): every
repository path written in inline backticks or as a markdown link in AGENTS.md, agents/*.md and
.claude/skills/*/SKILL.md must exist. Paths under the research shorthands R/, EX/, AN/ (AGENTS.md 0.4) live on
another branch and are resolved in the worktree .wt/p3/pe if it exists, else skipped with a note.
"""
import difflib
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "GENERAL.md"
MARK = "<!-- general -->"

# (file, label used to prefix unnumbered headings so they stay unique)
FILES = [
    ("AGENTS.md", "Entry"),
    ("agents/INTERFACE.md", "Interface"),
    ("agents/MASTER.md", "Master"),
    ("agents/MANAGER.md", "Manager"),
    ("agents/FORMATS.md", "Formats"),
    ("agents/RECORDS.md", "Records"),
    ("agents/IMPLEMENTER.md", "Implementer"),
    ("agents/LEAF.md", "Leaf"),
    ("agents/VERIFIER.md", "Verifier"),
    ("agents/CODEX.md", "Codex"),
    ("agents/OPERATIONS.md", "Operations"),
]

DENY = [r"/home/asd", r"servingsim", r"slotrun", r"\bR/", r"\bEX/", r"\bAN/", r"\bII\.", r"rate_wl", r"explore/",
        r"\.wt/", r"HANDOFF", r"gh_token", r"vllm", r"ASTRA", r"Dynamo", r"\.vscode",
        # Repository paths of the rule files and Claude settings (roles v2, O14). Only section bodies are checked, so
        # the generated `Source:` labels that name these paths stay legal; "subagents/" does not match.
        r"\bagents/", r"\.claude/"]


def read_sections():
    """Return list of (file, label, level, heading, [(lineno, text)])."""
    out = []
    for rel, label in FILES:
        lines = (ROOT / rel).read_text().splitlines()
        i = 0
        while i < len(lines):
            m = re.match(r"^(#+) (.*)$", lines[i])
            if m and i + 1 < len(lines) and lines[i + 1].strip() == MARK:
                level, head = len(m.group(1)), m.group(2)
                j = i + 2
                in_code = False
                while j < len(lines):
                    if lines[j].startswith("```"):
                        in_code = not in_code
                    m2 = re.match(r"^(#+) ", lines[j])
                    if not in_code and m2 and len(m2.group(1)) <= level:
                        break
                    j += 1
                body = [(k + 1, lines[k]) for k in range(i + 2, j)]
                while body and not body[-1][1].strip():
                    body.pop()
                out.append((rel, label, level, head, body))
                i = j
            else:
                i += 1
    out.extend(read_skills())
    return out


def read_skills():
    """Skills whose first line after the frontmatter is the marker: one `## Skill: <name>` section each.

    The skill's own H1 is demoted (all its headings move two levels down) rather than dropped, because it carries
    the procedure's title, which does not repeat the skill name.
    """
    out = []
    for f in sorted((ROOT / ".claude/skills").glob("*/SKILL.md")):
        lines = f.read_text().splitlines()
        if not lines or lines[0].strip() != "---":
            continue
        end = next((k for k in range(1, len(lines)) if lines[k].strip() == "---"), None)
        if end is None or end + 1 >= len(lines) or lines[end + 1].strip() != MARK:
            continue
        desc, dln = "", end
        for k in range(1, end):
            if lines[k].startswith("description:"):
                desc, dln = lines[k][len("description:"):].strip(), k + 1
        rel = str(f.relative_to(ROOT))
        body = [(dln, ""), (dln, f"Trigger: {desc}"), (dln, "")]
        in_code = False
        for k in range(end + 2, len(lines)):
            t = lines[k]
            if not t.strip() and len(body) == 3:
                continue
            if t.startswith("```"):
                in_code = not in_code
            if not in_code and re.match(r"^#+ ", t):
                t = "##" + t
            body.append((k + 1, t))
        while body and not body[-1][1].strip():
            body.pop()
        out.append((rel, "Skill", 2, f"Skill: {f.parent.name}", body))
    return out


def build():
    parts, ids, hits = [], [], []
    secs = read_sections()
    for rel, label, level, head, body in secs:
        mid = re.match(r"^((?:I|II|0)\.\d+)\b", head)
        if mid:
            ids.append(mid.group(1))
            src = f"Source: `{rel}` {mid.group(1)}"
        else:
            src = f"Source: `{rel}` \"{re.sub(r' \(\d{4}-\d\d-\d\d\)$', '', head)}\""
            if head.startswith("Skill: "):
                src = f"Source: `{rel}`"
            elif not head.startswith(label):
                head = f"{label}: {head}"
        parts.append("\n".join(["#" * level + " " + head, "", src] + [t for _, t in body]))
    for rel, label, level, head, body in secs:
        for ln, t in body:
            pats = [pat for pat in DENY if re.search(pat, t)]
            if pats:  # one hit per line, naming every pattern it matches
                hits.append(f"{rel}:{ln}: repository-specific token {', '.join(map(repr, pats))}: {t.strip()[:100]}")
            for m in re.finditer(r"\b((?:I|II)\.\d+|0\.\d+)\b", t):
                if m.group(1) not in ids:
                    hits.append(f"{rel}:{ln}: cites section {m.group(1)} not in GENERAL.md: {t.strip()[:100]}")
    header = (
        "# GENERAL.md\n\n"
        "Repository-independent rules for agents (Claude Code, Codex, and others): roles and spawning, delegation, "
        "decision rights and escalation, briefs and reports, tests and review, handover between sessions, and safe "
        "git/process habits. This file is generated, verbatim, from the sections marked `<!-- general -->` in a "
        "repository's rule files (`AGENTS.md`, `agents/*.md`) by `agents/gen_general.py`, and is never edited by hand: "
        "change the marked section and regenerate. The general terms the sections use (handoff file, decisions list, "
        "task trail, ...) are defined in section 0.6; each repository's `AGENTS.md` maps them to its own files. "
        "A repository's own `AGENTS.md` wins on anything repository-specific. Each section's `Source:` line names "
        "the file it comes from.\n\n"
        f"Sections: {', '.join(ids)}, plus the role sections (Manager duties, Implementer, Leaf duties, Verifier, Master pitfalls) and the skills ({', '.join(h[7:] for _, _, _, h, _ in secs if h.startswith('Skill: '))}).\n\n---\n\n"
    )
    return header + "\n\n".join(parts) + "\n", hits


# Research shorthands (AGENTS.md 0.4) and the worktree that holds their branch.
SHORTHANDS = {"R": "outputs/pe_mc/srpt_20261002/rate_wl", "EX": "outputs/pe_mc/srpt_20261002/tracelab/explore",
              "AN": "outputs/pe_mc/srpt_20261002/rate_wl/agents-notes"}
RESEARCH_TREE = ROOT / ".wt/p3/pe"
FILE_EXT = (".md", ".py", ".sh", ".json", ".jsonl", ".txt", ".yaml", ".yml", ".csv", ".toml", ".cfg")
REPO_ABS = "/home/asd/LLMServingSim/"


def pointer_candidate(p):
    """Return the path to check, or None if the text does not look like a repository file path."""
    p = p.strip()
    if p.startswith("./"):
        p = p[2:]
    if p.startswith(REPO_ABS):
        p = p[len(REPO_ABS):]
    # Placeholders (<x>), globs, variables, URLs, options, other absolute paths and elisions are not pointers.
    if not p or re.search(r"\s|[<>*?{}\[\]$|=]|://|\.\.\.", p) or p.startswith(("/", "~", "-", "@", ":")):
        return None
    p = re.sub(r"(#.*|:\d+(-\d+)?)$", "", p)
    head = p.split("/", 1)[0]
    if head in SHORTHANDS:
        return p
    if "/" not in p:
        # A bare file name is a pointer only for the extensions the rule names; others are mentions.
        return p if p.endswith((".md", ".py", ".sh")) else None
    if p.endswith(FILE_EXT):
        return p
    # A slash path without a file extension: only when its first component exists here (filters branch names
    # such as feat/pe-srpt or origin/main).
    if "/" in p and ((ROOT / head).exists() or (RESEARCH_TREE / head).exists()):
        return p
    return None


def tracked_files(tree):
    """Paths in the git tree at `tree`: tracked (submodules included) and untracked-but-not-ignored."""
    out = []
    for args in (["--cached", "--recurse-submodules"], ["--others", "--exclude-standard"]):
        try:
            r = subprocess.run(["git", "-C", str(tree), "ls-files", "-z"] + args,
                               capture_output=True, text=True, timeout=60)
            out += [x for x in r.stdout.split("\0") if x] if r.returncode == 0 else []
        except (OSError, subprocess.SubprocessError):
            pass
    return out


# An inline-code span, optionally followed by ` (on `<branch>`)`.
BRANCH_PTR = re.compile(r"`([^`\n]+)`(?:\s*\(on `([^`\s]+)`\))?")


def branch_has(branch, path):
    """True if `path` exists on the local branch, else on origin/<branch>."""
    for ref in (branch, "origin/" + branch):
        r = subprocess.run(["git", "-C", str(ROOT), "cat-file", "-e", f"{ref}:{path}"], capture_output=True)
        if r.returncode == 0:
            return True
    return False


def ignored(p):
    r = subprocess.run(["git", "-C", str(ROOT), "check-ignore", "-q", "--no-index", p], capture_output=True)
    return r.returncode == 0


def pointer_hits():
    """Return (missing, notes): file:line strings for pointers whose target does not exist."""
    files = [ROOT / "AGENTS.md"] + sorted((ROOT / "agents").glob("*.md")) + sorted((ROOT / ".claude/skills").glob("*/SKILL.md"))
    missing, skipped = [], 0
    known = tracked_files(ROOT) + (tracked_files(RESEARCH_TREE) if RESEARCH_TREE.is_dir() else [])

    def suffix_known(p):
        """True if p is the tail of a known path (a bare name, or a path relative to a directory named nearby)."""
        q = p.rstrip("/")
        return any(k == q or k.endswith("/" + q) or k.startswith(q + "/") or ("/" + q + "/") in k for k in known)

    for f in files:
        rel = f.relative_to(ROOT)
        in_code = False
        for ln, line in enumerate(f.read_text().splitlines(), 1):
            if line.lstrip().startswith("```"):
                in_code = not in_code
                continue
            if in_code:
                continue
            texts = [(m.group(1), m.group(2)) for m in BRANCH_PTR.finditer(line)] + \
                [(t, None) for t in re.findall(r"\]\(([^)\s]+)\)", line)]
            for t, branch in texts:
                p = pointer_candidate(t)
                if p is None:
                    continue
                if branch:
                    # `path` (on `branch`): the file lives on that branch only (AGENTS.md 0.5 item 4).
                    if not branch_has(branch, p):
                        missing.append(f"{rel}:{ln}: pointer target does not exist on {branch}: {t}")
                    continue
                head, _, tail = p.partition("/")
                if head in SHORTHANDS:
                    if not RESEARCH_TREE.is_dir():
                        skipped += 1
                        continue
                    ok = (RESEARCH_TREE / SHORTHANDS[head] / tail).exists()
                else:
                    ok = (ROOT / p).exists() or (f.parent / p).exists() or \
                        (RESEARCH_TREE.is_dir() and (RESEARCH_TREE / p).exists()) or suffix_known(p)
                if not ok and ignored(p):
                    continue  # a gitignored path names generated output, which need not exist
                if not ok:
                    missing.append(f"{rel}:{ln}: pointer target does not exist: {t}")
    notes = []
    if skipped:
        notes.append(f"pointer check: {skipped} research-shorthand pointer(s) skipped ({RESEARCH_TREE} not found)")
    return missing, notes


def main():
    check = "--check" in sys.argv[1:]
    text, hits = build()
    if not check:
        OUT.write_text(text)
        print(f"wrote {OUT} ({len(text)} bytes)")
        for h in hits:
            print("HIT:", h)
        return 0
    cur = OUT.read_text() if OUT.exists() else ""
    rc = 0
    if cur != text:
        sys.stdout.writelines(difflib.unified_diff(cur.splitlines(True), text.splitlines(True), "GENERAL.md", "generated"))
        print("GENERAL.md is out of date: run python3 agents/gen_general.py")
        rc = 1
    for h in hits:
        print("ERROR:", h)
        rc = 1
    missing, notes = pointer_hits()
    for h in missing:
        print("POINTER:", h)
        rc = 1
    for n in notes:
        print("NOTE:", n)
    return rc


if __name__ == "__main__":
    sys.exit(main())
