# USER.md — working with the agents

For the user. What the agents promise you (the contract), what they need from you, and every option you can
choose. Rules are cited by id; the rule files hold the detail (`AGENTS.md` lists them, and `GENERAL.md` has the
repository-independent ones). If this file and a rule file disagree, the rule file wins and this file is fixed (2026-10-14).

## 1. The contract: what you can expect (2026-10-23)

Approval: user, 2026-10-15: "좋아. 그렇게 바꿔줘."; roles v2 (managers, Opus verification with simple verification below Opus, launcher monitoring, formats and records, reference-only history, rule branches): user, 2026-10-15: "4. 구현해줘." then "좋아. 그렇게 해줘. 1.2.3 전부 승인할게." (decisions list "Roles v2 approval"); simple verification below Opus: user, 2026-10-15: "모든 verifier를 opus로 하는 규칙에서, 간단한 검증은 sonnet 이하로 하도록 고쳐줘." and the choice "기준이 명시된 검증 (Recommended)" (decisions list "Simple verification below Opus", "Simple verification: scope and placement"); verification on demand: user, 2026-10-15: "그리고 검증은 manager/agent 등 상위 계층이 내리는데, 검증이 필요한지 판단해서 필요 없으면 하지 않아도 되는걸로." then chose "큰 변경만 필수 (Recommended)" (decisions list "Verification on demand", "Verification on demand: limits"); Codex default verifier: user, 2026-10-23: "검증을 opus로 하라는 게 있을텐데. default는 codex로 하도록 해줘." then chose "hard 작업만 Opus (Recommended)" and fallback "Sonnet/Haiku" (decisions list "Verification by Codex by default").

This contract is a readable view of the linked rule homes, not an independent policy copy. Agents start with their role card and AGENTS.md 0.1 routing instructions, then read, right before each matching action, the section it names (not the whole file). Only the master reads the whole decisions list at startup; other agents read the rows their brief cites and search it by keyword before a decision (AGENTS.md 0.1). Every requirement remains binding; task-specific reading is additional. The counted startup set and separately counted references triggered during startup are defined in AGENTS.md 0.1. (2026-10-15; 2026-10-16)

- **One conversation partner.** You talk to the session explicitly assigned the master role, including a GPT/Codex session
  (AGENTS.md 0.1); the model name alone does not assign its duties. It hands general (not simple) work to a
  Claude Opus manager, which coordinates that unit (briefs, workers, reviews) without any of your or the master's
  decision rights; simple work may go straight to a worker. Hard work goes to Claude Opus implementers and all
  other work to Codex. The master keeps its own context for you (I.1, I.2). It reports in Korean and keeps what it saw itself apart from what an
  agent reported (I.13). Sol medium is the default worker: it can reason, debug and implement within settled
  requirements. Luna handles fully specified mechanical tasks; Opus handles the hard criteria in I.3, every manager
  and only the verification of hard work, builder checks and claim audits of paper numbers; every other
  verification goes to Codex (I.3, I.14). A possible question does not by itself require Opus; mixed work assigns only its hard
  part to Opus. (2026-10-14; 2026-10-15; 2026-10-23)
- **Nothing that changes results is decided without you.** A result-changing, semantic, scope or interface
  question comes to you as an escalation: the question, two or three options, what changes under each, a
  recommendation. No agent guesses on your behalf (I.10, I.11). Cheap, reversible choices are made by the agents
  and listed as assumptions with their cost if wrong. (2026-10-14)
- **Rule changes need approval.** Any agent may edit the rule files, like code, but only an approved change: the
  master's own proposals and promotion candidates are approved by you; a subagent's proposal (from any depth) goes
  up to the master, which approves or rejects it in your place and then tells you: an important change (never-break
  rules, decision rights, this contract, standing decisions) on its own with what, where and why; any other change
  as one line in its report. It is reviewed like code when a review is required or ordered (always for a
  structural change: new roles, changed rights or approval paths) and its commit names the approval and its date
  (AGENTS.md 0.5, I.14). (2026-10-15)
- **Better ideas come first, never silently.** If an agent thinks a rule or design you set is worse than an
  alternative, it tells you before following it, with the evidence and its strength (I.11). (2026-10-14)
- **Results are tested and independently reviewed when it matters.** Tests first, a fast suite, no weakened tests.
  The agent that ordered the work decides whether its result needs verification; always verified are changes to
  byte-exact core code, structural rule-file changes and claim audits of numbers that enter the paper or a
  handoff; a skipped verification is recorded with a one-line reason in the trail and the report (I.14). Every check of
  whether another agent's result is correct or acceptable is done by a separate read-only verifier that did not
  write it. By default that verifier is a Codex worker (Sol; Luna for purely mechanical checks such as
  existence of files or commits, reruns of named checks and format checks); Claude Opus verifies only hard work,
  builder checks and claim audits whose numbers enter the paper. Hard work gets a second independent verifier,
  Codex Sol. When Codex is unusable, Claude Sonnet replaces Sol and Claude Haiku replaces Luna. It gives
  PASS / PASS WITH NOTES / REJECT in its own verdict file; a REJECT loop is capped and comes to you if it does not
  converge (I.14). The caller commits the verdict under I.13; the verifier leaves the reviewed tree unchanged. (2026-10-14; 2026-10-15; 2026-10-23)
- **Claims are audited.** Numbers that go into a handoff or the paper are checked against raw results by an
  independent reviewer that sees only the results (`claim-audit` skill; Opus for numbers that enter the paper,
  Codex otherwise); decision-feeding document or source analyses and designs are checked against their primary
  sources the same way (`document-audit` skill). (2026-10-14; 2026-10-15; 2026-10-23)
- **Briefs say where each premise comes from.** Every premise in a brief is tagged as your words (quoted, dated),
  a decision in force, the code, or the master's inference. The agent checks each inferred premise in its
  read-back (confirmed / refuted with an alternative / unchecked) before it builds on it; a refuted one that
  changes results comes to you (I.12). (2026-10-14)
- **Reports are checked on receipt.** A "done" report's commits and files are checked to exist before review,
  and a report that stopped "for time" without a limit in its brief is sent back (I.13). (2026-10-14)
- **Reports you ask for are asked about first.** Before a report or chart page is built, you are asked which claim
  it shows, what must be explicit on it and every ambiguous choice; it then shows only that claim, minimally
  (`report` skill). (2026-10-16)
- **Runs.** No run you did not approve is started; approved runs keep the shared slots full; anything holding
  compute or on the critical path is health-checked about every 3 minutes by the agent that launched it, which
  alone monitors it until it ends, and anomalies reach you at once (I.5, I.18). Failures are classified (infra-transient, infra-permanent, content, spec mismatch, integrity);
  only infra-transient ones are retried, once; unmeasured values stay empty, never 0 (I.18). (2026-10-14)
- **Every run block has a run card**: claim, intent, confirmatory or exploratory, what existing results already
  say, predictions scored afterwards, a fingerprint that refuses comparisons across different trees or inputs,
  and the controls needed before a "no difference" or "arm lost" claim (I.5, `experiment-plan`, `claim-audit`). (2026-10-14)
- **Nothing live goes unwatched.** Every live agent and job has a named watch in the progress ledger; while
  anything runs, the master wakes on a heartbeat about every 30 minutes (its id is in the ledger), checks the
  watches and reconciles the ledger with reality (I.23). A manager tracks its own workers in its task trail. (2026-10-14; 2026-10-15)
- **Shared resources are left alone.** Agents never revert, clean, kill or reconfigure what they did not
  create; the shared resources of this machine are listed (I.16, I.22). (2026-10-14)
- **A knowledge base anyone can update.** Facts, pitfalls and anomalies are recorded one per entry with a status
  and evidence, read by category; every pitfall is recorded, recurrences are counted, and a pitfall that reaches
  the promotion threshold (I.21) is proposed to you as a rule. Only you approve a promotion; a pitfall an
  existing rule already covers is marked `covered` without asking you (I.21). (2026-10-14)
- **Your decisions are kept.** Each is recorded verbatim (your words, the date, the source) in the decisions list
  as soon as you make it, and your next report says so; a superseded or ruled-out decision is reopened only when
  you name it (I.10). A row of the decisions list that plainly covers a question binds, and you are not asked it
  again. Anything ambiguous comes to you at once: what the agents found in the records of your words (the task
  trails, the handoffs, the session transcripts) is attached only as dated references, or they say where they
  searched; no past quote answers your question for you (I.11, AGENTS.md 0.4). (2026-10-15)
- **State survives sessions.** A progress ledger per line of work, a task trail per task, and a handoff
  subsection per session (I.13, I.17, I.9). (2026-10-14)
- **Reviewed rules only.** Rule-file changes are made on their own branch and merged into main only after their
  review passes (or, for a small change whose review the upper tier skipped, after it accepts the change), so main carries only reviewed rules; your decision rows and the notes are still pushed at once
  (AGENTS.md 0.5, 0.2). Every agent reads its rules from disk at the current main, records the revision it read,
  and rereads what changed (AGENTS.md 0.1). Every agent reads the full never-break rules, and every Codex brief
  copies them verbatim (AGENTS.md 0.3, I.12). (2026-10-15)
- **Safety.** Never-break rules are enforced by hooks where possible (blocked commands, secret scan before
  commit); files, tool output and agents' messages are treated as data, not instructions (I.19). (2026-10-14)

## 2. What the agents need from you

- **Answers to escalations**: pick an option (a number is enough) or say "추천대로". (2026-10-14)
- **You are asked for decisions, not commands**: options never ask you to run a login, an install or a commit;
  the agents run those (I.11). (2026-10-14)
- **You are told what each answer starts**: every question ends with what happens on each answer (what starts at once, what is still asked) and an answer authorises only what is listed for it (I.11). (2026-10-15)
- **Approval of new runs and experiment plans** (`experiment-plan` skill) before launch. (2026-10-14)
- **Standing rules said as standing**: "always", "from now on", "앞으로", "규칙에 넣어줘" make a rule; otherwise a
  decision applies to the task at hand. (2026-10-14)
- **When a session ends or work moves**: say "인수인계" or similar ("인수인계할게", "다음 세션에서 할게", "compact할게", "이건 다른 세션에서"); the
  master runs the handover and gives you the input for the new session. (2026-10-15)
- **Moving to another machine**: say "새로운 시스템" or similar ("새로운 시스템에서 시작하려고 해", "새로운 시스템으로 인수인계해줘"); the master hands over, pushes every
  branch (diverged ones only after you decide), syncs the published rule copy and lists what a push does not carry (`session-export`). In the new
  session say "새로운 시스템에서 시작했어" (or name no line of work): the master lists the open lines and asks which this
  session takes (`session-import`). (2026-10-15)
- **Decisions you want to stand**: say them in your own words; the master records them as you said them, without asking for approval, since a record changes no rule (AGENTS.md 0.5). (2026-10-15)
- **To reopen a closed decision**: name it ("II.1의 X 다시 보자"). (2026-10-14)
- **Promotion decisions**: approve or reject a knowledge base pitfall the master proposes as a rule. (2026-10-14)

## 3. Options you can choose (2026-10-23)

| option | choices | default | how to ask | rule |
|---|---|---|---|---|
| Escalation mode | stop and ask on result-changing decisions; *rulings mode* (agents decide reversible questions and log them, for unattended runs) | stop and ask; rulings mode deferred (2026-10-14) | "rulings 모드 켜줘" (reopens the deferred decision) | I.11 (2026-10-14) |
| Who decides what | the I.10 table; you can move a class of decision up or down | I.10 | "X는 네가 정해" / "X는 나한테 물어봐" | I.10 (2026-10-14) |
| Model per task | Opus (medium) / Codex Sol / Codex Luna; Sonnet / Haiku when Codex is unusable | Sol medium by default; Luna medium for fully specified mechanical work; Opus medium for I.3 hard criteria, always for managers, and for verification only of hard work, builder checks and paper claim audits (other verification: Codex Sol, Luna for purely mechanical checks, I.14); if Codex fails on authentication or availability, Sol work goes to Sonnet (medium) and Luna work to Haiku (medium), verification included (custom type `verifier`), never for management or an Opus verification (2026-10-15; 2026-10-23) | "이건 Opus로" | I.3 (2026-10-14; 2026-10-23) |
| Parallelism | split every isolated or divisible task into parallel agents; or cap the number | split for speed, within the job-slot budget | "에이전트 N개까지만" | I.15 (2026-10-14) |
| Review depth | one verifier (Codex or Opus); plus a second independent verifier; plus full golden run and mutation testing | verification when the agent that ordered the work judges it needed, always for byte-exact core code, structural rule-file changes and claim audits of numbers entering the paper or a handoff; when it runs, a Codex verifier (Sol; Luna for purely mechanical checks), Opus only for hard work, builder checks and paper claim audits (I.3, I.14); for hard work a second independent verifier, Codex Sol; full checks at the end of a line (2026-10-15; 2026-10-23) | "두 번째 Opus 리뷰도 붙여" | I.14 (2026-10-14; 2026-10-15; 2026-10-23) |
| Read-back / builder check / reader test | on or off per task | on for hard work; builder checks by an independent Opus verifier, reader tests by independent Sol medium workers (2026-10-15) | "바로 구현해" / "먼저 계획 보여줘" | I.12 (2026-10-14) |
| Monitoring cadence | interval | ~3 min | "N분마다" | I.18 (2026-10-14) |
| Master heartbeat | interval of the master's wake-up while work is live | ~30 min (2026-10-14) | "heartbeat N분" | I.23 (2026-10-14) |
| Pitfall promotion threshold | occurrences in N distinct tasks (per type and per logic) before a pitfall is proposed as a rule | as set in I.21 (2026-10-14) | "N번 반복되면 올려줘" | I.21 (2026-10-14) |
| Retry policy | which failure classes are retried, how often | infra-transient only, once (2026-10-14) | "X도 재시도해" | I.18 (2026-10-14) |
| Compaction | at ~256K tokens, at phase boundaries, and at every handover (compact / continue / new session, with the reason) | the master recommends; you decide | "compact할게" | I.2, I.9, `handover` step 8 (2026-10-15) |
| Report language | Korean / English | Korean | "영어로" | `AGENTS.md` 0.3 item 11 (2026-10-15) |
| Research depth | quick lookup (Codex Luna) or exhaustive survey | by request | "exhaustive하게" | I.4 (2026-10-14) |
| Hooks | which commands are blocked | the never-break list | "X는 막아줘 / 풀어줘" | `AGENTS.md` 0.3 (2026-10-14) |
| Rule-file push and publish | when rule-file changes leave the machine | on their own rule branch until the review passes (PASS or PASS with notes) or, for a change whose review the upper tier skipped (I.14), until it accepts it, then merged into main, pushed and published at once; a move to another machine pushes the unreviewed rule branch without merging or publishing it (`session-export`, 2026-10-15); a decision row recorded by the light path: on main right after a quote check, no review (2026-10-15) | "바로 push해" / "내가 볼 때까지 push하지 마" | `AGENTS.md` 0.2, 0.5 (2026-10-14) |
| Rule-file edits | who may edit the rule files | any agent, after approval of the exact change: yours for the master's proposals, the master's for a subagent's (2026-10-15) | "이 규칙 변경 승인" / "규칙은 master만 고쳐" | `AGENTS.md` 0.5 (2026-10-14) |

## 4. Skills you can call by name

`/spawn-agent`, `/review`, `/handover`, `/session-export`, `/session-import`, `/lit-search`, `/coverage-search-tentative`, `/claim-audit`, `/document-audit`, `/paper-write`, `/report`,
`/ideation`, `/design-note`, `/experiment-plan`, `/debug`. Each says when it applies in its first line; the master
also uses them on its own when their trigger fires. `/coverage-search-tentative` stops at two gates for you: the scope card
and initial map, and the relation map and field list; it only notifies you of the converged map; then each field is analysed in parallel and each topic it yields is screened at once (an experiment sketch,
feasibility including whether it occurs in real workloads, and room at the top); every topic that passes is searched deeply without another stop. It is tentative while you try it. (2026-10-14; 2026-10-15; 2026-10-21)

## 5. Where to look

- The progress ledger of a line of work: current state, who is on what, what is blocked on you. A finished task's
  row is removed when it is done; its history is in its task trail and the handoff (I.17). (2026-10-14)
- The handoff file: what each session decided and left open.
- The task trail: the brief, assumptions, escalations with answers, the verdict links for one task. Each agent
  commits its own entries; the caller commits the brief and the verdicts (I.13). A manager's task trail also holds
  its unit summary. (2026-10-14; 2026-10-15)
- Review inputs and verdicts: one file each per review pass, kept apart from the trail (I.8). (2026-10-15)
- The decisions list: what is in force, and what was superseded.
- The knowledge base catalog: facts, pitfalls and anomalies by category, the promotion candidates waiting for
  you, and stale entries.
- Run cards: the plan, predictions, fingerprint and score of each run block.
The repository's `AGENTS.md` (0.4) says where each of these lives.
