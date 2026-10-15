# agents/OPERATIONS.md — runs, git and processes

Sections: I.5 runs, slots and monitoring · I.6 git · I.7 processes and cleanup · I.18 monitoring running work ·
I.20 hooks · I.22 shared resources ·
I.16 the general git/process rules that I.6, I.7 and I.22 specialise.

Scope: every Claude agent and Codex task worker that runs, builds, commits or kills anything in this repository. Repository-specific (machine, container, slots); I.16 and I.18 are copied into `GENERAL.md` (AGENTS.md 0.2).

## I.5 Runs, slots and monitoring (2026-10-14)

**Slots.** Several agents share one machine (28 vCPUs, about 8 fast cores, about 11-12 GB RAM, no GPU). (2026-10-14)
- Every simulator run goes through `/home/asd/LLMServingSim/.wt/bin/slotrun <kind> <command...>` (same path inside
  the container), one run per slot job; never loop several runs inside one job. (2026-10-14)

  | kind | slots | use for |
  |---|---|---|
  | `sim` | 8: the machine budget all agents share (`.wt/perf-tools/slots/sim.n`); 14 is only slotrun's hard cap | one simulator run, or one run of the default test suite (2026-10-14) |
  | `replay` | 3 | one ASTRA-Sim replay (2026-10-14) |
  | `build` | 1 | one C++ build, `-j4` or less (2026-10-14) |
  | `excl` | runs alone | anything bigger than one sim run (2026-10-14) |

- Never run work on vCPUs outside your slot (it halves 8 parallel runs). A Codex research call is the only exception (I.4). (2026-10-14)
- `slotrun` admits a `sim` job only when MemAvailable leaves 800 MB of peak plus 500 MB. A slow queue with free
  slots usually means low memory. Long FI runs above about 1.2 GB: keep about 4 in flight. (2026-10-14)
- `validate-par` and the K=8 throughput script queue their own `slotrun` jobs: call them directly. Never run two
  `validate-par` at once, and never with `--update`. (2026-10-14)
- Wait for long jobs with Bash `run_in_background` (or an until-loop with long sleeps), never tight polling;
  check their health every ~3 minutes as I.18 says, with the table under *Monitoring* below. (2026-10-14)

**Within an approved experiment, keep the slots full.** Submit every run whose inputs exist at once, each its own
`slotrun sim` job; submit a dependent run (one needing another's T_res or params) the moment its dependency
finishes; a pending question does not justify draining the queue. Any run outside the approved experiment: ask
first (AGENTS.md 0.3 rule 8). A subagent asks through an escalation; the runs its brief lists count as
approved. (2026-10-14)

**Validation timing.** Routine checks while working: the default test suite (`tests/run.sh` (on `feat/tests`), under 10 s, host
venv `.wt/testenv`, through one `slotrun sim` slot) and the quick golden subset
(`SIM_TREE=<tree> KV_DIV=1 .wt/bin/validate-par --quick`, list in `serving/validate-quick.txt` (on `feat/tests`)). The full
`validate-par` (59 + 8) and the reference checks (II.4) run once at the end of a line of work, by the verifier
(I.14). On main-line work, run `./serving/validate.sh` after every commit that touches `serving/`
(`agents/SIM-REFERENCE.md`, Testing). Never pip install into the container; test tools live in `.wt/testenv`. (2026-10-14)

**Run cards** (design note `notes/design/T20261014-knowledge-runcard.md`, user 2026-10-14). Every run block (the
runs launched for one purpose) has one card, made with the run-card tool `python3 agents/runcard.py` (stdlib;
exit 0 pass, 1 check failed, 2 usage or file error; usage in its docstring). Where cards live: the run-card row
of the map in AGENTS.md 0.4. The order is the one of the `experiment-plan` skill; in this repository (2026-10-14):

1. `runcard.py new <card> --block-id <id> --by "<role> <task id>"`. (2026-10-14)
2. Fill claim, intent, label, retrodiction, predictions, `arm_active_check.how` and `positive_control.how` from
   the plan. (2026-10-14)
3. `runcard.py fingerprint <card> --tree <tree> --inputs <workload, config and profile files> --env KV_DIV
   RATE_POLICY RATE_HOLE RATE_SEG RATE_SESS_STATE ... --build <id> --config <path> --tool <name>=<version>
   --flags <the run's argv tokens>` (`--flags` last). Name every env variable that selects the arm or the
   configuration; an unset one is recorded as unset. A measurement tree under `.wt/` that is not its own git
   root also needs `--source-commit <commit it was built from>` (it is identified by a content hash; skip build
   output with `--hash-exclude <glob>`). Per arm: `runcard.py fingerprint <card> --arm <name> --env ... --inputs
   ... --flags ...`. (2026-10-14)
4. `runcard.py check <card>` passes (a confirmatory card refuses a dirty tree; a card whose retrodiction says
   existing results already answer the question is refused). (2026-10-14)
5. **Approval**: the user approves the plan together with its checked cards (AGENTS.md 0.3 rule 8). (2026-10-14)
6. Run the block through `slotrun` (above). (2026-10-14)
7. `runcard.py set <card> --runs <id>... --seeds <s>...` as the runs launch, and
   `runcard.py set <card> --control positive|arm-active <result>` once the control results are read. Nobody edits
   a card by hand. (2026-10-14)
8. `runcard.py score <card> --hit <idx>[=<observed>]... --miss <idx>[=<observed>]... --verdict "<...>"`; after a
   miss, read the raw results and rescore with `--raw-read`. (2026-10-14)
9. `runcard.py check --post --claim null|arm-lost|difference <card>` (default `null`) passes before any result is
   reported: the arm-active result is always required, the positive-control result for `null` and `arm-lost`. (2026-10-14)
10. `runcard.py compare <cardA> <cardB> --arm-vars <VAR>... --arm-flags <prefix>...` (`--arm-flags` last) exits 0
    before two blocks' numbers are put side by side; a refused comparison is not made: rerun instead. (2026-10-14)

Wording (same-seed rerun is a reproduction, not a replication; "confirmed" only with stated evidence;
confirmatory vs exploratory) is in the `experiment-plan` skill; `claim-audit` checks it. (2026-10-14)

**Monitoring.** The agent that launched a run watches it and may kill and rerun its own runs. Only the master
kills or reruns another agent's runs, and only on the user's order; it then tells that agent. (2026-10-14)

The checks, commands and healthy values for runs, processes, memory and `validate-par` are in the knowledge
entry `knowledge/anomalies/run-health.md` (I.21; read it before monitoring a run). The actions on what a check flags
stay here; each names its failure class (I.18) (2026-10-14):

- **Startup hang** (infra-transient): frontend at 0% CPU for more than 30 s after "Starting simulation":
  `.wt/bin/hangdump <rid> [log]`, kill by PID, retry once and record the retry in the task trail. A second hang
  is infra-permanent: stop and tell the spawner. Venv-guard suspects with `fe_state=R` are usually slow starts. (2026-10-14)
- **Runaway memory** (unclassified until diagnosed; RSS climbing more than about 1 GB/min above siblings): hangdump first, then kill by PID. (2026-10-14)
- **MemAvailable below about 1 GB or swap growing:** stop launching and tell the user. The harness watchdog kills
  a run below 1 GB. (2026-10-14)
- **Content failures are not retried:** the simulator is deterministic, so a crash, a wrong number or an overflow
  repeats on rerun with the same inputs. Diagnose it (`debug` skill). (2026-10-14)

## I.6 Git (2026-10-14)

- The fork is `origin` = `https://github.com/qwxe/LLMServingSim.git`. No git identity is set: commit with
  `git -c user.name=qwxe -c user.email=psh010103@gmail.com commit ...`, and end messages with the
  `Co-Authored-By` line the session gives. (2026-10-14)
- Commit only on your own branch, one method or item per commit. Never bump gitlinks. (2026-10-14)
- Code branches stay local unless the user asks. Experiment results and handoff notes on
  `explore/rate-wl-phase3` are pushed as soon as they are written (user, 2026-10-12/13), with the credential
  helper (never print the token):
  ```
  git -c credential.helper= -c 'credential.helper=!f() { echo username=x-access-token; echo password=$(tr -d "\r\n" < /home/asd/LLMServingSim/gh_token); }; f' push origin <branch>:<branch>
  ```
  The same helper works for `fetch`. The submodule fetch fails (astra-sim pin not on the remote); the main repo
  fetch still succeeds. (2026-10-14)
- Stage only your own files; others' uncommitted files share the worktrees. Notes under `outputs/` are
  gitignored: add them with `git add -f`. (2026-10-14)
- The stash is shared by all worktrees and sessions: never bare `git stash`/`pop`; prefer a WIP commit. (2026-10-14)
- **Knowledge base exception** (I.21). Knowledge entries and the regenerated catalog are committed on `main`
  from any line of work, through the main working tree `/home/asd/LLMServingSim`, staged by path, even when your
  own work is on another branch. A Codex worker sandboxed to another worktree cannot write there: it proposes
  the entries in its report and its caller commits them. (2026-10-14)
- **Rule files** (AGENTS.md 0.2, 0.5): a commit on `main` that changes the rule files stays local until its
  review passes (PASS or PASS with notes); then push `main` with the credential helper above and run
  `python3 agents/publish_agentsmd.py` at once (user, 2026-10-14). (2026-10-14)
- Branch and worktree layout for research code: II.3 and II.4. (2026-10-14)

## I.7 Processes and cleanup (2026-10-14)

- Kill by PID only (AGENTS.md 0.3 rule 5). (2026-10-14)
- A process reparented to PID 1 runs outside every slot: kill it by PID. (2026-10-14)
- Before you finish, remove your measurement tree (unless the brief keeps it), fork server, `/tmp` scratch and
  orphan processes. (2026-10-14)
- Files written by the container are root-owned: delete them with `docker exec servingsim_docker rm -rf ...`. (2026-10-14)
- `validate.sh`/`validate-par` rewrite `bench/examples/*/outputs/sim.log` with only run-id and wall-time changes:
  revert them with `git checkout`. (2026-10-14)

## I.18 Monitoring running work (2026-10-14)
<!-- general -->

User, 2026-10-14: runs that take compute or sit on the critical path of the goal are monitored periodically. (2026-10-14)

- **What.** Every job that holds compute (a job slot, a build, a long test, anything at high CPU or memory) and
  every job on the critical path of the current goal, from launch to exit. (2026-10-14)
- **Who.** The agent that launched it. A Codex worker returns before a long job ends, so its caller runs the
  health loop below in the background and acts on what it reports (calling a Codex Luna worker for checks it
  needs). The loop prints only on an anomaly or at exit. The master does not run job health checks itself; it
  keeps a watch on every watch mechanism and the progress ledger current (I.23). (2026-10-14)
- **Mechanism.** A completion notification alone does not catch a hang. Run both: the job (or its wait) in the
  background so its exit wakes the agent, and a health loop that checks every ~180 s and prints only on an
  anomaly or at the end. The health loop itself runs as a background command whose exit (on an anomaly or at
  the end) wakes the agent; its PID is recorded only so that another session can check it. (2026-10-14)
- **How often.** A health check about every **3 minutes**, from a background wait with a ~180 s sleep or a
  scheduled wake-up. Never a tight loop; wait on a PID or an output file, not on `pgrep -f` (I.16). (2026-10-14)
- **What a check looks at.** Progress (heartbeat, simulated clock or output still advancing), CPU state (running,
  or stuck near 0%), memory (process growth, machine free memory, swap), errors in the log, and the expected
  finish. The run rules give this repository's commands and healthy values. (2026-10-14)
- **Failure classes.** Classify every failure before acting; the class decides the action (user, 2026-10-14):

  | class | what it is | action |
  |---|---|---|
  | infra-transient | the environment failed once (a hang at start, a lost connection, a killed worker) and the inputs are fine | capture diagnostics, kill by PID, retry **once**; the retry is recorded in the task trail (2026-10-14) |
  | infra-permanent | the environment fails again or cannot work (out of memory, disk full, missing tool, a second transient failure) | stop launching; kill the offender if it is your own job and endangers others (another agent's job: only the master kills it, on the user's order); tell the spawner (2026-10-14) |
  | content | the job itself is wrong (a crash, an assertion, a wrong or impossible number); a deterministic job repeats it | no retry; diagnose (the `debug` skill) or tell the spawner (2026-10-14) |
  | spec mismatch | the job ran but not what was asked (wrong arm, configuration, inputs or version) | stop the block; fix the specification; the results do not count (2026-10-14) |
  | integrity | the record cannot be trusted (missing or truncated output, a fingerprint that does not match, results from mixed trees) | quarantine the results; never use them in a comparison; tell the spawner (2026-10-14) |

  A value that was not measured is recorded as null (missing), never as 0. (2026-10-14)
- **Acting** (on your own jobs only; another agent's job is reported to the master). Act by the class above.
  Runaway memory or a machine short of memory: stop launching, kill the offender, tell the spawner. Report an
  anomaly to the spawner at once, not at the end; record it, its class and the action in the task trail, and
  record a new kind of anomaly in the knowledge base (I.21). Healthy checks are not logged. (2026-10-14)

## I.20 Hooks (2026-10-15)

Mechanical enforcement of the never-break rules (user, 2026-10-14). Change a hook only with its tests
(`.wt/testenv/bin/python -m pytest .claude/hooks -q`) and update this section in the same commit. (2026-10-14)

`.claude/hooks/notify_stop.py` runs when the master finishes an answer (`Stop`; subagents fire `SubagentStop` and do
not notify): it raises a Windows balloon notification through `powershell.exe`, detached, and never blocks; any
failure is silent (user, 2026-10-15: "그리고 답이 끝나면 user한테 알림을 띄우는 걸로."). (2026-10-15)

`.claude/hooks/guard_bash.py` runs before every Bash tool call in this repository (`.claude/settings.json`,
`PreToolUse`, matcher `Bash`). A refused command exits 2 with one line `BLOCKED by .claude/hooks/guard_bash.py
(<rule id>: <reason>)`. Any parse error or git failure allows the command. (2026-10-14)

**Where it looks.** Inside `;`, `&&`, `||`, `|`, newlines, `$(...)` (quoted or not) and backticks, `bash/sh -c` (also
`-lc`, `-ec`), `eval`, shell keywords (`if/then/else/do/while/{/!`), and wrappers (`sudo`, `env`, `nohup`, `time`,
`xargs`, `timeout`, `docker exec`). (2026-10-14)

**Where it does not look.** Heredoc bodies, the text arguments of echo/printf, grep patterns, commit messages,
and comments. It is a safety net against mistakes, not against deliberate evasion. (2026-10-14)

| rule | blocks | allows on purpose | do this instead |
|---|---|---|---|
| 0.3 rule 5 | `pkill -f`, `pkill -<flags with f>`, `pkill --full`, `killall` | `pkill <name>`, `kill <pid>`, `pgrep -f` | kill by PID; in the container `docker exec servingsim_docker kill <pid>` (2026-10-14) |
| 0.3 rule 7 (force-push) | `git push` with `--force`, `-f` (or a cluster with f), `--force-with-lease[=..]`, `--force-if-includes`, a refspec starting with `+` or containing `:+` | normal pushes, `-u`, `--follow-tags` | push a new branch, or ask the user (2026-10-14) |
| I.16 (staging) | `git add -A`, `--all`, a cluster with `A`, `.`, `./` (also after `--`) | `git add <paths>`, `-f <path>`, `-u <path>`, `git add -- -A` (a file named -A), `--help` | name your files (2026-10-14) |
| I.16 (stash) | bare `git stash` (also with options only), `git stash push`, `save`, `clear`, `pop`/`drop` without a ref | `git stash list`, `show`, `apply`, `pop`/`drop stash@{n}`, `--help`/`-h` | a WIP commit on your branch (2026-10-14) |
| 0.3 rule 4 | `timeout ... slotrun ...` | `slotrun sim timeout N cmd`, `timeout N <other cmd>` | let slotrun manage the job; kill by PID if it hangs (2026-10-14) |
| 0.3 rule 7 (token) | a printer (`cat tac nl less more head tail xxd od hexdump strings base64 sort cut grep rg sed awk ...`) with `gh_token`/`hf_token` as a file operand or as `< file` | the credential helper `$(tr -d "\r\n" < gh_token)`; `ls`, `test -f`, `wc -c <`, `chmod` on the file; searching for the word: `grep [-A N] [-m N] gh_token <files>`, `rg -g '*.md' gh_token` | use the credential helper (I.6); if the hook misreads a search, give the pattern with `-e gh_token` (2026-10-14) |
| I.4 | `--dangerously-bypass-approvals-and-sandbox` as an argument of any command except text commands (echo, printf, grep, sed, awk, cat, git) | mentioning the flag in text | `codex exec -s read-only`; a task worker uses `-s workspace-write` or `-s danger-full-access` (I.4) (2026-10-14) |
| 0.3 rule 7 (commit) | `git commit` whose change adds a GitHub (`gh?_`, `github_pat_`), Hugging Face (`hf_`), `sk-` or AWS `AKIA` key, or a private-key header, or adds a file named `gh_token`/`hf_token`. The index is checked; with `-a`, `-i`, `-o` or pathspecs, `git diff HEAD` is checked instead. The block message names `file:line` and the kind, never the value. | mentions such as `ghp_` without a token-length tail; `--dry-run`; `-sm msg` and `-mmsg` checked as index-only | remove the secret, or unstage the file (2026-10-14) |

**Known limits** (accepted for precision; the user, 2026-10-14):
- These token-file routes are not followed (2026-10-14):
  - globs (`cat gh_to*`, `cat *` in the repo root);
  - `$(< gh_token)`;
  - command substitutions that produce the name (`cat $(echo gh_token)`);
  - interpreter code that opens the file (`python3 -c "open('gh_token')"`, `perl -e`, `node -e`, `ruby -e`). (2026-10-14)
- Variable indirection (`g=git; $g stash`, `P=pkill; $P -f`, `f=gh_token; cat $f`) is not followed. (2026-10-14)
- Unquoted `$(...)` is split by the tokenizer and checked as separate commands. (2026-10-14)
- Heredoc bodies are not checked (`python3 - <<EOF ... EOF`). (2026-10-14)
- `$(...)` inside single quotes is still checked, because the quoting is lost. (2026-10-14)
- Aliases and shell functions are not followed. (2026-10-14)
- The commit message itself is not scanned for secrets (finding 6, out of scope). (2026-10-14)
- If the hook times out (60 s), the command is not blocked. (2026-10-14)

`.claude/hooks/session_start.py` (SessionStart) prints at most 10 lines: each `notes/ledger/*.md` (up to 7) with
its count of rows not `done`; when `knowledge/KNOWLEDGE.md` exists, the number of rows in its "Promotion
candidates" table (pitfalls the master proposes to the user, I.21); and a pointer to AGENTS.md 0.4. It prints no
row contents. Tests: `.wt/testenv/bin/python -m pytest .claude/hooks -q`. (2026-10-14)

## I.22 Shared resources (2026-10-14)

User, 2026-10-14: "공유 자원에 대해서는 명시해줘". The general rule is in I.16: never revert, clean, kill, reset or
reconfigure what you did not create; teardown removes only your own. This is the list for this machine. Anything
not listed that another agent or session could also use counts as shared. (2026-10-14)

| resource | shared by | you may | you may not |
|---|---|---|---|
| the main working tree `/home/asd/LLMServingSim` (branch `main`) | every session; the user's uncommitted files (e.g. `.gitignore`, `workloads/`, corpora) | edit and stage the files your brief gives you, by path | `git add -A`, `git checkout -- <others' files>`, `git clean`, `git reset --hard`, switching its branch (2026-10-14) |
| worktrees under `.wt/` (`.wt/p3/pe`, measurement trees, `.wt/corpus`) | the sessions that created them | use a tree your brief names; create and remove your own | remove, reset or switch the branch of a tree you did not create (2026-10-14) |
| the git stash and the local branches | all worktrees and sessions | `git stash list/show/apply` | bare `git stash`/`pop`, `drop`/`clear`; deleting or force-moving another's branch (2026-10-14) |
| `origin` (https://github.com/qwxe/LLMServingSim) and https://github.com/qwxe/agents.md | every session | push your own branch as I.6 says | force-push; push branches the user keeps local (2026-10-14) |
| the container `servingsim_docker` | every run of every agent | `docker exec` your runs; kill your own PIDs | restart or stop it; `pip install` into it; kill PIDs you did not launch (2026-10-14) |
| job slots (`.wt/bin/slotrun`, `.wt/perf-tools/slots/`) and machine memory | every agent | take the slots your brief gives you, through `slotrun` | edit `sim.n` or the slot files; run outside a slot (I.5) (2026-10-14) |
| tools in `.wt/bin/` (`slotrun`, `validate-par`, `hangdump`) and the host venv `.wt/testenv` | every agent | run them | edit or reinstall them without a brief that orders it (2026-10-14) |
| the session scratchpad (`/tmp/claude-1000/<project>/<session>/scratchpad`) and other temporary directories | the master and every subagent of the session | create files or a subdirectory of your own; delete them by explicit path | glob-delete (`rm -f <dir>/*`) a directory you did not create (`pitfalls/ops-shared-scratchpad-wipe`) (2026-10-14) |
| `validate-par` scratch `/tmp/vpar_*` and `bench/examples/*/outputs/` | one `validate-par` at a time (I.5) | read; revert the `sim.log` rewrites of your own run (I.7) | delete another run's scratch; start a second `validate-par` (2026-10-14) |
| progress ledgers `notes/ledger/*.md`, handoff files, task trails of other tasks | the master of each line; the task's agents | append to your own task trail | edit another line's ledger or another task's trail (2026-10-14) |
| the knowledge base `knowledge/` | every role (I.21) | add an entry; append an occurrence; update or refute an entry with evidence | delete an entry; rewrite another's evidence; edit the generated catalog `knowledge/KNOWLEDGE.md` by hand (2026-10-14) |
| generated files `GENERAL.md`, `knowledge/KNOWLEDGE.md` | their generators | regenerate and commit with the source change | hand edits (2026-10-14) |
| Claude settings and hooks `.claude/settings.json`, `.claude/hooks/`, the master's memory directory | every Claude session | read | change them without the user's order (hooks: with their tests, I.20) (2026-10-14) |
| token files `gh_token`, `hf_token` | every agent | use through the credential helper (I.6) | print, copy or move them (2026-10-14) |
| the Codex binary in `~/.vscode-server/extensions/` | every agent | run it (I.4) | update or move it (2026-10-14) |

## I.16 Git, processes and safety: the general rules (2026-10-14)
<!-- general -->

- Never print a token file and never put a token in a remote URL; push through a credential helper that reads
  the file. Never force-push. (2026-10-14)
- Commit only on your own branch, one item per commit; stage only your own files (others' uncommitted files share
  the worktrees). Never `git add -A` in a shared tree. Exception: knowledge base entries are committed where the
  knowledge base lives, from any line of work (the run rules say how); a worker that cannot write there
  proposes its entries in its report. (2026-10-14)
- The stash is shared by all worktrees and sessions: never bare `git stash`/`pop`; prefer a WIP commit. (2026-10-14)
- Code branches stay local unless the user asks; notes and results the user wants visible elsewhere are pushed
  as soon as they are written. (2026-10-14)
- Never `pkill -f` or `killall`; kill by PID. Clean up your own scratch, trees and orphan processes when done. (2026-10-14)
- **Shared resources** (user, 2026-10-14). Never revert, clean, kill, reset or reconfigure anything you did not
  create: other agents' files and processes, shared trees, the shared stash, containers, job slots, tool
  installations, settings. Teardown removes only what you created and recorded. When a shared resource is in
  your way, report it to your spawner; do not fix it. The run rules list this repository's shared resources. (2026-10-14)
- To wait for a process, wait on its PID (`while kill -0 <pid>`) or on its output file, never on `pgrep -f
  <pattern>`: the waiting shell's own command line contains the pattern, so the loop matches itself and never ends
  (verifier, 2026-10-14).
- Ask the user before starting expensive jobs they did not request. Within an approved experiment, keep the
  available slots full. (2026-10-14)
- If a permission check blocks an action, do not work around it; report it to the user. (2026-10-14)

## Operations pitfalls (2026-10-14)

These are promoted pitfalls; a new pitfall is recorded first in the knowledge base (I.21, AGENTS.md 0.5 item 3). (2026-10-14)

- Following an old rule number ("0.2 rule 6"): the never-break rules are AGENTS.md 0.3. (2026-10-14)
- Reading the 14-slot slotrun cap as the budget: the shared budget is 8 `sim` slots. (2026-10-14)
- Relying on the completion notification to notice a hang (I.18). (2026-10-14)
- Starting `validate-par` while another agent's is running. (2026-10-14)
- Retrying a deterministic failure "once more": only infra-transient failures are retried (I.18). (2026-10-14)
