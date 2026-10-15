---
name: spawn-agent
description: Spawn a Claude subagent or Codex worker with a correct brief. Use every time a master, manager or permitted worker delegates, including a depth-two Claude implementer spawning a depth-three Opus leaf (I.12, I.15).
---
<!-- general -->

# Spawning an agent (2026-10-15)

Approval: user, 2026-10-15: "좋아. 그렇게 바꿔줘."; steps 2, 6, 7, 8 and the background-launch rule: user, 2026-10-15: "4. 구현해줘." then "좋아. 그렇게 해줘. 1.2.3 전부 승인할게." (the decisions list); simple verification below Opus: user, 2026-10-15: "모든 verifier를 opus로 하는 규칙에서, 간단한 검증은 sonnet 이하로 하도록 고쳐줘." and the choice "기준이 명시된 검증 (Recommended)" (the decisions list); leaf role at depth three: user, 2026-10-15: "preflight를 넣을 필요 없어. leaf worker 등 agent를 스폰할 수 없는 역할의 markdown 파일을 새로 만들어." then chose "type + 역할 파일 (Recommended)" (the decisions list); verification on demand: user, 2026-10-15: "그리고 검증은 manager/agent 등 상위 계층이 내리는데, 검증이 필요한지 판단해서 필요 없으면 하지 않아도 되는걸로." then chose "큰 변경만 필수 (Recommended)" (the decisions list).

1. **Pick tier, role and model** using I.3 before delegating (the master hands general work to a manager); record the selected criterion in *Resources*. Use I.12 for custom agent types and I.4 for Codex invocation/flags. (2026-10-15)
2. **Identify and track the assignment.** Give it a task id `T<YYYYMMDD>-<slug>`. The master creates a
   `queued` direct-item row in F-ledger under I.17; every non-master caller, including a manager, creates
   a `queued` F-helper record in its own task trail. Record the artifact/decision/report owners and planned
   completion watch under I.12/I.18 before launch. Only the master writes the progress ledger or owns its
   I.23 heartbeat; non-master callers never create either on its behalf. (2026-10-15)
3. **Write the brief** in F-brief (I.24) with all I.12 requirements (provenance tags, rule-source commit, actual and maximum depth); read I.12 before writing it. Commit the brief under I.13's ownership rules, then send its path, never pasted earlier conversation. (2026-10-15)
4. **Parallel work:** follow I.15 before launching shared work. (2026-10-15)
5. **Hard-tier work:** execute I.12's design/builder/reader/read-back gates before code; record premise answers in the task trail. Batch small same-shaped tasks only within I.12's batching limit. (2026-10-15)
6. **Codex briefs.** Name the research-worker or task-worker role, "Codex's own rules", answer language,
   rule-source commit, tree, sandbox (I.4) and explicitly ordered launches, kills, commits and pushes.
   Name the role's disk startup row/card and required rule files; retain the research worker's limited
   reading scope. Copy the complete never-break section verbatim from the named rule-source commit,
   including heading, provenance and explanations, and check exact equality before launch. A research
   worker never edits, commits, launches jobs or spawns agents. A task worker spawns no agents and acts
   only within its explicit scope. Verification of another agent's result is an independent Opus
   assignment under I.14, never a Codex role; simple verification (I.14) is the exception to both. Record the actual hierarchy depth and ownership using
   F-brief; startup freshness checks remain mandatory. (2026-10-15)
7. **Launch and arm the watch.** Apply the background-launch rule and I.11 transport checks before launch.
   Establish the authorized watch mechanism and expected artifact/checkpoint under I.18; the master records
   the planned watch in F-ledger and arms its I.23 heartbeat, while a non-master caller records the watch in
   F-helper in its own trail. Immediately after the launch returns a real agent id or PID, record it and
   set that item to `running`. Failure before an id is a failed launch, never a fictitious running watch.
   The caller alone monitors the direct item it launched; it does not take over that item's jobs.
   (2026-10-15)

**Background launch.** Spawn every manager and Claude job/worker launcher as a background subagent
(`run_in_background: true`), including a permitted nested launcher.
Launch any other agent in the background unless the next step needs its result.
The fallback transport for mid-run messages when SendMessage is unavailable is the launcher channel file
(I.8), written only within brief-authorized output
scope and polled by the direct caller's child watch about every 180 seconds and read on every wake.
Its watch signals new packets to the caller, which relays escalation/anomaly/result packets and keeps job
health monitoring with the launcher. Validate fallback write/detection/relay in the same background mode
before launch; a missing output permission or caller watch blocks dependent launch. (2026-10-15)

8. **Handle reports and escalation.** On a terminal report first perform I.13 receipt checks and then its
   status-word action; read the full report only as far as needed. The master updates its direct F-ledger
   row; every non-master caller updates F-helper in its own task trail, and a manager also updates F-unit.
   Only the master relays to the user, separating direct observations from reported findings; managers and
   other workers report upward to their caller. Deliver mid-run escalations immediately under I.11 without
   waiting for a terminal report. Route authorized answers through the caller chain with decider, dated
   words, source and action bounds: Claude resumes the same agent by SendMessage; Codex receives a new call.
   Send completed results requiring verification (I.14 *Verification on demand*) to the review or matching audit skill under I.14; do not
   accept them yourself. Close tracking only after receipt and required review; clean only authorized own
   resources and retain launcher-exclusive monitoring until terminal receipt. (2026-10-15)
