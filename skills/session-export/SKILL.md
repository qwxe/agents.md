---
name: session-export
description: Hand this session's work to another machine. Use when the user says the work moves to another machine or system ("다른 시스템에서 새로 시작하려고 해", "다른 기계로 옮길게", "전부 push하고 넘겨줘").
---
<!-- general -->

# Session export (2026-10-15)

Approval: user, 2026-10-15: "좋아. 그렇게 해줘. 다른 레포에도 쓰게 해주고, 승인해줘." and, for step 3, "session export할 때 이것도 같이 갱신하도록해줘."

Run this before the user leaves the machine. It extends the `handover` skill with what a move between machines
needs; the handover procedure itself stays in that skill. (2026-10-15)

1. **Hand over this session** with the `handover` skill, steps 1-6 (handoff subsection, decisions list, memory,
   progress ledger, commit and push). (2026-10-15)
2. **Push every branch.** Compare every local branch with the remote. Push each branch that is ahead or missing on
   the remote. A branch that diverged from the remote is never force-pushed by the agent: first push the remote
   head to a backup branch on the remote (e.g. `backup/<branch>-remote-<date>`), then show the user the diverged
   branches (commits on each side) and let the user decide. Branches of other sessions are pushed only on the
   user's order (I.16). A rule-change branch still under review is pushed too, so the other machine can continue it;
   pushing it neither merges nor publishes it. (2026-10-15)
3. **Sync the published rule copy.** Where the repository publishes a copy of its rule files to another repository,
   check that copy against the main branch and publish any drift of reviewed rule files, so the other machine and
   other repositories read the same rules. Rule changes still under review stay unpublished; list them in the
   handoff with their branch and review state. (2026-10-15)
4. **List what a push does not carry** in the handoff subsection: credentials, untracked data, containers and build
   environments, tool install paths, the session transcripts, the master's memory, and work still running on this
   machine (which stops reporting when the session ends). Say where each is on this machine. (2026-10-15)
5. **Check the push**: no local branch is ahead of the remote, the handoff commit is on the remote, and the published
   rule copy is in sync. Then tell
   the user, in the report language, the commits, the backups made, anything not pushed and why, and the words
   to say in the new session ("새 시스템에서 시작했어"), which start the `session-import` skill. (2026-10-15)
