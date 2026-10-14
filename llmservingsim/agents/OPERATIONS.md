# agents/OPERATIONS.md — runs, git and processes

Sections: I.5 runs, slots and monitoring · I.6 git · I.7 processes and cleanup · I.18 monitoring running work ·
I.20 hooks ·
I.16 the general git/process rules that I.6 and I.7 specialise.

Scope: every Claude agent and Codex task worker that runs, builds, commits or kills anything in this repository. Repository-specific (machine, container, slots); I.16 is copied into `GENERAL.md` (AGENTS.md 0.2).

## I.5 Runs, slots and monitoring (2026-10-14)

**Slots.** Several agents share one machine (28 vCPUs, about 8 fast cores, about 11-12 GB RAM, no GPU).
- Every simulator run goes through `/home/asd/LLMServingSim/.wt/bin/slotrun <kind> <command...>` (same path inside
  the container), one run per slot job; never loop several runs inside one job.

  | kind | slots | use for |
  |---|---|---|
  | `sim` | 8: the machine budget all agents share (`.wt/perf-tools/slots/sim.n`); 14 is only slotrun's hard cap | one simulator run, or one run of the default test suite |
  | `replay` | 3 | one ASTRA-Sim replay |
  | `build` | 1 | one C++ build, `-j4` or less |
  | `excl` | runs alone | anything bigger than one sim run |

- Never run work on vCPUs outside your slot (it halves 8 parallel runs). A Codex research call is the only exception (I.4).
- `slotrun` admits a `sim` job only when MemAvailable leaves 800 MB of peak plus 500 MB. A slow queue with free
  slots usually means low memory. Long FI/TraceLab runs above about 1.2 GB: keep about 4 in flight.
- `validate-par` and the K=8 throughput script queue their own `slotrun` jobs: call them directly. Never run two
  `validate-par` at once, and never with `--update`.
- Wait for long jobs with Bash `run_in_background` (or an until-loop with long sleeps), never tight polling;
  check their health every ~3 minutes as I.18 says, with the table under *Monitoring* below.

**Within an approved experiment, keep the slots full.** Submit every run whose inputs exist at once, each its own
`slotrun sim` job; submit a dependent run (one needing another's T_res or params) the moment its dependency
finishes; a pending question does not justify draining the queue. Any run outside the approved experiment: ask
first (AGENTS.md 0.3 rule 8). A subagent asks through an escalation; the runs its brief lists count as
approved.

**Validation timing.** Routine checks while working: the default test suite (`tests/run.sh` (on `feat/tests`), under 10 s, host
venv `.wt/testenv`, through one `slotrun sim` slot) and the quick golden subset
(`SIM_TREE=<tree> KV_DIV=1 .wt/bin/validate-par --quick`, list in `serving/validate-quick.txt` (on `feat/tests`)). The full
`validate-par` (59 + 8) and the reference checks (II.4) run once at the end of a line of work, by the verifier
(I.14). On main-line work, run `./serving/validate.sh` after every commit that touches `serving/`
(`agents/SIM-REFERENCE.md`, Testing). Never pip install into the container; test tools live in `.wt/testenv`.

**Monitoring.** The agent that launched a run watches it and may kill and rerun its own runs. Only the master
kills or reruns another agent's runs, and only on the user's order; it then tells that agent.

| what | how | healthy |
|---|---|---|
| harness progress | heartbeat lines `[<t>s] ...` in `<rid>.log`; the run's line in the runs jsonl | sim clock advancing |
| live processes | `docker exec servingsim_docker ps -eo pid,ppid,etimes,pcpu,stat,rss,args \| grep -- '-m serving'` | frontend `R` near 100% CPU; ASTRA-Sim a few % |
| memory | `free -m` | MemAvailable well above 1 GB, swap not growing |
| validate-par | `ls /tmp/vpar_*/*.rc \| wc -l`; `grep -h ' PASS \| FAIL \| NEW ' /tmp/vpar_*/*.s` | every finished scenario PASS |

- **Startup hang:** frontend at 0% CPU for more than 30 s after "Starting simulation": `.wt/bin/hangdump <rid>
  [log]`, kill by PID, rerun once. Venv-guard suspects with `fe_state=R` are usually slow starts.
- **Runaway memory** (RSS climbing more than about 1 GB/min above siblings): hangdump first, then kill by PID.
- **MemAvailable below about 1 GB or swap growing:** stop launching and tell the user. The harness watchdog kills
  a run below 1 GB.

## I.6 Git (2026-10-14)

- The fork is `origin` = `https://github.com/qwxe/LLMServingSim.git`. No git identity is set: commit with
  `git -c user.name=qwxe -c user.email=psh010103@gmail.com commit ...`, and end messages with the
  `Co-Authored-By` line the session gives.
- Commit only on your own branch, one method or item per commit. Never bump gitlinks.
- Code branches stay local unless the user asks. Experiment results and handoff notes on
  `explore/rate-wl-phase3` are pushed as soon as they are written (user, 2026-10-12/13), with the credential
  helper (never print the token):
  ```
  git -c credential.helper= -c 'credential.helper=!f() { echo username=x-access-token; echo password=$(tr -d "\r\n" < /home/asd/LLMServingSim/gh_token); }; f' push origin <branch>:<branch>
  ```
  The same helper works for `fetch`. The submodule fetch fails (astra-sim pin not on the remote); the main repo
  fetch still succeeds.
- Stage only your own files; others' uncommitted files share the worktrees. Notes under `outputs/` are
  gitignored: add them with `git add -f`.
- The stash is shared by all worktrees and sessions: never bare `git stash`/`pop`; prefer a WIP commit.
- Branch and worktree layout for research code: II.3 and II.4.

## I.7 Processes and cleanup (2026-10-14)

- Kill by PID only (AGENTS.md 0.3 rule 5). `tl2_run.kill(rid)` kills a harness run.
- A process reparented to PID 1 runs outside every slot: kill it by PID.
- Before you finish, remove your measurement tree (unless the brief keeps it), fork server, `/tmp` scratch and
  orphan processes.
- Files written by the container are root-owned: delete them with `docker exec servingsim_docker rm -rf ...`.
- `validate.sh`/`validate-par` rewrite `bench/examples/*/outputs/sim.log` with only run-id and wall-time changes:
  revert them with `git checkout`.

## I.18 Monitoring running work (2026-10-14)
<!-- general -->

User, 2026-10-14: runs that take compute or sit on the critical path of the goal are monitored periodically.

- **What.** Every job that holds compute (a job slot, a build, a long test, anything at high CPU or memory) and
  every job on the critical path of the current goal, from launch to exit.
- **Who.** The agent that launched it. A Codex worker returns before a long job ends, so its caller runs the
  health loop below in the background and acts on what it reports (calling a Codex Luna worker for checks it
  needs). The master does not poll: the loop prints only on an anomaly or at exit, and the master keeps the
  progress ledger current.
- **Mechanism.** A completion notification alone does not catch a hang. Run both: the job (or its wait) in the
  background so its exit wakes the agent, and a health loop that checks every ~180 s and prints only on an
  anomaly or at the end.
- **How often.** A health check about every **3 minutes**, from a background wait with a ~180 s sleep or a
  scheduled wake-up. Never a tight loop; wait on a PID or an output file, not on `pgrep -f` (I.16).
- **What a check looks at.** Progress (heartbeat, simulated clock or output still advancing), CPU state (running,
  or stuck near 0%), memory (process growth, machine free memory, swap), errors in the log, and the expected
  finish. The run rules give this repository's commands and healthy values.
- **Acting** (on your own jobs only; another agent's job is reported to the master). A stall or hang:
  capture diagnostics, kill by PID, rerun once. Runaway memory or a machine short of
  memory: stop launching, kill the offender, tell the spawner. Report an anomaly to the spawner at once, not at
  the end; record it and the action in the task trail. Healthy checks are not logged.

## I.20 Hooks (2026-10-14)

Mechanical enforcement of the never-break rules (user, 2026-10-14). Change a hook only with its tests
(`.wt/testenv/bin/python -m pytest .claude/hooks -q`) and update this section in the same commit.

`.claude/hooks/guard_bash.py` runs before every Bash tool call in this repository (`.claude/settings.json`,
`PreToolUse`, matcher `Bash`). A refused command exits 2 with one line `BLOCKED by .claude/hooks/guard_bash.py
(<rule id>: <reason>)`. Any parse error or git failure allows the command.

**Where it looks.** Inside `;`, `&&`, `||`, `|`, newlines, `$(...)` (quoted or not) and backticks, `bash/sh -c` (also
`-lc`, `-ec`), `eval`, shell keywords (`if/then/else/do/while/{/!`), and wrappers (`sudo`, `env`, `nohup`, `time`,
`xargs`, `timeout`, `docker exec`).

**Where it does not look.** Heredoc bodies, the text arguments of echo/printf, grep patterns, commit messages,
and comments. It is a safety net against mistakes, not against deliberate evasion.

| rule | blocks | allows on purpose | do this instead |
|---|---|---|---|
| 0.3 rule 5 | `pkill -f`, `pkill -<flags with f>`, `pkill --full`, `killall` | `pkill <name>`, `kill <pid>`, `pgrep -f` | kill by PID; in the container `docker exec servingsim_docker kill <pid>` |
| 0.3 rule 7 (force-push) | `git push` with `--force`, `-f` (or a cluster with f), `--force-with-lease[=..]`, `--force-if-includes`, a refspec starting with `+` or containing `:+` | normal pushes, `-u`, `--follow-tags` | push a new branch, or ask the user |
| I.16 (staging) | `git add -A`, `--all`, a cluster with `A`, `.`, `./` (also after `--`) | `git add <paths>`, `-f <path>`, `-u <path>`, `git add -- -A` (a file named -A), `--help` | name your files |
| I.16 (stash) | bare `git stash` (also with options only), `git stash push`, `save`, `clear`, `pop`/`drop` without a ref | `git stash list`, `show`, `apply`, `pop`/`drop stash@{n}`, `--help`/`-h` | a WIP commit on your branch |
| 0.3 rule 4 | `timeout ... slotrun ...` | `slotrun sim timeout N cmd`, `timeout N <other cmd>` | let slotrun manage the job; kill by PID if it hangs |
| 0.3 rule 7 (token) | a printer (`cat tac nl less more head tail xxd od hexdump strings base64 sort cut grep rg sed awk ...`) with `gh_token`/`hf_token` as a file operand or as `< file` | the credential helper `$(tr -d "\r\n" < gh_token)`; `ls`, `test -f`, `wc -c <`, `chmod` on the file; searching for the word: `grep [-A N] [-m N] gh_token <files>`, `rg -g '*.md' gh_token` | use the credential helper (I.6); if the hook misreads a search, give the pattern with `-e gh_token` |
| I.4 | `--dangerously-bypass-approvals-and-sandbox` as an argument of any command except text commands (echo, printf, grep, sed, awk, cat, git) | mentioning the flag in text | `codex exec -s read-only`; a task worker uses `-s workspace-write` or `-s danger-full-access` (I.4) |
| 0.3 rule 7 (commit) | `git commit` whose change adds a GitHub (`gh?_`, `github_pat_`), Hugging Face (`hf_`), `sk-` or AWS `AKIA` key, or a private-key header, or adds a file named `gh_token`/`hf_token`. The index is checked; with `-a`, `-i`, `-o` or pathspecs, `git diff HEAD` is checked instead. The block message names `file:line` and the kind, never the value. | mentions such as `ghp_` without a token-length tail; `--dry-run`; `-sm msg` and `-mmsg` checked as index-only | remove the secret, or unstage the file |

**Known limits** (accepted for precision; the user, 2026-10-14):
- These token-file routes are not followed:
  - globs (`cat gh_to*`, `cat *` in the repo root);
  - `$(< gh_token)`;
  - command substitutions that produce the name (`cat $(echo gh_token)`);
  - interpreter code that opens the file (`python3 -c "open('gh_token')"`, `perl -e`, `node -e`, `ruby -e`).
- Variable indirection (`g=git; $g stash`, `P=pkill; $P -f`, `f=gh_token; cat $f`) is not followed.
- Unquoted `$(...)` is split by the tokenizer and checked as separate commands.
- Heredoc bodies are not checked (`python3 - <<EOF ... EOF`).
- `$(...)` inside single quotes is still checked, because the quoting is lost.
- Aliases and shell functions are not followed.
- The commit message itself is not scanned for secrets (finding 6, out of scope).
- If the hook times out (60 s), the command is not blocked.

`.claude/hooks/session_start.py` (SessionStart) prints at most 10 lines: each `notes/ledger/*.md` with its count
of rows not `done`, and a pointer to AGENTS.md 0.4. Tests: `.wt/testenv/bin/python -m pytest .claude/hooks -q`.

## I.16 Git, processes and safety: the general rules (2026-10-14)
<!-- general -->

- Never print a token file and never put a token in a remote URL; push through a credential helper that reads
  the file. Never force-push.
- Commit only on your own branch, one item per commit; stage only your own files (others' uncommitted files share
  the worktrees). Never `git add -A` in a shared tree.
- The stash is shared by all worktrees and sessions: never bare `git stash`/`pop`; prefer a WIP commit.
- Code branches stay local unless the user asks; notes and results the user wants visible elsewhere are pushed
  as soon as they are written.
- Never `pkill -f` or `killall`; kill by PID. Clean up your own scratch, trees and orphan processes when done.
- To wait for a process, wait on its PID (`while kill -0 <pid>`) or on its output file, never on `pgrep -f
  <pattern>`: the waiting shell's own command line contains the pattern, so the loop matches itself and never ends
  (verifier, 2026-10-14).
- Ask the user before starting expensive jobs they did not request. Within an approved experiment, keep the
  available slots full.
- If a permission check blocks an action, do not work around it; report it to the user.

## Operations pitfalls (2026-10-14)

- Following an old rule number ("0.2 rule 6"): the never-break rules are AGENTS.md 0.3.
- Reading the 14-slot slotrun cap as the budget: the shared budget is 8 `sim` slots.
- Relying on the completion notification to notice a hang (I.18).
- Starting `validate-par` while another agent's is running.
