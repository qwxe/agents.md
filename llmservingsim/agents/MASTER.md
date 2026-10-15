# agents/MASTER.md — the Claude master agent

Scope: the session explicitly assigned the master role, including a GPT/Codex session (AGENTS.md 0.1). Read with `AGENTS.md` Part 0 and `agents/INTERFACE.md`;
`agents/OPERATIONS.md` when managing runs; `agents/RESEARCH.md` II.1 always; the knowledge catalog
`knowledge/KNOWLEDGE.md` (its promotion candidates at session start, the categories a brief will name). Sections marked `<!-- general -->`
are copied into `GENERAL.md` (AGENTS.md 0.2).

## I.1 Roles and spawning (2026-10-15)
<!-- general -->

The assigned role determines duties independently of the model. The labels below retain the existing
invocation paths and model routing; a model name alone never assigns a role. (2026-10-14)

Three levels (user, 2026-10-14):

1. **Claude master agent** — manages the agents; discusses algorithm and design choices and paper writing with
   the user, and does that discussion itself. Keeps its context under about 256K tokens (I.2). Its own rule-file
   changes go up to the user as proposals; a subagent's proposed rule change (from any depth of the spawn chain)
   is reviewed and approved or rejected by the master in the user's place (AGENTS.md 0.5). Once a change is
   approved, the master or an agent it assigns makes the edit. Other documents the user marks as important are
   edited by the master itself. (2026-10-15)
2. **Claude subagents (Opus)** — do the hard-tier work only (I.3): the **implementer** (`agents/IMPLEMENTER.md`)
   builds and runs hard work; the **verifier** (`agents/VERIFIER.md`) reviews a finished implementation that
   changed byte-exact core code and only reports (I.14). (2026-10-14)
3. **Codex** — does every other task (I.3, I.4): research (documents, papers, deployed source code), simple and
   general implementation, runs, checks, analyses, and the review of changes outside the byte-exact core. Any
   Claude agent may call it. Example: a subagent implementing algorithm B from document A asks Codex to look up
   A and B and how a deployed framework implements B, then builds on the answer; it hands the fully specified
   launches and value collection that follow to Codex workers (I.15). (2026-10-14)

Every spawn starts its brief with the spawned session's role and names the rule files for that role (I.12). When a request holds several
independent pieces of work, spawn one agent per piece, in parallel, each on its own branch, tree, notes folder and
job-slot budget (the budgets sum to at most the machine's slots), and tell each what the others own. (2026-10-14)


## I.2 Delegation and the context budget (2026-10-14)
<!-- general -->

Long-context benchmarks (RULER/MRCR-style summaries) show models stay strong up to about 32K tokens and lose
15-60 points of multi-fact retrieval beyond it, so the master's context is kept small (2026-10-14):

- **Work goes to subagents.** The master writes each task as a self-contained brief in the I.12 format and hands
  it off, however small it looks. This holds for small sequential tasks too: the master's context is where the user
  talks, so it is the bottleneck and is not spent on work (user, 2026-10-14: "master context는 유저와 직접 대화하는
  영역이라서 이쪽이 오히려 병목이야. 그러니까 건드리면 안돼"). The 2025 finding that multi-agent setups lose on
  sequential tasks was considered and set aside for this reason. The master does not read
  large files, raw logs or source trees itself and keeps only the conclusions. Exceptions: design and paper
  discussion with the user, and documents the user asks the master to handle directly. (2026-10-14)
- **Research goes to Codex** (I.4), not to a Claude research subagent. Codex output is verified before it is
  relied on. (2026-10-14)
- **At about 256K tokens of context**, the master records the state (decisions, results, pending work) in the
  handoff file (I.9), tells the user it recommends compacting, and gives the input for
  the next session. (2026-10-14)
- **Compaction at phase boundaries.** Besides the 256K mark, the master suggests compacting when a phase of work
  ends (a design settled, a grid finished), after running the `handover` skill, rather than in the middle of one. (2026-10-14)
- **The master receives reports, it does not review code.** On each report it first runs the receipt checks of
  I.13 (claimed commits and files exist; no unrequested time limit); review is the verifier's (I.14); the master
  relays the verdict. (2026-10-14)
- **Memory holds pointers.** The master's memory (`~/.claude/projects/.../memory/`) names where a decision or
  rule lives (a row of the decisions list, a rule section) with a one-line gist for recall; the rule files win. When a decision
  changes, the master edits the rule file first and the pointer in the same step. (2026-10-14)
- A subagent's report reaches only the master; the master relays what matters to the user. The master never
  reports a subagent's results before the subagent has returned them, and keeps what it observed directly
  apart from what a subagent reported. (2026-10-14)


## I.17 The progress ledger (2026-10-14)
<!-- general -->

The master keeps one short progress ledger per line of work (user, 2026-10-14; after Magentic-One's progress
ledger), so it can recover the state without rereading agent exchanges and the handover starts from it. (2026-10-14)

- **Current state only**, one row per task: task id · owner (agent / session) · state (`queued`, `running`, `escalated`,
  `blocked`, `review`, `done`) · blocked on (a question for the user, another task) · watch (how the master
  learns the task ended or broke, I.23; `—` when nothing is live) · next action · task trail. Above the table, one
  line `Heartbeat: <id> since <time>` (I.23). (2026-10-14)
- **Direct work only.** The ledger tracks the master's own spawns and jobs. An agent's helpers (an implementer's
  Codex workers, its runs) are tracked in that agent's task trail, not here.
  A row is removed as soon as its task is `done`, in a commit that names the task id (`Ledger: <task-id> done`);
  the task trail and the handoff file hold the history (user, 2026-10-14: "1번으로 해줘").
- **Updated by the master** when it spawns an agent, receives a report or escalation, gets a user decision, or
  hands work to another session. One line per change; no narrative. (2026-10-14)
- **Dependencies** go in "blocked on" (task id), which makes the order of dependent tasks explicit. (2026-10-14)
- Pushed with the notes, so another session or machine can read it. (2026-10-14)

## I.23 The master's watch (2026-10-14)
<!-- general -->

User, 2026-10-14: "master agent의 모니터링 같은데. 지금은 구현이 됐다 말았다 해. 이걸 명시적으로 해줘." Health checks
of each job belong to the agent that launched it (I.18); the master's duty is that every live piece of work has
a working watch and that the progress ledger matches reality. (2026-10-14)

- **A watch per live item.** Every live item the master spawned or launched itself (agent, Codex worker, job,
  health loop) has a ledger row whose *watch* column names how its end or failure reaches the master. Watch
  kinds: the background agent's id (its report wakes the master); the id of a background command that waits on a
  PID or an output file, or that runs a health loop (I.18; its exit wakes the master); a monitor id; a **result
  file** that appears or changes when the item ends. Ids that exist only in this session (agent, background
  command and monitor ids) are marked `(session)`; a PID and a result file are valid across sessions. A live
  item with no watch is an anomaly: give it one at once. (2026-10-14)
- **Heartbeat.** While anything is live, the master keeps one background heartbeat: a background command that
  sleeps about 30 minutes (`sleep 1800`) and whose exit wakes the master. Exactly one at a time; its id and start
  time are the ledger's `Heartbeat:` line. After a compaction or in a new session, when the heartbeat cannot be
  verified as running in this session, start a new one and update the line. (2026-10-14)
- **Checking that a watch is alive.** Within the session that created it: a background agent or command by its
  notification state (still running, or its completion seen). Across sessions (after a handover, or for a
  `(session)` id from another session): only result files and PIDs count; a session-local id from elsewhere
  proves nothing. (2026-10-14)
- **On every wake** (heartbeat, report, notification, user message), before anything else (2026-10-14):
  1. check that each watch is alive, as above;
  2. reconcile the ledger with reality: PIDs, result files, run ids, branch heads and commits against each row;
     fix the rows that are wrong;
  3. restart a dead watch at once; report to the user a job whose watch died and whose state is unknown;
  4. re-arm the heartbeat if anything is still live; when nothing is live, let it lapse. (2026-10-14)
- The heartbeat checks watches and the ledger only; it does not replace the ~3-minute health loop of each job. (2026-10-14)
- A heartbeat is never a tight loop and never waits on a pattern match (I.16). (2026-10-14)

## I.3 Model choice (2026-10-14)
<!-- general -->

User, 2026-10-14: "어려운 작업은 모두 opus 5.5 medium, 나머지 작업은 전부 codex (sol, luna 등.)";
clarified by the user on 2026-10-14: "좋아. gpt에 대한 기준을 좀 더 명확히 해줘." Use Codex Sol at medium
effort by default. Choose Luna only for fully specified mechanical work; choose Opus only for the hard criteria
below. This replaces the broad "design or judgement", "anything that may need to stop and ask" and "between two
tiers, use the higher one" criteria. Set the model and effort explicitly on every spawn. (2026-10-14)

| tier | model | selection criteria |
|---|---|---|
| general (default) | Codex Sol, effort `medium` (I.4 task worker) | Work requiring code comprehension, several steps, local implementation choices, evidence-based comparison or ordinary debugging within settled requirements. Includes implementing a decided design, script and harness changes, reproducing and comparing approved runs, result analysis and write-ups, and reviews outside byte-exact core changes. (2026-10-14) |
| simple | Codex Luna, effort `medium` (I.4 task worker) | Commands, inputs, outputs and acceptance checks are specified; execution requires no substantive interpretation or diagnosis. Includes exact file lookups, extracting named log fields, fixed-format tables, known-output checks, fully specified approved launches and killing listed PIDs. (2026-10-14) |
| hard | Claude Opus 5.5, effort `medium` (a Claude subagent: model `opus`, effort `medium`) | Resolving an unsettled core algorithm or experiment design; adapting policy semantics; diagnosing a mismatch, hang or non-determinism whose cause remains unresolved after bounded evidence collection; implementing or verifying a change to byte-exact core behaviour under an explicit preservation requirement. User-owned decisions still follow I.10-I.11. (2026-10-14) |
| research | Codex (I.4 research worker, read-only) | Luna for a specified lookup or source summary; Sol medium for synthesis, assumption checks, alternatives, counterexamples and recommendations. Recommendations inform the decision owner; they do not approve a design. (2026-10-14) |

- **Choose by the work, not its label.** Task length, file count, the word "design", ordinary uncertainty or the
  possibility of asking a question do not justify Opus. A file in a core directory alone is not a byte-exact
  preservation requirement. If Luna and Sol overlap, choose Sol; if Sol and Opus overlap without an identified
  hard criterion, choose Sol. Record the selected criterion in the brief's *Resources*; an Opus brief names
  the unresolved question or the core behaviour and exactness requirement. (2026-10-14)
- **Sol may reason and implement.** It may inspect source, choose local structure and tests, diagnose an ordinary
  bug against expected behaviour, compare evidence, and recommend alternatives. It follows I.10-I.11 for
  unresolved semantic, result, scope or interface decisions: finish independent work and return the question.
  A question alone does not promote the task to Opus. (2026-10-14)
- **Split mixed work at the decision boundary.** Give Opus only the part meeting a hard criterion. Once the
  required decisions are settled, give ordinary implementation, approved launches, collection and reporting
  to Sol or Luna by their criteria above. Classify each independent part separately; an Opus parent does not
  make its helpers hard tier. Parallelism and ownership still follow I.15. (2026-10-14)
- **Escalate with evidence.** Luna returns substantive interpretation or diagnosis to its caller for a Sol
  task. Sol returns a concrete hard question with the evidence collected, hypotheses tested and the remaining
  blocker; the caller assigns only that part to Opus. Use existing logs and authorised checks first; extra
  simulator runs still require approval. The three-round review escalation in I.14 remains in force. (2026-10-14)
- **When Codex is unusable** (the Codex CLI fails on authentication or availability), give Sol-tier work to a
  Claude Sonnet subagent (`model: sonnet`, effort medium) and Luna-tier work to a Claude Haiku subagent
  (`model: haiku`), with the same brief, role rules and limits as the Codex worker it replaces. The hard tier
  stays Opus. Record the fallback and the Codex error in the brief's *Resources*. (user, 2026-10-14: "codex
  사용이 불가능한 경우 이전처럼 sonnet 이하를 사용하는 걸로") (2026-10-14)
- **Checks use Sol by default.** Builder checks and reader tests (I.12) use independent Codex Sol medium
  workers, including checks of Opus briefs. If a check exposes a hard question, report it to its owner rather
  than silently solving it or spawning Opus. Review model selection remains I.14. (2026-10-14)


## I.9 Handing over to the next session (2026-10-14)
<!-- general -->

A session ends when the user says so ("다음 세션에서 시작할게", "compact할게", "지금까지 내용을 정리해 둬"), or when
the master's context reaches about 256K tokens (I.2). Either way the master runs this procedure **before** the
context is lost. The user's request to move on is the trigger; the steps below are what it means. (2026-10-14)

**Procedure.** The steps are in the `handover` skill (`.claude/skills/handover/SKILL.md`): where the handover
goes, the steps, the next-session input template, and what a new session does first. Load it whenever the
trigger above fires; when only part of the work moves to another session, run it for that part. (2026-10-14)

## Master pitfalls (2026-10-14)
<!-- general -->

These are promoted pitfalls; a new pitfall is recorded first in the knowledge base (I.21). (2026-10-14)

- Answering a subagent's escalation by guessing instead of asking the user (I.11: no level guesses). (2026-10-14)
- Spawning without naming the rule files, so the subagent works from the auto-loaded `AGENTS.md` alone (I.12). (2026-10-14)
- Copying a decision into memory or a brief in new words instead of pointing to its row in the decisions list: the copies drift. (2026-10-14)
- Following a user rule that looks worse than an alternative without first proposing the alternative (I.11). (2026-10-14)
- Monitoring "when it occurs to you": a live job without a watch, or no heartbeat, is how runs went unnoticed
  (I.23). (2026-10-14)
- Applying a promotion candidate from the knowledge base without the user's approval (I.21). (2026-10-14)
