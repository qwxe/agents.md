"""Tests for the Claude Code hooks in .claude/hooks (run: .wt/testenv/bin/python -m pytest .claude/hooks -q).

Fake secrets are assembled at run time so this file never contains a string the secret scan would block.
"""
import json
import os
import subprocess
import sys
from io import StringIO
from pathlib import Path
from unittest.mock import Mock

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import guard_bash  # noqa: E402
import session_start  # noqa: E402
import notify_stop  # noqa: E402

TOKEN_PATH = "/home/asd/LLMServingSim/" + "gh_token"
HELPER_PUSH = ("git -c credential.helper= -c 'credential.helper=!f() { echo username=x-access-token; "
               "echo password=$(tr -d \"\\r\\n\" < " + TOKEN_PATH + "); }; f' push origin explore/x:explore/x")


def blocked(cmd):
    try:
        guard_bash.check_text(cmd)
    except guard_bash.Block:
        return True
    return False


BLOCK = [
    # pkill -f / killall
    "pkill -f 'python -m serving'",
    "pkill -9f serving",
    "pkill --full serving",
    "killall python3",
    "docker exec servingsim_docker pkill -f serving",
    "sudo killall astra",
    "ls; pkill -f x",
    "echo $(pkill -f x)",
    "bash -c 'pkill -f x'",
    # force push
    "git push --force origin main",
    "git push -f origin main",
    "git push --force-with-lease origin main",
    "git push --force-with-lease=main:abc origin main",
    "git push origin +main",
    "git -C /tmp/r push -uf origin b",
    # git add -A / --all / .
    "git add -A",
    "git add --all",
    "git add .",
    "git add -Af",
    "cd x && git add .",
    # stash
    "git stash",
    "git stash -u",
    "git stash push -m wip",
    "git stash pop",
    "git stash pop --index",
    "git stash drop",
    "git stash drop -q",
    # timeout around slotrun
    "timeout 600 .wt/bin/slotrun sim python -m serving",
    "timeout -k 5 600 /home/asd/LLMServingSim/.wt/bin/slotrun sim x",
    # printing a token file
    "cat " + TOKEN_PATH,
    "cat gh_token",
    "head -c 10 hf_token",
    "tail hf_token",
    "xxd ./gh_token",
    "less gh_token",
    "cat < gh_token",
    "grep ghp gh_token",
    "sed -n 1p gh_token",
    "echo token=$(cat gh_token)",
    "git remote set-url origin https://x:$(cat gh_token)@github.com/a/b.git",
    # follow-up 2, finding 1: shell keywords
    "for i in 1 2; do pkill -f x; done",
    "for i in 1 2\ndo\n  pkill -f x\ndone",
    "if true; then git push --force origin main; fi",
    "if git diff --quiet; then :; else git stash; fi",
    "while true; do killall x; done",
    "{ git push --force; }",
    "! git add -A",
    "ls | xargs -I{} pkill -f {}",
    # finding 2: combined -c, eval
    'bash -lc "pkill -f x"',
    "sh -xc 'git add -A'",
    "bash -e -c 'killall y'",
    "bash -o pipefail -c 'git stash'",
    'eval "git push --force"',
    "eval git stash",
    # finding 5
    "git stash clear",
    "git push origin HEAD:+main",
    "git push origin +HEAD:main",
    "grep --regexp=x gh_token",
    "grep -e x hf_token",
    # bypass flag
    '"$CODEX" exec --dangerously-bypass-approvals-and-sandbox "hi"',
    "timeout 600 codex exec --dangerously-bypass-approvals-and-sandbox x </dev/null",
]

ALLOW = [
    # mentions only
    "grep -n 'pkill -f' AGENTS.md",
    "grep -rn killall agents/",
    'echo "never git push --force"',
    'git commit -m "Block git add -A, git stash and pkill -f in the hook"',
    "git log --grep='force-with-lease'",
    "cat <<'EOF' > notes.md\npkill -f x\nkillall y\ngit push --force\ncat gh_token\nEOF",
    "python3 - <<EOF\nimport os\nos.system('git add -A')\nEOF\nls",
    "grep -n gh_token .gitignore",
    "grep -- --dangerously-bypass-approvals-and-sandbox agents/CODEX.md",
    "echo '--dangerously-bypass-approvals-and-sandbox is banned'",
    "ls # pkill -f x",
    # fine variants
    "pkill python3",
    "kill 1234",
    "docker exec servingsim_docker kill 4321",
    "git push origin explore/rate-wl-phase3:explore/rate-wl-phase3",
    "git push -u origin feat/x",
    "git push --follow-tags origin main",
    "git add -f outputs/x/NOTES.md",
    "git add agents/gen_general.py .claude/hooks/guard_bash.py",
    "git add -u agents/",
    "git stash list",
    "git stash show -p stash@{0}",
    "git stash pop stash@{1}",
    "git stash apply stash@{2}",
    "git stash drop stash@{0}",
    ".wt/bin/slotrun sim timeout 600 python -m serving",
    "timeout 600 \"$CODEX\" exec --ephemeral -s read-only -m x 'q' </dev/null",
    "timeout 5 ls",
    HELPER_PUSH,
    HELPER_PUSH.replace(" push ", " fetch "),
    "ls -l gh_token",
    "chmod 600 gh_token",
    "test -f gh_token && echo present",
    "git diff -- .gitignore",
    "sed -n 1,20p AGENTS.md",
    # follow-up 2, false-positive guards
    "for f in a b; do echo pkill -f $f; done",
    "if [ -f gh_token ]; then echo present; fi",
    "{ ls; git status; }",
    "bash -lc 'ls -la'",
    "bash script.sh -c",
    "eval \"echo git push --force\"",
    "grep -A 3 gh_token AGENTS.md",
    "grep -B2 -m 1 gh_token agents/OPERATIONS.md",
    "grep -C 2 hf_token README.md",
    "grep -n --include=*.md gh_token -r .",
    "grep --max-count 2 gh_token AGENTS.md",
    "grep -e gh_token -e hf_token AGENTS.md",
    "rg -g '*.md' gh_token .",
    "rg -t md gh_token",
    "rg --glob '*.md' -n hf_token agents/",
    "git stash --help",
    "git stash -h",
    "git add -- -A",
    "git push origin feat/c++",
    "git push origin main:main",
]


@pytest.mark.parametrize("cmd", BLOCK)
def test_blocks(cmd):
    assert blocked(cmd), cmd


@pytest.mark.parametrize("cmd", ALLOW)
def test_allows(cmd):
    assert not blocked(cmd), cmd


def run_hook(script, payload, env=None):
    return subprocess.run([sys.executable, str(HERE / script)], input=json.dumps(payload), capture_output=True,
                          text=True, timeout=30, env=env)


@pytest.mark.parametrize("cmd", [
    "unlink .wt/../outside-link",
    "unlink /home/asd/LLMServingSim/.wt/../outside-link",
    "git worktree remove .wt/../outside-tree",
    "git worktree remove /home/asd/LLMServingSim/.wt/../outside-tree",
    "git worktree remove --force -- .wt/p2v/../../outside-tree",
    "unlink -- .wt/p2v/../x",
    "unlink .wt/.",
    "git worktree remove .wt/",
    "cd x && unlink .wt/../outside-link",
    "cd x && git worktree remove .wt/../outside-tree",
    "bash -lc 'unlink .wt/../outside-link'",
    "env X=1 git -C /tmp worktree remove --force .wt/../outside-tree",
])
def test_cleanup_boundary_blocks(cmd):
    # Only send command text to the hook; never execute cleanup commands.
    r = run_hook("guard_bash.py", {"tool_name": "Bash", "tool_input": {"command": cmd}})
    assert r.returncode == 2
    assert r.stderr.startswith("BLOCKED by .claude/hooks/guard_bash.py (I.7:")
    assert len(r.stderr.strip().splitlines()) == 1


@pytest.mark.parametrize("cmd", [
    "unlink .wt/p2v/x",
    "unlink /home/asd/LLMServingSim/.wt/p2v/x",
    "git worktree remove .wt/p2v/x",
    "git worktree remove --force -- /home/asd/LLMServingSim/.wt/p2v/x",
    "cd x && unlink .wt/p2v/x",
    "bash -lc 'git worktree remove .wt/p2v/x'",
    "unlink ../outside-link",
    "unlink /tmp/outside-link",
    "git worktree remove --force ../outside-tree",
    "git worktree remove /tmp/outside-tree",
    "unlink .wt-other/../outside-link",
    "git worktree prune",
    "echo 'unlink .wt/../outside-link'",
])
def test_cleanup_boundary_allows(cmd):
    r = run_hook("guard_bash.py", {"tool_name": "Bash", "tool_input": {"command": cmd}})
    assert r.returncode == 0 and r.stderr == ""


def test_cleanup_boundary_does_not_follow_operand_symlink(tmp_path, monkeypatch):
    root = tmp_path / "repo"
    wt = root / ".wt"
    wt.mkdir(parents=True)
    outside = tmp_path / "outside"
    outside.touch()
    (wt / "link").symlink_to(outside)
    monkeypatch.setattr(guard_bash, "REPO_ROOT", str(root))
    monkeypatch.setattr(guard_bash, "WORKTREE_ROOT", str(wt))
    guard_bash.check_text("unlink .wt/link")
    guard_bash.check_text("unlink " + str(wt / "link"))
    assert outside.exists() and (wt / "link").is_symlink()


def test_hook_protocol_block_and_allow(tmp_path):
    r = run_hook("guard_bash.py", {"tool_name": "Bash", "tool_input": {"command": "killall x"}, "cwd": str(tmp_path)})
    assert r.returncode == 2 and "0.3 rule 5" in r.stderr and len(r.stderr.strip().splitlines()) == 1
    r = run_hook("guard_bash.py", {"tool_name": "Bash", "tool_input": {"command": "ls"}, "cwd": str(tmp_path)})
    assert r.returncode == 0 and r.stderr == ""


@pytest.mark.parametrize("args,whole", [
    (["-m", "x"], False), (["-sm", "x"], False), (["-mmsg-with-a"], False), (["-m", "fix a"], False),
    (["-am", "x"], True), (["-a", "-m", "x"], True), (["--all", "-m", "x"], True), (["-m", "x", "f.py"], True),
    (["-m", "x", "--", "f.py"], True), (["-uno", "-m", "x"], False), (["-F", "msg.txt"], False),
    (["--message", "x"], False), (["--message=x"], False), (["-C", "HEAD"], False), (["-i", "-m", "x", "f"], True),
    (["--amend", "--no-edit"], False), (["-S", "-m", "x"], False),
])
def test_commit_scope(args, whole):
    assert guard_bash.commit_scope(args) is whole


def test_hook_unparseable_command_allows(tmp_path):
    r = run_hook("guard_bash.py", {"tool_name": "Bash", "tool_input": {"command": "echo 'unterminated; killall"},
                                   "cwd": str(tmp_path)})
    assert r.returncode == 0


def test_hook_bad_json_allows():
    r = subprocess.run([sys.executable, str(HERE / "guard_bash.py")], input="not json", capture_output=True,
                       text=True, timeout=30)
    assert r.returncode == 0


# --- secret scan ---------------------------------------------------------------------------------------------

FAKE = {
    "ghp": "gh" + "p_" + "A1b2C3d4" * 5,
    "pat": "github" + "_pat_" + "11ABCDEFG" * 4,
    "hf": "h" + "f_" + "AbCdEfGhIjKlMnOpQrStUv",
    "sk": "s" + "k-" + "proj1234567890abcdefghij",
    "aws": "AK" + "IA" + "ABCDEFGHIJKLMNOP",
    "key": "-----BEGIN " + "RSA PRIVATE" + " KEY-----",
}


@pytest.fixture
def repo(tmp_path):
    def git(*a):
        subprocess.run(["git", "-C", str(tmp_path)] + list(a), check=True, capture_output=True)
    git("init", "-q")
    git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "init")
    (tmp_path / "ok.txt").write_text("hello\n")
    git("add", "ok.txt")
    return tmp_path, git


def commit_hook(cwd, cmd="git commit -m x"):
    return run_hook("guard_bash.py", {"tool_name": "Bash", "tool_input": {"command": cmd}, "cwd": str(cwd)})


@pytest.mark.parametrize("kind", sorted(FAKE))
def test_secret_blocks_without_echo(repo, kind):
    d, git = repo
    (d / "a.py").write_text("x = 1\ny = '" + FAKE[kind] + "'\n")
    git("add", "a.py")
    r = commit_hook(d)
    assert r.returncode == 2 and "a.py:2" in r.stderr
    assert FAKE[kind] not in r.stderr and FAKE[kind] not in r.stdout


def test_token_file_staged_blocks(repo):
    d, git = repo
    (d / "gh_token").write_text("x\n")
    git("add", "gh_token")
    r = commit_hook(d)
    assert r.returncode == 2 and "gh_token" in r.stderr


def test_clean_commit_allowed_and_mentions_ok(repo):
    d, git = repo
    (d / "doc.md").write_text("Patterns: ghp_, hf_, sk-, AKIA; never cat gh_token.\n")
    git("add", "doc.md")
    assert commit_hook(d).returncode == 0


def test_secret_follows_cd_and_dash_C(repo, tmp_path_factory):
    d, git = repo
    (d / "a.txt").write_text(FAKE["ghp"] + "\n")
    git("add", "a.txt")
    elsewhere = tmp_path_factory.mktemp("elsewhere")
    assert commit_hook(elsewhere, f"cd {d} && git commit -m x").returncode == 2
    assert commit_hook(elsewhere, f"git -C {d} commit -m x").returncode == 2


def test_commit_all_scans_unstaged_tracked(repo):
    d, git = repo
    git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "ok")
    (d / "ok.txt").write_text("hello\n" + FAKE["hf"] + "\n")
    assert commit_hook(d).returncode == 0  # nothing staged
    assert commit_hook(d, "git commit -sm x").returncode == 0  # bundled -s -m: index only, x is the message
    assert commit_hook(d, "git commit -am x").returncode == 2


# --- SessionStart -------------------------------------------------------------------------------------------


def test_session_start(tmp_path):
    led = tmp_path / "notes" / "ledger"
    led.mkdir(parents=True)
    (led / "a.md").write_text("# L\n\n| task id | owner | state |\n|---|---|---|\n| T1 | x | done |\n"
                              "| T2 | y | running |\n| T3 | z | queued |\n")
    (led / "b.md").write_text("no table here\n")
    env = dict(os.environ, CLAUDE_PROJECT_DIR=str(tmp_path))
    r = run_hook("session_start.py", {"hook_event_name": "SessionStart", "source": "startup"}, env=env)
    lines = r.stdout.strip().splitlines()
    assert r.returncode == 0 and len(lines) <= 10
    assert lines[0] == "Progress ledger notes/ledger/a.md: 2 row(s) not done"
    assert "notes/ledger/b.md: no state column" in lines[1]
    assert "AGENTS.md 0.4" in lines[-1]
    assert "T2" not in r.stdout


def test_session_start_no_ledgers(tmp_path):
    env = dict(os.environ, CLAUDE_PROJECT_DIR=str(tmp_path))
    r = run_hook("session_start.py", {}, env=env)
    assert r.returncode == 0 and r.stdout.strip().splitlines() == [
        "Research ledger and handoff: see AGENTS.md 0.4 (where the current state lives)."]


KNOWLEDGE_CATALOG = (
    "# Knowledge catalog\n\n## pitfalls\n\n| id | title | status | updated | read_when |\n|---|---|---|---|---|\n"
    "| pitfalls/a | A | verified | 2026-10-14 | x |\n\n"
    "## Promotion candidates\n\n| id | type | logic | tasks | promote |\n|---|---|---|---|---|\n"
    "| pitfalls/a | t | l | 3 | candidate |\n| pitfalls/b | t | l | 4 | candidate |\n\n"
    "## Stale\n\n| id | title | updated |\n|---|---|---|\n| simulator/z | Z | 2026-01-01 |\n")


def test_session_start_promotion_candidates(tmp_path):
    (tmp_path / "knowledge").mkdir()
    (tmp_path / "knowledge" / "KNOWLEDGE.md").write_text(KNOWLEDGE_CATALOG)
    env = dict(os.environ, CLAUDE_PROJECT_DIR=str(tmp_path))
    lines = run_hook("session_start.py", {}, env=env).stdout.strip().splitlines()
    assert lines[0] == ("Knowledge base knowledge/KNOWLEDGE.md: 2 promotion candidate(s) "
                        "(the master proposes them to the user, AGENTS.md I.21)")
    assert "AGENTS.md 0.4" in lines[-1] and len(lines) == 2


def test_session_start_no_candidates_section(tmp_path):
    (tmp_path / "knowledge").mkdir()
    (tmp_path / "knowledge" / "KNOWLEDGE.md").write_text("# Knowledge catalog\n\n## Promotion candidates\n\nnone\n")
    env = dict(os.environ, CLAUDE_PROJECT_DIR=str(tmp_path))
    lines = run_hook("session_start.py", {}, env=env).stdout.strip().splitlines()
    assert lines[0].startswith("Knowledge base knowledge/KNOWLEDGE.md: 0 promotion candidate(s)")


def test_session_start_at_most_10_lines(tmp_path):
    led = tmp_path / "notes" / "ledger"
    led.mkdir(parents=True)
    for i in range(12):
        (led / f"l{i:02d}.md").write_text("| state |\n|---|\n| running |\n")
    (tmp_path / "knowledge").mkdir()
    (tmp_path / "knowledge" / "KNOWLEDGE.md").write_text(KNOWLEDGE_CATALOG)
    env = dict(os.environ, CLAUDE_PROJECT_DIR=str(tmp_path))
    lines = run_hook("session_start.py", {}, env=env).stdout.strip().splitlines()
    assert len(lines) <= 10
    assert any("more in notes/ledger/" in x for x in lines)
    assert any("2 promotion candidate(s)" in x for x in lines)
    assert "AGENTS.md 0.4" in lines[-1]


# --- Stop: silent input/failures, detached launch, re-entry, event registration ------------------------------


@pytest.fixture
def notification(monkeypatch):
    exists = Mock(return_value=True)
    popen = Mock()
    monkeypatch.setattr(notify_stop.os.path, "exists", exists)
    monkeypatch.setattr(notify_stop.subprocess, "Popen", popen)

    def invoke(payload):
        monkeypatch.setattr(sys, "stdin", StringIO(payload))
        notify_stop.main()

    return invoke, exists, popen


@pytest.mark.parametrize("payload", [
    "not json", "null", "[]", '"text"', "7", "true",
    '{"cwd": 7}', '{"cwd": []}', '{"cwd": {}}', '{"cwd": false}',
    '{"cwd": "bad\\u0000path"}',
])
def test_notify_malformed_input_is_silent(notification, capsys, payload):
    invoke, _, popen = notification
    invoke(payload)
    popen.assert_not_called()
    assert capsys.readouterr() == ("", "")


def test_notify_missing_powershell(notification, capsys):
    invoke, exists, popen = notification
    exists.return_value = False
    invoke("{}")
    exists.assert_called_once_with(notify_stop.PS)
    popen.assert_not_called()
    assert capsys.readouterr() == ("", "")


def test_notify_popen_failure(notification, capsys):
    invoke, _, popen = notification
    popen.side_effect = OSError("unavailable")
    invoke("{}")
    popen.assert_called_once()
    assert capsys.readouterr() == ("", "")


def test_notify_detached_without_wait(notification, capsys):
    invoke, _, popen = notification
    invoke(json.dumps({"cwd": "/tmp/user's-project"}))
    popen.assert_called_once_with(
        [notify_stop.PS, "-NoProfile", "-WindowStyle", "Hidden", "-Command",
         notify_stop.SCRIPT.format(msg="users-project: answer finished")],
        stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    assert popen.return_value.mock_calls == []  # No wait, communicate, or context-manager exit.
    assert capsys.readouterr() == ("", "")


def test_notify_reentry_does_not_spawn(notification, capsys):
    invoke, exists, popen = notification
    invoke('{"stop_hook_active": true}')
    exists.assert_not_called()
    popen.assert_not_called()
    assert capsys.readouterr() == ("", "")


def test_notify_registered_only_for_stop():
    hooks = json.loads((HERE.parent / "settings.json").read_text())["hooks"]
    registrations = [event for event, groups in hooks.items() for group in groups
                     for hook in group["hooks"] if "notify_stop.py" in hook.get("command", "")]
    assert registrations == ["Stop"]


# --- pointer check in agents/gen_general.py -----------------------------------------------------------------


@pytest.fixture
def gen(tmp_path, monkeypatch):
    """gen_general with ROOT at a temp repo that has branch `feat/x` holding tools/run.sh."""
    sys.path.insert(0, str(HERE.parents[1] / "agents"))
    import gen_general as g

    def git(*a):
        subprocess.run(["git", "-C", str(tmp_path), "-c", "user.name=t", "-c", "user.email=t@t"] + list(a),
                       check=True, capture_output=True)
    git("init", "-q", "-b", "main")
    (tmp_path / "doc.md").write_text("x\n")
    git("add", "doc.md")
    git("commit", "-q", "-m", "init")
    git("checkout", "-q", "-b", "feat/x")
    (tmp_path / "tools").mkdir()
    (tmp_path / "tools" / "run.sh").write_text("true\n")
    git("add", "tools/run.sh")
    git("commit", "-q", "-m", "b")
    git("checkout", "-q", "main")
    (tmp_path / "agents").mkdir()
    monkeypatch.setattr(g, "ROOT", tmp_path)
    monkeypatch.setattr(g, "RESEARCH_TREE", tmp_path / "no-such-tree")
    return g, tmp_path


def test_pointer_check(gen):
    g, root = gen
    (root / "AGENTS.md").write_text(
        "See `doc.md` and [d](doc.md).\n"                     # exists here
        "Missing `gone/file.md` here.\n"                       # line 2: missing
        "Suite `tools/run.sh` (on `feat/x`).\n"                # on the branch: ok
        "Bad `tools/nope.sh` (on `feat/x`).\n"                 # line 4: not on the branch
        "Unqualified `tools/run.sh`.\n"                        # line 5: not in this tree
        "Placeholder `R/tasks/<id>.md`, branch `feat/pe-srpt`, glob `a/*.md`.\n")
    missing, notes = g.pointer_hits()
    lines = sorted(int(m.split(":")[1]) for m in missing)
    assert lines == [2, 4, 5], missing
    assert any("on feat/x" in m for m in missing)
