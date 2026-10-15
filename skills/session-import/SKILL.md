---
name: session-import
description: Take over work on a new machine or in a new session. Use when the user says the session starts on a new machine or system ("새 시스템에서 시작했어", "다른 기계에서 이어서 할게"), or when a master session starts and the user has not named the line of work it takes.
---
<!-- general -->

# Session import (2026-10-15)

Approval: user, 2026-10-15: "좋아. 그렇게 해줘. 다른 레포에도 쓰게 해주고, 승인해줘."

1. **Read and fetch**: read the master's startup rule files; fetch the remote so the progress ledgers and handoff
   files are current. (2026-10-15)
2. **List the open lines**: every progress ledger with rows not done and every handoff file whose newest
   subsection is not marked closed. For each line give the newest handoff subsection (number, date), its state in
   one line, what it waits on, and the work that was in flight with where it publishes. (2026-10-15)
3. **Ask the user** in the report language which line or lines this session takes. Several sessions may be open:
   take only the lines the user assigns, and leave the others untouched. (2026-10-15)
4. **Resume each chosen line** with the `handover` skill's "At the start of a new session" paragraph. (2026-10-15)
5. **Check the machine-local items** the handoff lists (credentials, untracked data, containers, tool paths,
   transcripts, memory) before relying on them, and report what is missing on this machine. (2026-10-15)
