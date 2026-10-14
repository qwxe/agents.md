# agents/CODEX.md — Codex research worker

Scope: Codex, and any Claude agent that calls Codex. Codex reads "Codex's own rules" and the files its brief names, and ignores the rest. Sections marked `<!-- general -->` are copied into `GENERAL.md` (AGENTS.md 0.2).

## I.4 Codex CLI (2026-10-14)
<!-- general -->

### Codex's own rules

Codex works in one of three roles; the first line of the brief names it ("Role: Codex research worker", "Role:
Codex task worker", "Role: Codex verifier").

- **Every role.** Answer in the language the brief asks for. Never print token or credential files and never put a
  token in a remote URL. Never decide a non-obvious question (the brief, the decisions list and the code do not
  settle it, and the choices differ in behaviour, results, interfaces or scope): finish the work that does not
  depend on it, then stop and return the question with two or three options, what changes under each and your
  recommendation. Say what you verified and what you did not.
- **Research worker.** Read-only: never edit, commit, push or launch anything. Cite a source (URL, paper, file
  path) for each claim and mark what you could not verify. Your output is a second opinion that the caller verifies.
- **Task worker** (simple and general work). Read the rule files your brief names before anything else: the rules
  that must never be broken, the run rules, and the role file of the work (implementer duties, or the verifier
  checklist). Work only in the worktree and branch the brief names and write only the files it gives you.
  Launch runs, kill processes, commit and push only where the brief orders it, and then exactly as the run rules
  say: runs through the job slots, kill by PID, name your files when staging, never force-push. Tests first, never
  weaken a test. Never wait on a long run inside your own call: launch it detached, record its id and PID, and
  return; the caller monitors it and, when it ends, calls a new task worker for the steps after it (summaries,
  commits). Short tests run inside the call. End with the report headings the brief names, written to the task
  trail.
- **Verifier.** A task worker that reviews and never fixes: follow the verifier checklist the brief names; write
  nothing but your verdict to the task trail; the reviewed tree's status and HEAD are unchanged at the end.

### Calling Codex (Claude agents)

Run it on the host, not inside a build or run container. A research call needs no job slot (the one exception
to "no CPU outside your slot"), but don't run many at once; a task worker's tests and runs take the slots its
brief gives it. `--search` enables live web search for literature work.

```
timeout <secs> "$CODEX" [--search] exec --ephemeral -s <sandbox> [--add-dir <dir>] --color never -m <model> \
  -c model_reasoning_effort="<level>" -C <tree> -o "$SCRATCH/codex_last.txt" "<prompt>" \
  </dev/null >"$SCRATCH/codex.out" 2>"$SCRATCH/codex.err"
```

| role | sandbox | timeout |
|---|---|---|
| research worker | `-s read-only` | 600 s |
| task worker or verifier that edits, tests or commits in a worktree | `-s workspace-write --add-dir <main repo>/.git` (a worktree's git metadata lives in the main repository's `.git`) | sized to the task, default 3600 s |
| task worker that launches runs, uses the container runtime, kills processes or pushes | `-s danger-full-access` (workspace-write blocks the network and, unverified, the container socket) | as above |

- Call task workers in the background so their exit wakes the caller; `-C` is the worker's own worktree. One
  task worker per tree at a time (one writer per file, I.15).
- The guard hooks that block forbidden commands watch the Claude agent's own shell only, not the commands Codex
  runs. A task worker's brief therefore always names the rules that must never be broken.

- `$CODEX` is the installed codex binary; where it lives on this machine is in the repository's `AGENTS.md`.
- Always `</dev/null` (else it waits on stdin); for a long brief pass `-` and pipe it on stdin. The answer is in
  the `-o` file. Add `--skip-git-repo-check` outside a git repo. Never `--dangerously-bypass-approvals-and-sandbox`.
- Always pass the effort: unset, it runs at `low`.

| job | model | flags |
|---|---|---|
| simple-tier task (I.3): mechanical work with a clear spec | Luna | `-m gpt-6-luna -c model_reasoning_effort="medium"` |
| general-tier task (I.3), and the verifier for changes outside the byte-exact core | Sol Medium | `-m gpt-6.1-sol -c model_reasoning_effort="medium"` |
| find docs/papers/source, summarise with sources | Luna | `-m gpt-6-luna -c model_reasoning_effort="medium"` |
| judge assumptions, complexity, pros/cons; choose what to investigate; mixed jobs | Sol Light | `-m gpt-6.1-sol -c model_reasoning_effort="low"` |
| correctness checks, hard counterexamples, comparing designs | Sol Medium+ | `-m gpt-6.1-sol -c model_reasoning_effort="medium"` (or `high`/`xhigh`) |

## Codex in this repository (2026-10-14)

- Binary (not on PATH; the path changes with every VS Code extension update):
  `CODEX=$(ls -d ~/.vscode-server/extensions/openai.chatgpt-*/bin/linux-x86_64/codex | tail -1)`.
- Research: `-C /home/asd/LLMServingSim`, no `slotrun` slot. Task workers: `-C` the worktree under `.wt/`,
  `--add-dir /home/asd/LLMServingSim/.git`; runs and `docker exec` need `-s danger-full-access`. Host only,
  never inside `servingsim_docker`.
- Rule files a task worker's brief names: `AGENTS.md` 0.1 and 0.3, `agents/INTERFACE.md` I.10-I.14,
  `agents/OPERATIONS.md`, and `agents/IMPLEMENTER.md` (task worker) or `agents/VERIFIER.md` (verifier);
  `agents/SIM-REFERENCE.md` when it touches `serving/`, `profiler/` or `bench/`.
- Install details and more flags, if a flag above is missing: `AN/CODEX-DETAIL.md` (research branch, 0.4).

## Codex pitfalls (2026-10-14)
<!-- general -->

- Running without `</dev/null`: it waits on stdin forever.
- Omitting the reasoning effort: it runs at `low`.
- Relying on an answer without opening its sources: Codex output is a second opinion.
- Assuming the guard hooks protect a task worker: they watch the Claude agent's shell only, so the brief must name
  the rules that must never be broken.
- A task worker waiting on a long run inside its call: the call's timeout kills it mid-run. Launch detached and
  return; the caller monitors.
