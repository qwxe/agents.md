---
name: spawn-agent
description: Spawn a Claude subagent or a Codex worker with a correct brief. Use every time the master (or an implementer calling a Codex worker) delegates a task (AGENTS I.12, I.15).
---
<!-- general -->

# Spawning an agent (2026-10-15)

Approval: user, 2026-10-15: "좋아. 그렇게 바꿔줘."

1. **Pick tier, role and model** using I.3 before delegating; record the selected criterion in *Resources*. Use I.12 for custom subagent types and I.4 for Codex invocation/flags. (2026-10-15)
2. **Give it a task id** `T<YYYYMMDD>-<slug>` and a row in the progress ledger (I.17), state `queued`. (2026-10-14)
3. **Write the brief** with all I.12 headings/provenance requirements; read I.12 before writing it. Commit the brief under I.13's ownership rules, then send its path, never pasted earlier conversation. (2026-10-15)
4. **Parallel work:** follow I.15 before launching shared work. (2026-10-15)
5. **Hard-tier work:** execute I.12's design/builder/reader/read-back gates before code; record premise answers in the task trail. Batch small same-shaped tasks only within I.12's batching limit. (2026-10-15)
6. **Codex briefs** name the Codex role, "Codex's own rules", the answer language, and for task workers and
   verifiers the rule files the repository lists for them, the tree, the sandbox (I.4) and which launches,
   commits or pushes are ordered. A research worker never commits or runs jobs. (2026-10-14)
7. **Launch in the background** unless the next step needs the result; set the ledger row to `running` and its
   watch/heartbeat according to I.23 before launch. (2026-10-14) (2026-10-15)
8. **On its report**: first run I.13's receipt checks, then act on its status word; read the full report in the task trail only as far as needed;
   update the ledger; relay to the user what matters, keeping what you observed apart from what
   the agent reported; answer escalations (I.11) by `SendMessage` to the same agent (Codex: a new call that quotes its report and the
   answer), quoting who decided; send
   finished implementations to review (`review` skill). (2026-10-14) (2026-10-15)
