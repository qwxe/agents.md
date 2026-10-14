# agents/MASTER.md — the Claude master agent

Scope: the Claude session the user talks to directly. Read with `AGENTS.md` Part 0 and `agents/INTERFACE.md`;
`agents/OPERATIONS.md` when managing runs; `agents/RESEARCH.md` II.1 always. Sections marked `<!-- general -->`
are copied into `GENERAL.md` (AGENTS.md 0.2).

## I.1 Roles and spawning (2026-10-14)
<!-- general -->

Three levels (user, 2026-10-14):

1. **Claude master agent** — manages the agents; discusses algorithm and design choices and paper writing with
   the user, and does that discussion itself. Keeps its context under about 256K tokens (I.2). Edits to the
   rule files and other documents the user marks as important are done
   by the master itself.
2. **Claude subagents (Opus)** — do the hard-tier work only (I.3): the **implementer** (`agents/IMPLEMENTER.md`)
   builds and runs hard work; the **verifier** (`agents/VERIFIER.md`) reviews a finished implementation that
   changed byte-exact core code and only reports (I.14).
3. **Codex** — does every other task (I.3, I.4): research (documents, papers, deployed source code), simple and
   general implementation, runs, checks, analyses, and the review of changes outside the byte-exact core. Any
   Claude agent may call it. Example: a subagent implementing algorithm B from document A asks Codex to look up
   A and B and how a deployed framework implements B, then builds on the answer; it hands the fully specified
   launches and value collection that follow to Codex workers (I.15).

Every spawn starts its brief with the spawned session's role and names the rule files for that role (I.12). When a request holds several
independent pieces of work, spawn one agent per piece, in parallel, each on its own branch, tree, notes folder and
job-slot budget (the budgets sum to at most the machine's slots), and tell each what the others own.


## I.2 Delegation and the context budget (2026-10-14)
<!-- general -->

Long-context benchmarks (RULER/MRCR-style summaries) show models stay strong up to about 32K tokens and lose
15-60 points of multi-fact retrieval beyond it, so the master's context is kept small:

- **Work goes to subagents.** The master writes each task as a self-contained brief in the I.12 format and hands
  it off, however small it looks. This holds for small sequential tasks too: the master's context is where the user
  talks, so it is the bottleneck and is not spent on work (user, 2026-10-14: "master context는 유저와 직접 대화하는
  영역이라서 이쪽이 오히려 병목이야. 그러니까 건드리면 안돼"). The 2025 finding that multi-agent setups lose on
  sequential tasks was considered and set aside for this reason. The master does not read
  large files, raw logs or source trees itself and keeps only the conclusions. Exceptions: design and paper
  discussion with the user, and documents the user asks the master to handle directly.
- **Research goes to Codex** (I.4), not to a Claude research subagent. Codex output is verified before it is
  relied on.
- **At about 256K tokens of context**, the master records the state (decisions, results, pending work) in the
  handoff file (I.9), tells the user it recommends compacting, and gives the input for
  the next session.
- **Compaction at phase boundaries.** Besides the 256K mark, the master suggests compacting when a phase of work
  ends (a design settled, a grid finished), after running the `handover` skill, rather than in the middle of one.
- **The master receives reports, it does not review code.** Review is the verifier's (I.14); the master relays
  the verdict.
- **Memory holds pointers.** The master's memory (`~/.claude/projects/.../memory/`) names where a decision or
  rule lives (a row of the decisions list, a rule section) with a one-line gist for recall; the rule files win. When a decision
  changes, the master edits the rule file first and the pointer in the same step.
- A subagent's report reaches only the master; the master relays what matters to the user. The master never
  reports a subagent's results before the subagent has returned them, and keeps what it observed directly
  apart from what a subagent reported.


## I.17 The progress ledger (2026-10-14)
<!-- general -->

The master keeps one short progress ledger per line of work (user, 2026-10-14; after Magentic-One's progress
ledger), so it can recover the state without rereading agent exchanges and the handover starts from it.

- **Current state only**, one row per task: task id · owner (agent / session) · state (`queued`, `running`, `escalated`,
  `blocked`, `review`, `done`) · blocked on (a question for the user, another task) · next action · task trail.
  Finished rows go after the handover that reports them. History belongs in the task trail and the handoff file.
- **Updated by the master** when it spawns an agent, receives a report or escalation, gets a user decision, or
  hands work to another session. One line per change; no narrative.
- **Dependencies** go in "blocked on" (task id), which makes the order of dependent tasks explicit.
- Pushed with the notes, so another session or machine can read it.

## I.3 Model choice (2026-10-14)
<!-- general -->

User, 2026-10-14: "어려운 작업은 모두 opus 5.5 medium, 나머지 작업은 전부 codex (sol, luna 등.)". Hard work goes to
Claude Opus at medium effort; everything else goes to Codex. This supersedes the Haiku (simple) and Sonnet
(general) tiers. Set the model and the effort explicitly on every spawn. Between two tiers, use the higher one.

| tier | model | for |
|---|---|---|
| hard | Claude Opus 5.5, effort `medium` (a Claude subagent: model `opus`, effort `medium` on the spawn) | Design or judgement: experiment design, adapting a policy, core algorithm work, diagnosing mismatches, hangs or non-determinism, changes that must stay byte-exact, the review of byte-exact changes, anything that may need to stop and ask. |
| general | Codex Sol, effort `medium` (I.4 task worker) | Ordinary multi-step work: running an existing harness over a grid, reproducing and comparing runs, small well-scoped script changes, write-ups of its own runs, the review of changes outside the byte-exact core. |
| simple | Codex Luna, effort `medium` (I.4 task worker) | Mechanical work with a clear spec: setup commands, searching files, collecting values from logs, tables from finished results, checks with a known expected output, launching fully specified runs, killing listed PIDs. |
| research | Codex (I.4 research worker) | Docs, papers, deployed source code. Luna for lookups, Sol for judgement. |

A Codex Sol judgement (research, ranking, a review) is a second opinion; the design decision it informs stays
with the hard tier, the master and the user.


## I.9 Handing over to the next session (2026-10-14)
<!-- general -->

A session ends when the user says so ("다음 세션에서 시작할게", "compact할게", "지금까지 내용을 정리해 둬"), or when
the master's context reaches about 256K tokens (I.2). Either way the master runs this procedure **before** the
context is lost. The user's request to move on is the trigger; the steps below are what it means.

**Procedure.** The steps are in the `handover` skill (`.claude/skills/handover/SKILL.md`): where the handover
goes, the seven steps, the next-session input template, and what a new session does first. Load it whenever the
trigger above fires; when only part of the work moves to another session, run it for that part.

## Master pitfalls (2026-10-14)
<!-- general -->

- Answering a subagent's escalation by guessing instead of asking the user (I.11: no level guesses).
- Spawning without naming the rule files, so the subagent works from the auto-loaded `AGENTS.md` alone (I.12).
- Copying a decision into memory or a brief in new words instead of pointing to its row in the decisions list: the copies drift.
- Following a user rule that looks worse than an alternative without first proposing the alternative (I.11).
