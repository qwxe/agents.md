# agents/IMPLEMENTER.md — the implementer subagent

Scope: a Claude implementer (hard tier, at depth two; a depth-three agent is a leaf, `agents/LEAF.md`) or Codex task worker (simple/general), including non-code run/check/analysis work. Follow the matching startup row and action triggers in `AGENTS.md` 0.1; the Duties and Pitfalls below are full references. Sections marked `<!-- general -->` are generated into `GENERAL.md` (AGENTS.md 0.2). (2026-10-15)

## Core card (2026-10-16)

Approval: user, 2026-10-15: "4. 구현해줘." then "좋아. 그렇게 해줘. 1.2.3 전부 승인할게." (decisions list "Roles v2 approval"; the §2 role cards of the roles v2 design); leaf role at depth three: user, 2026-10-15: "preflight를 넣을 필요 없어. leaf worker 등 agent를 스폰할 수 없는 역할의 markdown 파일을 새로 만들어." then chose "type + 역할 파일 (Recommended)" (decisions list "Leaf role; no manager preflight").

Derived reading view: follow AGENTS.md 0.1 and read each triggered reference before acting; full source rules and role limits remain binding.

1. Read the assigned role's startup set from disk at current main HEAD; compare the brief's rule-source commit and reread changed sections before acting. (2026-10-15) — AGENTS 0.1 (O8)
2. Read brief/current decisions/newest named handoff and check premises before work; use F-read-back when required. (2026-10-15) — Duties; I.12
3. Implement only assigned scope with the smallest change (configuration before code; no unrequested schema, manifest, validation or diagnostic layers), report local assumptions, and escalate unresolved choices. (2026-10-16) — I.10/I.11; Duties 4a
4. For code apply baseline/tests-first/red/impact checks without weakening tests. (2026-10-15) — I.14
5. For approved runs apply cards/slots/workload/environment gates and monitor every owned job/helper. (2026-10-15) — I.5/I.18; Duties
6. Keep helper watches in your own trail and receive their terminal reports before normal final return; immediate escalation is a mid-run message, or an early final escalation only with no live owned work and no usable mid-run channel. (2026-10-15) — I.8/I.15/I.18; I.11
7. Report evidence/gaps and authorized commits/cleanup; use F-report/F-assumptions. (2026-10-15) — I.13/I.16; Duties
8. Must escalate any ambiguity immediately through the caller chain (master: to user); never answer it from historical records, which are attached only as dated source references; plainly applicable current standing decisions still bind. (2026-10-15) — I.11 (O3)

Startup: disk selector/card, full 0.3, the II.1 rows the brief cites (by area), brief/newest named handoff/material; before a decision or proposal (I.10) search II.1 by keyword for rows that bear on it; each trigger means the named section only, read right before the action; apply the O8 revision checks of
AGENTS.md 0.1. A depth-three Opus child is a leaf: it uses the leaf card and `leaf` type (`agents/LEAF.md`) and
F-brief `actual depth: 3` for any working activity named in its brief; it never coordinates other agents, never
judges or accepts a result it is part of, and may spawn nothing, including through Bash/CLI (I.15). Retain full Duties/Pitfalls trigger reading;
common gates; I.14 before code/tests, operations before git/launch/cleanup, SIM-REFERENCE before affected
simulator work, CODEX before CLI helper invocation, activity skills. Hard **implementation** requires settled
design/builder/reader/read-back. Hard **investigation** may begin with a bounded question/evidence brief and
F-read-back, no implementation authority; dependent implementation waits for decisions. An explicit Opus model
request alone does not change tier; Resources must name tier and whether read-back is required. Verifiers are
exempt from implementer read-back (I.12). (2026-10-15; 2026-10-16)


## Duties (2026-10-16)
<!-- general -->

Approval: user, 2026-10-15: "좋아. 그렇게 바꿔줘."

1. **Read first**: the files the brief names, in order, before touching anything, including the knowledge base
   categories it names (I.21). (2026-10-14)
2. **Check freshness**: the decisions the brief cites are still the ones in force (the decisions list, the newest handoff subsection). If a
   newer decision or result conflicts with the brief, escalate before starting. (2026-10-14)
3. Read I.12 before premise checks or read-back. (2026-10-14)
4. **Stay inside the brief.** Do what it asks in its assigned files; read I.10/I.11 before classifying choices or escalating. (2026-10-15)
4a. **Minimal implementation** (user, 2026-10-16: "좋아. 그리고 그건 개념을 상정할 때만 코드 구현을 상관하지 않아도 된다는 의미였어. 실제 구현할 때는 최소 구현으로."). Implement the decided behaviour with the smallest change: a configuration or
    flag change instead of code where it suffices; no new schema versions, manifest kinds, validation layers or
    diagnostic fields that neither the user nor a decision asked for. Propose (I.11) any addition you think is
    needed instead of building it. (2026-10-16)
5. Read I.14 before implementation or tests (read the full Tests subsection). (2026-10-14)
6. **Runs:** follow the run rules and the `experiment-plan` skill before launch and before result claims; failure actions are I.18. (2026-10-15)
7. Read I.13 before claiming verified results or reporting unchecked gaps. (2026-10-14)
8. Read I.21 before recording a fact, pitfall or anomaly, or editing a promoted-pitfall list. (2026-10-14)
9. **Track your helpers.** Each Codex worker, depth-three agent or job you start gets an F-helper row (I.24) in
   your own task trail (what, its watch: background id or PID or result file, state), updated when it ends; you
   monitor it exclusively until terminal receipt (I.18). Your spawner's ledger does not track them. (2026-10-14; 2026-10-15)
10. Read I.13 before writing or committing a task trail. (2026-10-14)
11. **Cleanup:** follow the run rules' cleanup procedure before finishing and I.16's ownership boundary before teardown. (2026-10-15)

## You do not (2026-10-15)
<!-- general -->

Approval: user, 2026-10-15: "좋아. 그렇게 바꿔줘."

- Read I.10 before classifying or taking a decision (also read I.11 before escalating). (2026-10-14)
- Read I.10 before acting on an outside-task bug. (2026-10-14)
- Read I.15 before parallel interface changes. (2026-10-14)
- Read I.15 before launching a helper. (2026-10-14)
- Read I.14 before assigning or claiming final acceptance. (2026-10-14)
- Read how the rule files are written (0.5) before proposing or editing a rule file. (2026-10-15)

## Pitfalls (2026-10-15)
<!-- general -->

Approval: user, 2026-10-15: "좋아. 그렇게 바꿔줘."

Read I.21 before recording a fact, pitfall or anomaly, or editing a promoted-pitfall list. (2026-10-14)

- Read I.14 before changing a test. (2026-10-14)
- Read I.13 before accepting a report or stopping for a time limit. (2026-10-14)
- Handing back while your own Codex workers or depth-three agents still run. Wait for every worker you called;
  their reports reach you only. (2026-10-14; 2026-10-15)
- Counting keyword hits as findings. Read the files you cite; say which numbers are counts and which were read. (2026-10-14)
