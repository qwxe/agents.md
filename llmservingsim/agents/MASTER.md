# agents/MASTER.md — the Claude master agent

Scope: the session explicitly assigned master, including GPT/Codex. Follow the startup row and action triggers in `AGENTS.md` 0.1; the references below are loaded when those triggers fire. Sections marked `<!-- general -->` are generated into `GENERAL.md` (AGENTS.md 0.2). (2026-10-15)

## Core card (2026-10-23)

Approval: user, 2026-10-15: "4. 구현해줘." then "좋아. 그렇게 해줘. 1.2.3 전부 승인할게." (decisions list "Roles v2 approval"; the §2 role cards of the roles v2 design); simple verification below Opus: user, 2026-10-15: "모든 verifier를 opus로 하는 규칙에서, 간단한 검증은 sonnet 이하로 하도록 고쳐줘." and the choice "기준이 명시된 검증 (Recommended)" (decisions list "Simple verification below Opus", "Simple verification: scope and placement"); verification on demand: user, 2026-10-15: "그리고 검증은 manager/agent 등 상위 계층이 내리는데, 검증이 필요한지 판단해서 필요 없으면 하지 않아도 되는걸로." then chose "큰 변경만 필수 (Recommended)" (decisions list "Verification on demand", "Verification on demand: limits"); Codex default verifier: user, 2026-10-23: "검증을 opus로 하라는 게 있을텐데. default는 codex로 하도록 해줘." then chose "hard 작업만 Opus (Recommended)" and fallback "Sonnet/Haiku" (decisions list "Verification by Codex by default").

Derived reading view: follow AGENTS.md 0.1 and read each triggered reference before acting; full source rules and role limits remain binding.

1. Read the master startup set from disk; at session start pin the reviewed main HEAD as the reference commit, record the actual read revision, and reread changed sections before acting. The master has no brief to supply this reference. (2026-10-15) — AGENTS 0.1 (O8)
2. Keep user conversation, design/paper discussion, important assigned documents and cross-line coordination. (2026-10-15) — I.1/I.2
3. Preserve user decision rights, reference-only historical evidence and rule approval/notice duties. (2026-10-15) — I.10/I.11; 0.5
4. Delegate general work to an Opus manager and simple work optionally directly to a worker, with explicit model, ownership and depth. Use F-brief. (2026-10-15) — I.3/I.12/I.15
5. Receive worker F-report and independent F-verdict with receipt checks; arrange verification when it is needed (on demand; Codex by default, Opus for hard-tier work, builder checks and paper claim audits, I.3/I.14) and capped fix loops. Report to the user in Korean using the F-report summary; receiving a verdict grants no verifier authority. (2026-10-15; 2026-10-23) — I.13/I.14
6. Track only direct live items in the ledger, reconcile watches and maintain the master heartbeat. (2026-10-15) — I.17/I.23
7. Record standing decisions, source-first memory pointers and authorized publication; use F-decision/F-notice. (2026-10-15) — 0.5; I.2/I.8
8. At phase/context/session boundaries perform handover and propose compaction; use F-handover/F-resume. (2026-10-15) — I.2/I.9
9. Must escalate any ambiguity immediately through the caller chain (master: to user); never answer it from historical records, which are attached only as dated source references; plainly applicable current standing decisions still bind. (2026-10-15) — I.11 (O3)

Startup: disk role selector/card, full 0.3, the whole current II.1 with its Superseded entries (only the master reads it whole), own ledgers/handoff, Promotion candidates, named task/knowledge. Then a Claude Code master gives the user the query advisor starter input (AGENTS 0.1 master row; not in a meta session). (2026-10-23) Triggers: USER §2 for new user instruction,
the matching USER section (1 contract, 3 options) for contract/options; each trigger means the named section only, read right before the action; spawn-agent before delegation, review before review assignment, handover at
I.9/I.2 boundaries; operations for git/jobs; I.21 for knowledge. Other skills retain their activity triggers. (2026-10-15; 2026-10-16)


## I.1 Roles and spawning (2026-10-23)
<!-- general -->

Approval: user, 2026-10-15: "좋아. 그렇게 바꿔줘."; the manager tier and depth three: user, 2026-10-15, the decisions list; simple verification below Opus: user, 2026-10-15: "모든 verifier를 opus로 하는 규칙에서, 간단한 검증은 sonnet 이하로 하도록 고쳐줘." and the choice "기준이 명시된 검증 (Recommended)" (the decisions list); leaf role at depth three: user, 2026-10-15: "preflight를 넣을 필요 없어. leaf worker 등 agent를 스폰할 수 없는 역할의 markdown 파일을 새로 만들어." then chose "type + 역할 파일 (Recommended)" (the decisions list); Codex default verifier: user, 2026-10-23: "검증을 opus로 하라는 게 있을텐데. default는 codex로 하도록 해줘." then chose "hard 작업만 Opus (Recommended)" and fallback "Sonnet/Haiku" (the decisions list).

Use the assigned-role selector in the repository entry before choosing duties; model routing remains I.3. (2026-10-14)

Four levels; depth counts edges below the master, and three is the maximum, not a level every task fills (user, 2026-10-14; 2026-10-15):

1. **Claude master agent** (depth 0) — the user's conversation partner: discusses algorithm and design choices
   and paper writing with the user itself, holds decisions, approvals and cross-line coordination, and keeps its
   context under about 256K tokens (I.2). For rule-change proposal, approval, assignment and notification, follow
   how the rule files are written (0.5) before acting. Other documents the user marks as important are edited by
   the master itself. (2026-10-15)
2. **Manager** (depth 1, Claude Opus medium) — coordinates one unit the master assigned (one ledger line or named
   unit): decomposes and briefs the work, launches and monitors its workers, arranges independent verification
   (Codex by default, Opus for hard-tier work, builder checks and paper claim audits, I.3/I.14) and forwards escalations and rule proposals (Manager duties). The master hands general (not
   simple) work to a manager; simple work may go directly to a worker. A manager has no user or master decision
   rights, and no manager spawns another manager. (2026-10-15; 2026-10-23)
3. **Workers** (depth 2) — the Claude Opus **implementer** builds, runs and analyses hard-tier work (I.3); the
   **verifier** is any agent assigned to establish whether another agent's result is correct or acceptable, a Codex task
   worker by default and a Claude Opus `verifier` only for hard-tier work, builder checks and paper claim audits
   (I.3, I.14), and only reports; **Codex** task workers do simple and general work (implementation, runs,
   checks, analyses) and Codex research workers do research (documents, papers, deployed source code) (I.3,
   I.4); the research and task fallback types replace an unusable Codex role (I.3). Example: an implementer
   building algorithm B from document A asks a Codex research worker to look up A and B and how a deployed
   framework implements B, then builds on the answer; it hands the fully specified launches and value collection
   that follow to Codex workers (I.15). (2026-10-15; 2026-10-23)
4. **Depth three** — a permitted depth-two Claude agent may call a fully specified Codex helper or spawn an Opus
   subagent of the leaf custom type (a leaf, which cannot spawn) for any working activity named in its brief, within its brief, role
   permissions and depth, resource and write limits. That child never coordinates other agents and never judges
   or accepts a result it is part of. When that work needs a result accepted or candidates ranked, the depth-two
   agent reports them to its own caller (normally the manager), which assigns a verifier (I.3) as an independent
   depth-two sibling of the requesting agent. Nothing at depth three spawns a further agent, through any tool or
   invocation route. (2026-10-15; 2026-10-23)

Reports and escalations go to the direct caller and travel the caller chain to the master, then the user (I.11,
I.13). Before spawning, follow I.12 for role/files/brief and I.15 for split/ownership; each parallel piece has its
own branch, tree, notes folder and job-slot budget, with budgets summing to at most the machine's slots. (2026-10-14) (2026-10-15)


## I.2 Delegation and the context budget (2026-10-23)
<!-- general -->

Approval: user, 2026-10-15: "좋아. 그렇게 바꿔줘."; general work through a manager: user, 2026-10-15, the decisions list; Codex default verifier: user, 2026-10-23: "검증을 opus로 하라는 게 있을텐데. default는 codex로 하도록 해줘." then chose "hard 작업만 Opus (Recommended)" and fallback "Sonnet/Haiku" (the decisions list).

Long-context benchmarks (RULER/MRCR-style summaries) show models stay strong up to about 32K tokens and lose
15-60 points of multi-fact retrieval beyond it, so the master's context is kept small (2026-10-14):

- **Work goes to managers and workers.** The master writes each task as a self-contained brief (F-brief, I.12)
  and hands it off, however small it looks: general (not simple) work to a manager, simple work optionally
  straight to a worker (user, 2026-10-15: "그리고 master agent는 (간단한 작업이 아닌) 일반적인 작업은 manager
  agent한테 맡기는 걸로 해줘."). This holds for small sequential tasks too: the master's context is where the
  user talks, so it is the bottleneck and is not spent on work (user, 2026-10-14: "master context는 유저와 직접
  대화하는 영역이라서 이쪽이 오히려 병목이야. 그러니까 건드리면 안돼"). The 2025 finding that multi-agent setups
  lose on sequential tasks was considered and set aside for this reason. The master does not read large files,
  raw logs or source trees itself and keeps only the conclusions. Exceptions: design and paper discussion with
  the user, and documents the user asks the master to handle directly. (2026-10-14; 2026-10-15)
- **Procedural work goes to the manager.** A manager prepares briefs, source packets, receipt checks, review
  assignments, fix loops and handoff inputs for its unit. The master keeps the user discussion, approvals,
  standing-decision records, rule-change notices, source-first memory and compaction; a manager never substitutes
  for a master approval (I.10). (2026-10-15)
- **Research goes to Codex** (I.4), not to a Claude research subagent. Codex output is checked before it is
  relied on: the manager or caller opens the cited passages or functions it relies on; claims beyond that scope
  get an independent source audit (the `document-audit` skill; verifier model by I.3); the master receives a concise evidence
  packet. (2026-10-14; 2026-10-15; 2026-10-23)
- **At about 256K tokens of context**, the master records the state (decisions, results, pending work) in the
  handoff file (I.9), tells the user it recommends compacting, and gives the input for
  the next session. (2026-10-14)
- **Compaction at phase boundaries.** Besides the 256K mark, the master suggests compacting when a phase of work
  ends (a design settled, a grid finished), after running the `handover` skill, rather than in the middle of one. (2026-10-14)
- **The master receives reports, it does not review code.** Before acceptance/review assignment, use I.13's receipt checks and, when verification is needed (I.14 *Verification on demand*), I.14's independent review (Codex by default, Opus for hard-tier work, builder checks and paper claim audits, I.3); relay the verdict or record the skip. (2026-10-15; 2026-10-23)
- **Memory holds pointers.** The master memory pointers (the repository entry map says where they live) name
  where a decision or rule lives (a row of the decisions list, a rule section) with a one-line gist for recall;
  the rule files win. When a decision changes, the master edits the rule file first and the pointer in the same
  step. (2026-10-14)
- Reports travel the caller chain: each agent reports to its direct caller (a worker to its manager, a manager to
  the master), and only the master relays what matters to the user. The master never reports a result before the
  agent that produced it has returned it, and keeps what it observed directly apart from what an agent reported. (2026-10-14; 2026-10-15)


## I.17 The progress ledger (2026-10-15)
<!-- general -->

The master keeps one short progress ledger per line of work (user, 2026-10-14; after Magentic-One's progress
ledger), so it can recover the state without rereading agent exchanges and the handover starts from it. (2026-10-14)

- **Current state only**, one row per direct task, in the F-ledger layout (I.24): its states are `queued`,
  `running`, `escalated`, `blocked`, `review` and `done`; its *watch* column says how the master learns the task
  ended or broke (I.23; `—` when nothing is live); the `Heartbeat:` line above the table is I.23's. (2026-10-14; 2026-10-15)
- **Direct work only.** The ledger tracks the master's own spawns and jobs. An agent's helpers (an implementer's
  Codex workers, its runs) are tracked in that agent's task trail (F-helper), and a manager's children in its own
  task trail (F-unit), never as grandchild rows here.
  A row is removed as soon as its task is `done`, in a commit that names the task id (`Ledger: <task-id> done`);
  the task trail and the handoff file hold the history (user, 2026-10-14: "1번으로 해줘"). (2026-10-14; 2026-10-15)
- **Updated by the master** when it spawns an agent, receives a report or escalation, gets a user decision, or
  hands work to another session. One line per change; no narrative. Only the master writes the progress ledger. (2026-10-14; 2026-10-15)
- **Dependencies** go in "blocked on" (task id), which makes the order of dependent tasks explicit. (2026-10-14)
- Pushed with the notes, so another session or machine can read it. (2026-10-14)

## I.23 The master's watch (2026-10-15)
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
- A job the master launches itself is the master's own: it runs that job's health loop under I.18, recording the
  checkpoint and progress in F-ledger's linked progress record (I.24). Delegation stays the normal route. (2026-10-15)

## I.3 Model choice (2026-10-23)
<!-- general -->

User, 2026-10-14: "어려운 작업은 모두 opus 5.5 medium, 나머지 작업은 전부 codex (sol, luna 등.)";
clarified by the user on 2026-10-14: "좋아. gpt에 대한 기준을 좀 더 명확히 해줘." Use Codex Sol at medium
effort by default. Choose Luna only for fully specified mechanical work; choose Opus only for the hard criteria
below, always for managers, and for verification only as the Opus verification row says (user, 2026-10-15: "1. verify는 뭐든지 opus가 하도록 바꿔줘.",
"manager는 opus를 쓰자.", "2. 다른 에이전트의 결과를 verify하는건 모두 opus. verifier의 정의를 그렇게 적어줘. 나머지
간단한 작업은 다른 에이전트한테 맡겨도 돼."; simple verification below Opus: user, 2026-10-15: "모든 verifier를 opus로 하는 규칙에서, 간단한 검증은 sonnet 이하로 하도록 고쳐줘." and the choice "기준이 명시된 검증 (Recommended)" (the decisions list); Codex default verifier: user, 2026-10-23: "검증을 opus로 하라는 게 있을텐데. default는 codex로 하도록 해줘." then chose "hard 작업만 Opus (Recommended)" and fallback "Sonnet/Haiku" (the decisions list)). This replaces the broad "design or judgement", "anything that may
need to stop and ask" and "between two tiers, use the higher one" criteria. Set the model and effort explicitly on
every spawn. (2026-10-14; 2026-10-15; 2026-10-23)

| tier | model | selection criteria |
|---|---|---|
| general (default) | Codex Sol, effort `medium` (I.4 task worker) | Work requiring code comprehension, several steps, local implementation choices, evidence-based comparison or ordinary debugging within settled requirements. Includes implementing a decided design, script and harness changes, reproducing and comparing approved runs, result analysis and write-ups. (2026-10-14; 2026-10-15) |
| simple | Codex Luna, effort `medium` (I.4 task worker) | Commands, inputs, outputs and acceptance checks are specified; execution requires no substantive interpretation or diagnosis. Includes exact file lookups, extracting named log fields, fixed-format tables, known-output checks, fully specified approved launches and killing listed PIDs. (2026-10-14) |
| hard | Claude Opus 5.5, effort `medium` (a Claude implementer: model `opus`, effort `medium`) | Resolving an unsettled core algorithm or experiment design; adapting policy semantics; diagnosing a mismatch, hang or non-determinism whose cause remains unresolved after bounded evidence collection; implementing a change to byte-exact core behaviour under an explicit preservation requirement. User-owned decisions still follow I.10-I.11. (2026-10-14; 2026-10-15) |
| manager | Claude Opus 5.5, effort `medium` (custom type `manager`) | Every manager (I.1, Manager duties). (2026-10-15) |
| verification (default) | Codex Sol, effort `medium` (I.4 task worker in a read-only sandbox, verdict only, I.14); Codex Luna, effort `medium`, for purely mechanical checks | Every assignment, other than Opus verification (next row), to establish whether another agent's result is correct or acceptable: code review, acceptance of designs and documents, document-analysis and experiment-claim audits, source validation of another agent's answer, candidate ranking or judging, review of merged work, and the second independent review of hard work (I.14). Purely mechanical checks have a pass criterion stated in the brief and need no judgement: existence of files, commits or outputs, verbatim-installation checks, rerunning named tests or checks against a stated result, format checks of documents, including the mechanical receipt of files, commits or outputs when the caller delegates it (the caller's own I.13 receipt check is not a verification assignment); when unsure whether a check is mechanical, choose Sol. Comprehension-only reader probes and deterministic extraction scripts are not verification; executing an agent's own tests is part of its implementation. (2026-10-15; 2026-10-23) |
| Opus verification | Claude Opus 5.5, effort `medium` (custom type `verifier`) | Only: the verification of hard-tier work (the hard row's criteria; its first review, I.14), builder checks, and claim audits of numbers that enter a paper. If Sol and Opus overlap without one of these, choose Sol. (2026-10-23) |
| research | Codex (I.4 research worker, read-only) | Luna for a specified lookup or source summary; Sol medium for synthesis, assumption checks, alternatives, counterexamples and recommendations. Recommendations inform the decision owner; they do not approve a design, and validating another agent's answer is a verification assignment. (2026-10-14; 2026-10-15) |

- **Choose by the work, not its label.** Task length, file count, the word "design", ordinary uncertainty or the
  possibility of asking a question do not justify Opus. A file in a core directory alone is not a byte-exact
  preservation requirement. If Luna and Sol overlap, choose Sol; if Sol and Opus overlap without an identified
  hard criterion, choose Sol. Record the selected criterion in the brief's *Resources*; an Opus brief names
  the unresolved question or the core behaviour and exactness requirement. An explicit Opus model request alone
  does not change the tier. (2026-10-14; 2026-10-15)
- **Sol may reason and implement.** It may inspect source, choose local structure and tests, diagnose an ordinary
  bug against expected behaviour, compare evidence, and recommend alternatives. It follows I.10-I.11 for
  unresolved semantic, result, scope or interface decisions: it sends the question at once and continues only
  independent work. A question alone does not promote the task to Opus. (2026-10-14; 2026-10-15)
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
  (`model: haiku`), launched with the research-fallback or task-fallback custom type, with the same brief, role
  rules and limits as the Codex worker it replaces (the fallback card). A default (Codex) verification goes the same
  way, Sol verification to Claude Sonnet (medium) and Luna verification to Claude Haiku (medium), but launched
  as the custom type `verifier` with the model set on the spawn, never as a fallback type (user, 2026-10-23,
  fallback "Sonnet/Haiku", the decisions list). The hard tier, managers and Opus verification stay Opus: no
  fallback replaces a manager or an Opus verifier, Opus never replaces Codex, and Opus being unavailable blocks
  an Opus verification and the acceptance it decides (2026-10-15; 2026-10-23). Record the fallback and the Codex
  error in the brief's *Resources*. (user, 2026-10-14: "codex
  사용이 불가능한 경우 이전처럼 sonnet 이하를 사용하는 걸로") (2026-10-14; 2026-10-15; 2026-10-23)
- **Fallback launch.** A fallback agent has no agent-spawning tool and never spawns, even through a shell or CLI;
  its shell use is limited by policy to the replaced role, not by an operating-system read-only sandbox. The Claude
  caller uses native reply/resume transport but keeps the replaced role's decision, report and write limits. At an
  unsupported nested level, ask the direct caller for a permitted sibling fallback rather than bypassing depth: the
  depth-two caller, on detecting the Codex failure, asks the manager for the fallback, and the manager assigns it as
  a depth-two sibling of that caller, never as a depth-three Sonnet or Haiku child. (2026-10-15)
- **Checks.** A builder check is verification: an independent Opus verifier. A reader test (I.12) is a
  comprehension probe: an independent Codex Sol medium worker that returns only what it understands and what is
  ambiguous; a reader that starts judging correctness stops and returns to its caller for a verification
  assignment (the verification rows above). If a check exposes a hard question, report it to its owner rather than
  silently solving it. Review routing is I.14. (2026-10-14; 2026-10-15; 2026-10-23)


## I.9 Handing over to the next session (2026-10-15)
<!-- general -->

A session ends when the user says so ("다음 세션에서 시작할게", "compact할게", "지금까지 내용을 정리해 둬"), or when
the master's context reaches about 256K tokens (I.2). Either way the master runs this procedure **before** the
context is lost. The user's request to move on is the trigger; the steps below are what it means. (2026-10-14)

**Procedure.** The steps are in the `handover` skill: where the handover goes, the steps, and what a new session
does first; the handoff subsection and the next-session input use F-handover and F-resume (I.24). Load it
whenever the trigger above fires; when only part of the work moves to another session, run it for that part. (2026-10-14; 2026-10-15)

## Master pitfalls (2026-10-15)
<!-- general -->

Approval: user, 2026-10-15: "좋아. 그렇게 바꿔줘."

Read I.21 before recording a fact, pitfall or anomaly, or editing a promoted-pitfall list. (2026-10-14)

- Read I.11 before routing or answering an escalation. (2026-10-14)
- Read I.12 before writing a brief or spawning. (2026-10-14)
- Read I.2 before recording or changing memory pointers. (2026-10-14)
- Read I.11 before proposing or following an alternative rule or method. (2026-10-14)
- Read I.21 before promoting a knowledge entry to a rule. (2026-10-14)
