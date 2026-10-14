---
name: spawn-agent
description: Spawn a Claude subagent or a Codex worker with a correct brief. Use every time the master (or an implementer calling a Codex worker) delegates a task (AGENTS I.12, I.15).
---
<!-- general -->

# Spawning an agent (2026-10-14)

1. **Pick the tier, then the role and model** (I.3). Start with Codex Sol medium; use Luna only for fully
   specified mechanical work. Record the selection criterion in *Resources*. Use Opus only for an identified
   hard criterion; neither a possible question nor an Opus parent makes a task hard. Hard: a Claude subagent
   (implementer or verifier) on Opus
   at effort medium, spawned with its custom subagent type: the type sets the model and the tool permissions
   mechanically, and its prompt names the role's rule files (an instruction, not a guaranteed load, so the brief
   names them too). Everything else goes to Codex (I.4): a task worker (Luna for simple, Sol medium for general), a
   Codex verifier, or a research worker. (2026-10-14)
2. **Give it a task id** `T<YYYYMMDD>-<slug>` and a row in the progress ledger (I.17), state `queued`. (2026-10-14)
3. **Write the brief to the task trail with the I.12 headings, in order**, commit it (the spawner commits the
   brief; the agent commits its own entries, I.13), and send its path (never paste earlier
   conversation): role line and task id; read first (rule files, and the knowledge base categories or entries
   the task needs, I.21); goal and intent (the user's words quoted and dated); decided (pointers into the
   decisions list); not yours to decide; scope (files it owns, files others own, and the shared resources it
   may touch); interfaces; resources; done when; report (I.13). A heading with nothing to say says "none".
   **Tag every premise** under every heading, *Resources* included, with its source (I.12):
   `[user <date> "<quote>"]`, `[decisions <area>]`, `[rule <id>]`, `[knowledge <id> <status>]`,
   `[code <path>]` or `[master inferred]`; never leave an inferred premise untagged. (2026-10-14)
4. **Parallel work** (I.15): fix shared interfaces in every brief first; one writer per file; tell each what the
   others own. (2026-10-14)
5. **Hard-tier work**: start from a decision-complete design note (`design-note` skill) and its builder check;
   reader-test the brief with a fresh Codex Sol medium worker (I.3); the builder check also defaults to Sol
   and may share that worker. Ask the implementer for a read-back before it codes. Check that the
   read-back answers every `[master inferred]` or untagged premise with `confirmed`, `refuted` + `alternative`,
   or `unchecked`; take a `refuted` or `unchecked` premise that changes results to the user; the agent records
   the answers in its task trail.
   **Small same-shaped tasks**: batch them into one brief for one agent. (2026-10-14)
6. **Codex briefs** name the Codex role, "Codex's own rules", the answer language, and for task workers and
   verifiers the rule files the repository lists for them, the tree, the sandbox (I.4) and which launches,
   commits or pushes are ordered. A research worker never commits or runs jobs. (2026-10-14)
7. **Launch in the background** unless the next step needs the result; set the ledger row to `running` and its
   *watch* column to the agent id or the background command id, marked `(session)` (I.23); make sure the
   heartbeat is armed. (2026-10-14)
8. **On its report**: first run the receipt checks (I.13: the claimed commits and files exist; no time limit
   the brief did not set; a missing item: resume the agent with the list), then act on the status word; read the full report in the task trail only as far as needed;
   update the ledger; relay to the user what matters, keeping what you observed apart from what
   the agent reported; answer escalations (I.11) by `SendMessage` to the same agent (Codex: a new call that quotes its report and the
   answer), quoting who decided; send
   finished implementations to review (`review` skill). (2026-10-14)
