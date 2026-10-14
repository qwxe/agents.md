#!/usr/bin/env python3
"""Sync the rule files to https://github.com/qwxe/agents.md (AGENTS.md 0.2).

Usage: python3 agents/publish_agentsmd.py [--check | --dry-run]

Layout of the target repository (branch main):
  root:            README.md, GENERAL.md, USER.md, skills/<name>/SKILL.md (every skill gen_general.py treats as general)
  llmservingsim/:  AGENTS.md, agents/*.md|*.py, .claude/agents/*.md, .claude/hooks/*, .claude/settings.json

Default: refuse if a synced source file has uncommitted changes, run `gen_general.py --check`, clone or
fast-forward .wt/agentsmd, mirror the files (deleting stale files only inside the managed paths), commit as qwxe
with the source commit id and push main through a credential helper (the token is never printed or put in a URL).
--check: report drift against the remote, exit 1 if any, no push. --dry-run: show what would change, no commit.
Both --check and --dry-run are allowed on a dirty source tree.
"""
import importlib.util
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / ".wt/agentsmd"
REMOTE = "https://github.com/qwxe/agents.md"
TOKEN = ROOT / "gh_token"
COAUTHOR = "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
SHA_LINE = re.compile(r"^Source commit of the last sync: .*$", re.M)

README = """# agents.md

Rules for coding agents (Claude Code, Codex and others), kept in two parts.

## Part 1: general files (repository root)

These are repository-independent and reusable as they are:

- `GENERAL.md`: roles and spawning, delegation, decision rights and escalation, briefs and reports, tests and
  review, handover between sessions, safe git and process habits, and the general skills.
- `USER.md`: the contract between the user and the agents (the user's part and the options).
- `skills/<name>/SKILL.md`: the general skills (procedures an agent loads when a task matches).

## Part 2: `llmservingsim/`

The rule set of one concrete repository (LLMServingSim), as a worked example of how the general files are
adopted: its `AGENTS.md` entry file, the role files under `agents/`, the agent definitions and hooks under
`.claude/`, and the generator and publishing scripts.

## Adopting the general files in another repository

1. Copy `GENERAL.md` and `USER.md` into the repository, and the skills into `.claude/skills/`.
2. Write the repository's own `AGENTS.md`, with a term map in the style of section 0.4 of
   `llmservingsim/AGENTS.md` that maps the general terms (handoff file, decisions list, task trail, ...) to the
   repository's own files.
3. Mark the sections that are not tied to the repository with `<!-- general -->` on the line after their heading,
   and write them in general terms.
4. Run a generator like `llmservingsim/agents/gen_general.py` to rebuild `GENERAL.md` from the marked sections,
   and a publisher like `llmservingsim/agents/publish_agentsmd.py` to sync this layout.

## Provenance

The root files are generated from LLMServingSim and are edited there, never in this repository: change the
marked section in the source repository, regenerate, and run `python3 agents/publish_agentsmd.py`.

Source commit of the last sync: {sha}
"""


def run(args, cwd=ROOT, check=True):
    r = subprocess.run(args, cwd=cwd, capture_output=True, text=True)
    if check and r.returncode:
        sys.exit(f"command failed ({r.returncode}): {' '.join(str(a) for a in args[:6])}\n{r.stdout}{r.stderr}")
    return r


def cred_args():
    if not TOKEN.exists():
        return []  # no token file: use git's own credential setup
    helper = '!f() { echo username=x-access-token; echo password=$(tr -d "\\r\\n" < %s); }; f' % TOKEN
    return ["-c", "credential.helper=", "-c", f"credential.helper={helper}"]


def general_skills():
    spec = importlib.util.spec_from_file_location("gen_general", ROOT / "agents/gen_general.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return sorted(h[len("Skill: "):] for _, _, _, h, _ in mod.read_skills())


def source_files():
    """Map: path in the target -> source path."""
    m = {}
    for f in ("GENERAL.md", "USER.md"):
        m[f] = ROOT / f
    for name in general_skills():
        m[f"skills/{name}/SKILL.md"] = ROOT / ".claude/skills" / name / "SKILL.md"
    m["llmservingsim/AGENTS.md"] = ROOT / "AGENTS.md"
    for pat in ("agents/*.md", "agents/*.py", ".claude/agents/*.md", ".claude/hooks/*"):
        for p in sorted(ROOT.glob(pat)):
            if p.is_file() and p.suffix != ".pyc":
                m["llmservingsim/" + str(p.relative_to(ROOT))] = p
    m["llmservingsim/.claude/settings.json"] = ROOT / ".claude/settings.json"
    return m


SOURCE_PATHS = ["GENERAL.md", "USER.md", "AGENTS.md", "agents", ".claude/agents", ".claude/hooks",
                ".claude/settings.json", ".claude/skills"]


def dirty():
    """Uncommitted changes (modified, deleted, renamed, untracked) on any synced source path."""
    r = run(["git", "status", "--porcelain", "--"] + SOURCE_PATHS, check=False)
    return [l for l in r.stdout.splitlines() if l.strip() and "__pycache__" not in l]


def check_source_published():
    """The source must be on main with HEAD contained in origin/main (fetched through the credential helper)."""
    r = run(["git"] + cred_args() + ["fetch", "origin", "main"], check=False)
    if r.returncode:
        sys.exit("fetch of the source repository failed:\n" + r.stderr.replace(str(TOKEN), "<token>"))
    branch = run(["git", "branch", "--show-current"]).stdout.strip()
    if branch != "main":
        sys.exit(f"refusing: the source is on branch {branch!r}, not main")
    if run(["git", "merge-base", "--is-ancestor", "HEAD", "origin/main"], check=False).returncode:
        sys.exit("refusing: source HEAD is not contained in origin/main (push the source first)")


def managed(rel):
    return rel in ("README.md", "GENERAL.md", "USER.md") or rel.startswith(("skills/", "llmservingsim/"))


def prepare_target():
    if not (TARGET / ".git").exists():
        TARGET.parent.mkdir(parents=True, exist_ok=True)
        run(["git", "init", "-q", "-b", "main", str(TARGET)])
        run(["git", "remote", "add", "origin", REMOTE], cwd=TARGET)
    r = run(["git"] + cred_args() + ["fetch", "origin", "main"], cwd=TARGET, check=False)
    if r.returncode == 0:
        run(["git", "merge", "--ff-only", "FETCH_HEAD"], cwd=TARGET)  # fails if diverged: never forced
    elif "couldn't find remote ref" not in r.stderr:
        sys.exit("fetch failed:\n" + r.stderr.replace(str(TOKEN), "<token>"))


def current_target_files():
    out = {}
    for p in TARGET.rglob("*"):
        rel = p.relative_to(TARGET)
        if ".git" in rel.parts or not p.is_file():
            continue
        if managed(str(rel)):
            out[str(rel)] = p
    return out


def main():
    args = sys.argv[1:]
    check, dry = "--check" in args, "--dry-run" in args
    if (check and dry) or set(args) - {"--check", "--dry-run"}:
        sys.exit(__doc__)
    files = source_files()
    if not (check or dry):
        check_source_published()
        d = dirty()
        if d:
            sys.exit("refusing: synced files have uncommitted changes (they would publish unreviewed text):\n"
                     + "\n".join(d))
    r = run([sys.executable, str(ROOT / "agents/gen_general.py"), "--check"], check=False)
    if r.returncode:
        print(r.stdout[-3000:])
        if not (check or dry):
            sys.exit("gen_general.py --check failed")
        print("WARNING: gen_general.py --check failed")
    sha = run(["git", "rev-parse", "--short", "HEAD"]).stdout.strip()
    prepare_target()
    if not (check or dry):
        stray = [l for l in run(["git", "status", "--porcelain", "-uall"], cwd=TARGET).stdout.splitlines()
                 if not managed(l[3:].split(" -> ")[-1].strip('"'))]
        if stray:
            sys.exit("refusing: the target clone has changes outside the managed paths:\n" + "\n".join(stray))
    old = current_target_files()
    new_content = {rel: src.read_bytes() for rel, src in files.items()}
    readme_old = (TARGET / "README.md").read_text() if (TARGET / "README.md").exists() else ""
    m = SHA_LINE.search(readme_old)
    # The sha line alone is not a change: build the README with the old sha, and use the new sha only when
    # another managed file (or the template text) changed.
    base = README.format(sha=sha)
    if m:
        base = SHA_LINE.sub(lambda _: m.group(0), base)
    new_content["README.md"] = base.encode()

    changes = []
    for rel, data in sorted(new_content.items()):
        if rel not in old:
            changes.append(("add", rel))
        elif old[rel].read_bytes() != data:
            changes.append(("modify", rel))
    for rel in sorted(set(old) - set(new_content)):
        changes.append(("delete", rel))
    if changes:
        new_content["README.md"] = README.format(sha=sha).encode()
        if not any(rel == "README.md" for _, rel in changes) and old.get("README.md") is not None \
                and old["README.md"].read_bytes() != new_content["README.md"]:
            changes.append(("modify", "README.md"))
    for kind, rel in changes:
        print(f"{kind:7s} {rel}")
    print(f"{len(new_content)} files managed, {len(changes)} change(s); source commit {sha}")
    if check:
        print("DRIFT" if changes else "in sync")
        return 1 if changes else 0
    if dry:
        print("managed files:")
        print("\n".join(f"  {rel}" for rel in sorted(new_content)))
        return 0
    if not changes:
        print("nothing to sync")
        return 0
    for kind, rel in changes:
        p = TARGET / rel
        if kind == "delete":
            p.unlink()
        else:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(new_content[rel])
            if rel in files and files[rel].stat().st_mode & 0o111:
                p.chmod(p.stat().st_mode | 0o111)
    # Stage only the managed paths (never `add -A` on the whole clone); skip a path that neither exists nor is tracked.
    top = [t for t in ("README.md", "GENERAL.md", "USER.md", "skills", "llmservingsim")
           if (TARGET / t).exists() or run(["git", "ls-files", "--", t], cwd=TARGET).stdout.strip()]
    run(["git", "add", "-A", "--"] + top, cwd=TARGET)
    msg = f"Sync from LLMServingSim {sha}\n\n{COAUTHOR}\n"
    run(["git", "-c", "user.name=qwxe", "-c", "user.email=psh010103@gmail.com", "commit", "-q", "-m", msg], cwd=TARGET)
    r = run(["git"] + cred_args() + ["push", "origin", "main:main"], cwd=TARGET, check=False)
    if r.returncode:
        sys.exit("push failed:\n" + (r.stdout + r.stderr).replace(str(TOKEN), "<token>"))
    print("pushed", run(["git", "rev-parse", "--short", "HEAD"], cwd=TARGET).stdout.strip())
    return 0


if __name__ == "__main__":
    sys.exit(main())
