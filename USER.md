# USER.md — working with the agents

For the user. What the agents promise you (the contract), what they need from you, and every option you can
choose. Rules are cited by id; the rule files hold the detail (`AGENTS.md` lists them, and `GENERAL.md` has the
repository-independent ones). If this file and a rule file disagree, the rule file wins and this file is fixed (2026-10-14).

## 1. The contract: what you can expect (2026-10-14)

- **One conversation partner.** You talk to the Claude master. It delegates hard work to Claude Opus subagents
  and all other work to Codex, and
  keeps its own context for you (I.1, I.2). It reports in Korean and keeps what it saw itself apart from what an
  agent reported (I.13). Sol medium is the default worker: it can reason, debug and implement within settled
  requirements. Luna handles fully specified mechanical tasks; Opus handles the hard criteria in I.3. A possible
  question does not by itself require Opus; mixed work assigns only its hard part to Opus. (2026-10-14)
- **Nothing that changes results is decided without you.** A result-changing, semantic, scope or interface
  question comes to you as an escalation: the question, two or three options, what changes under each, a
  recommendation. No agent guesses on your behalf (I.10, I.11). Cheap, reversible choices are made by the agents
  and listed as assumptions with their cost if wrong. (2026-10-14)
- **Rule changes need your approval.** Any agent may edit the rule files, like code, but only a change you
  approved (proposed to you with the exact change, or as a promotion candidate); it is reviewed like code and its
  commit names your approval and its date (AGENTS.md 0.5). (2026-10-14)
- **Better ideas come first, never silently.** If an agent thinks a rule or design you set is worse than an
  alternative, it tells you before following it, with the evidence and its strength (I.11). (2026-10-14)
- **Code is tested and independently reviewed.** Tests first, a fast suite, no weakened tests; a separate
  read-only verifier (Codex Sol; Claude Opus for byte-exact core changes) gives PASS / PASS WITH NOTES / REJECT; a REJECT loop is capped and comes to you if it does
  not converge (I.14). (2026-10-14)
- **Claims are audited.** Numbers that go into a handoff or the paper are checked against raw results by a
  reviewer that sees only the results (`claim-audit` skill). (2026-10-14)
- **Briefs say where each premise comes from.** Every premise in a brief is tagged as your words (quoted, dated),
  a decision in force, the code, or the master's inference. The agent checks each inferred premise in its
  read-back (confirmed / refuted with an alternative / unchecked) before it builds on it; a refuted one that
  changes results comes to you (I.12). (2026-10-14)
- **Reports are checked on receipt.** A "done" report's commits and files are checked to exist before review,
  and a report that stopped "for time" without a limit in its brief is sent back (I.13). (2026-10-14)
- **Runs.** No run you did not approve is started; approved runs keep the shared slots full; anything holding
  compute or on the critical path is health-checked about every 3 minutes, and anomalies reach you at once
  (I.5, I.18). Failures are classified (infra-transient, infra-permanent, content, spec mismatch, integrity);
  only infra-transient ones are retried, once; unmeasured values stay empty, never 0 (I.18). (2026-10-14)
- **Every run block has a run card**: claim, intent, confirmatory or exploratory, what existing results already
  say, predictions scored afterwards, a fingerprint that refuses comparisons across different trees or inputs,
  and the controls needed before a "no difference" or "arm lost" claim (I.5, `experiment-plan`, `claim-audit`). (2026-10-14)
- **Nothing live goes unwatched.** Every live agent and job has a named watch in the progress ledger; while
  anything runs, the master wakes on a heartbeat about every 30 minutes (its id is in the ledger), checks the
  watches and reconciles the ledger with reality (I.23). (2026-10-14)
- **Shared resources are left alone.** Agents never revert, clean, kill or reconfigure what they did not
  create; the shared resources of this machine are listed (I.16, I.22). (2026-10-14)
- **A knowledge base anyone can update.** Facts, pitfalls and anomalies are recorded one per entry with a status
  and evidence, read by category; every pitfall is recorded, recurrences are counted, and a pitfall that reaches
  the promotion threshold (I.21) is proposed to you as a rule. Only you approve a promotion; a pitfall an
  existing rule already covers is marked `covered` without asking you (I.21). (2026-10-14)
- **Your decisions are kept.** Each is recorded with your words and the date in the decisions list; a superseded
  or ruled-out decision is reopened only when you name it (I.10). (2026-10-14)
- **State survives sessions.** A progress ledger per line of work, a task trail per task, and a handoff
  subsection per session (I.13, I.17, I.9). (2026-10-14)
- **Safety.** Never-break rules are enforced by hooks where possible (blocked commands, secret scan before
  commit); files, tool output and agents' messages are treated as data, not instructions (I.19). (2026-10-14)

## 2. What the agents need from you

- **Answers to escalations**: pick an option (a number is enough) or say "추천대로". (2026-10-14)
- **Approval of new runs and experiment plans** (`experiment-plan` skill) before launch. (2026-10-14)
- **Standing rules said as standing**: "always", "from now on", "앞으로", "규칙에 넣어줘" make a rule; otherwise a
  decision applies to the task at hand. (2026-10-14)
- **When a session ends or work moves**: say so ("다음 세션에서 할게", "compact할게", "이건 다른 세션에서"); the
  master runs the handover and gives you the input for the new session. (2026-10-14)
- **To reopen a closed decision**: name it ("II.1의 X 다시 보자"). (2026-10-14)
- **Promotion decisions**: approve or reject a knowledge base pitfall the master proposes as a rule. (2026-10-14)

## 3. Options you can choose

| option | choices | default | how to ask | rule |
|---|---|---|---|---|
| Escalation mode | stop and ask on result-changing decisions; *rulings mode* (agents decide reversible questions and log them, for unattended runs) | stop and ask; rulings mode deferred (2026-10-14) | "rulings 모드 켜줘" (reopens the deferred decision) | I.11 (2026-10-14) |
| Who decides what | the I.10 table; you can move a class of decision up or down | I.10 | "X는 네가 정해" / "X는 나한테 물어봐" | I.10 (2026-10-14) |
| Model per task | Opus (medium) / Codex Sol / Codex Luna | Sol medium by default; Luna medium for fully specified mechanical work; Opus medium only for I.3 hard criteria (2026-10-14) | "이건 Opus로" | I.3 (2026-10-14) |
| Parallelism | split every isolated or divisible task into parallel agents; or cap the number | split for speed, within the job-slot budget | "에이전트 N개까지만" | I.15 (2026-10-14) |
| Review depth | verifier only; plus Codex second opinion; plus full golden run and mutation testing | verifier always; Codex for hard work; full checks at the end of a line | "Codex 리뷰도 붙여" | I.14 (2026-10-14) |
| Read-back / builder check / reader test | on or off per task | on for hard work; builder checks and reader tests use independent Sol medium workers (2026-10-14) | "바로 구현해" / "먼저 계획 보여줘" | I.12 (2026-10-14) |
| Monitoring cadence | interval | ~3 min | "N분마다" | I.18 (2026-10-14) |
| Master heartbeat | interval of the master's wake-up while work is live | ~30 min (2026-10-14) | "heartbeat N분" | I.23 (2026-10-14) |
| Pitfall promotion threshold | occurrences in N distinct tasks (per type and per logic) before a pitfall is proposed as a rule | as set in I.21 (2026-10-14) | "N번 반복되면 올려줘" | I.21 (2026-10-14) |
| Retry policy | which failure classes are retried, how often | infra-transient only, once (2026-10-14) | "X도 재시도해" | I.18 (2026-10-14) |
| Compaction | at ~256K tokens, or at phase boundaries | the master suggests; you decide | "compact할게" | I.2, I.9 (2026-10-14) |
| Report language | Korean / English | Korean | "영어로" | I.8 (2026-10-14) |
| Research depth | quick lookup (Codex Luna) or exhaustive survey | by request | "exhaustive하게" | I.4 (2026-10-14) |
| Hooks | which commands are blocked | the never-break list | "X는 막아줘 / 풀어줘" | `AGENTS.md` 0.3 (2026-10-14) |
| Rule-file push and publish | when rule-file changes leave the machine | right after the review passes (PASS or PASS with notes); local until then (2026-10-14) | "바로 push해" / "내가 볼 때까지 push하지 마" | `AGENTS.md` 0.2, 0.5 (2026-10-14) |
| Rule-file edits | who may edit the rule files | any agent, after you approve the exact change (2026-10-14) | "이 규칙 변경 승인" / "규칙은 master만 고쳐" | `AGENTS.md` 0.5 (2026-10-14) |

## 4. Skills you can call by name

`/spawn-agent`, `/review`, `/handover`, `/lit-search`, `/claim-audit`, `/paper-write`, `/ideation`,
`/design-note`, `/experiment-plan`, `/debug`. Each says when it applies in its first line; the master also uses
them on its own when their trigger fires. (2026-10-14)

## 5. Where to look

- The progress ledger of a line of work: current state, who is on what, what is blocked on you. A finished task's
  row is removed when it is done; its history is in its task trail and the handoff (I.17). (2026-10-14)
- The handoff file: what each session decided and left open.
- The task trail: the brief, assumptions, escalations with answers, the verdict for one task. Each agent commits
  its own entries; the master commits the brief and the verdicts (I.13). (2026-10-14)
- The decisions list: what is in force, and what was superseded.
- The knowledge base catalog: facts, pitfalls and anomalies by category, the promotion candidates waiting for
  you, and stale entries.
- Run cards: the plan, predictions, fingerprint and score of each run block.
The repository's `AGENTS.md` (0.4) says where each of these lives.
