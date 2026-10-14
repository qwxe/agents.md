---
name: spawn-agent
description: Spawn a Claude subagent or a Codex worker with a correct brief. Use every time the master (or an implementer spawning a helper) delegates a task (AGENTS I.12, I.15).
---
<!-- general -->

# Spawning an agent (2026-10-14)

1. **Pick the role and model.** Implementer, verifier or helper (I.1, I.15) and the tier (I.3); research goes to
   Codex (I.4). Spawn Claude subagents with their custom subagent type so the role's rule files and tool
   permissions load mechanically.
2. **Give it a task id** `T<YYYYMMDD>-<slug>` and a row in the progress ledger (I.17), state `queued`.
3. **Write the brief to the task trail with the I.12 headings, in order**, and send its path (never paste earlier
   conversation): role line and task id; read first; goal and intent (the
   user's words quoted and dated); decided (pointers into the decisions list); not yours to decide; scope (files
   it owns, files others own); interfaces; resources; done when; report (I.13). A heading with nothing to say says
   "none".
4. **Parallel work** (I.15): fix shared interfaces in every brief first; one writer per file; tell each what the
   others own.
5. **Hard-tier work**: start from a decision-complete design note (`design-note` skill) and its builder check;
   reader-test the brief with a fresh agent; ask the agent for a read-back before it codes.
   **Small same-shaped tasks**: batch them into one brief for one agent.
6. **Codex briefs** name "Codex's own rules" and the answer language; Codex never commits or runs jobs.
7. **Launch in the background** unless the next step needs the result; set the ledger row to `running`.
8. **On its report**: act on the status word (I.13); read the full report in the task trail only as far as needed;
   update the ledger; relay to the user what matters, keeping what you observed apart from what
   the agent reported; answer escalations (I.11) by `SendMessage` to the same agent, quoting who decided; send
   finished implementations to review (`review` skill).
