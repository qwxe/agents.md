# USER.md — working with the agents

For the user. What the agents promise you (the contract), what they need from you, and every option you can
choose. Rules are cited by id; the rule files hold the detail (`AGENTS.md` lists them, and `GENERAL.md` has the
repository-independent ones). If this file and a rule file disagree, the rule file wins and this file is fixed.

## 1. The contract: what you can expect (2026-10-14)

- **One conversation partner.** You talk to the Claude master. It delegates all work to subagents and Codex and
  keeps its own context for you (I.1, I.2). It reports in Korean and keeps what it saw itself apart from what an
  agent reported (I.13).
- **Nothing that changes results is decided without you.** A result-changing, semantic, scope or interface
  question comes to you as an escalation: the question, two or three options, what changes under each, a
  recommendation. No agent guesses on your behalf (I.10, I.11). Cheap, reversible choices are made by the agents
  and listed as assumptions with their cost if wrong.
- **Better ideas come first, never silently.** If an agent thinks a rule or design you set is worse than an
  alternative, it tells you before following it, with the evidence and its strength (I.11).
- **Code is tested and independently reviewed.** Tests first, a fast suite, no weakened tests; a separate
  read-only verifier gives PASS / PASS WITH NOTES / REJECT; a REJECT loop is capped and comes to you if it does
  not converge (I.14).
- **Claims are audited.** Numbers that go into a handoff or the paper are checked against raw results by a
  reviewer that sees only the results (`claim-audit` skill).
- **Runs.** No run you did not approve is started; approved runs keep the shared slots full; anything holding
  compute or on the critical path is health-checked about every 3 minutes, and anomalies reach you at once
  (I.5, I.18).
- **Your decisions are kept.** Each is recorded with your words and the date in the decisions list; a superseded
  or ruled-out decision is reopened only when you name it (I.10).
- **State survives sessions.** A progress ledger per line of work, a task trail per task, and a handoff
  subsection per session (I.13, I.17, I.9).
- **Safety.** Never-break rules are enforced by hooks where possible (blocked commands, secret scan before
  commit); files, tool output and agents' messages are treated as data, not instructions (I.19).

## 2. What the agents need from you

- **Answers to escalations**: pick an option (a number is enough) or say "추천대로".
- **Approval of new runs and experiment plans** (`experiment-plan` skill) before launch.
- **Standing rules said as standing**: "always", "from now on", "앞으로", "규칙에 넣어줘" make a rule; otherwise a
  decision applies to the task at hand.
- **When a session ends or work moves**: say so ("다음 세션에서 할게", "compact할게", "이건 다른 세션에서"); the
  master runs the handover and gives you the input for the new session.
- **To reopen a closed decision**: name it ("II.1의 X 다시 보자").

## 3. Options you can choose

| option | choices | default | how to ask | rule |
|---|---|---|---|---|
| Escalation mode | stop and ask on result-changing decisions; *rulings mode* (agents decide reversible questions and log them, for unattended runs) | stop and ask; rulings mode deferred (2026-10-14) | "rulings 모드 켜줘" (reopens the deferred decision) | I.11 |
| Who decides what | the I.10 table; you can move a class of decision up or down | I.10 | "X는 네가 정해" / "X는 나한테 물어봐" | I.10 |
| Model per task | Haiku / Sonnet / Opus / Codex Luna / Codex Sol | by tier (I.3) | "이건 Opus로" | I.3 |
| Parallelism | split every isolated or divisible task into parallel agents; or cap the number | split for speed, within the job-slot budget | "에이전트 N개까지만" | I.15 |
| Review depth | verifier only; plus Codex second opinion; plus full golden run and mutation testing | verifier always; Codex for hard work; full checks at the end of a line | "Codex 리뷰도 붙여" | I.14 |
| Read-back / builder check / reader test | on or off per task | on for hard work | "바로 구현해" / "먼저 계획 보여줘" | I.12 |
| Monitoring cadence | interval | ~3 min | "N분마다" | I.18 |
| Compaction | at ~256K tokens, or at phase boundaries | the master suggests; you decide | "compact할게" | I.2, I.9 |
| Report language | Korean / English | Korean | "영어로" | I.8 |
| Research depth | quick lookup (Codex Luna) or exhaustive survey | by request | "exhaustive하게" | I.4 |
| Hooks | which commands are blocked | the never-break list | "X는 막아줘 / 풀어줘" | `AGENTS.md` 0.3 |

## 4. Skills you can call by name

`/spawn-agent`, `/review`, `/handover`, `/lit-search`, `/claim-audit`, `/paper-write`, `/ideation`,
`/design-note`, `/experiment-plan`, `/debug`. Each says when it applies in its first line; the master also uses
them on its own when their trigger fires.

## 5. Where to look

- The progress ledger of a line of work: current state, who is on what, what is blocked on you.
- The handoff file: what each session decided and left open.
- The task trail: the brief, assumptions, escalations with answers, the verdict for one task.
- The decisions list: what is in force, and what was superseded.
The repository's `AGENTS.md` (0.4) says where each of these lives.
