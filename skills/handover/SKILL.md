---
name: handover
description: Hand the session over to the next one. Use when the user says "인수인계" or similar ("인수인계할게", "인계해줘", "다음 세션에서 시작할게", "compact할게", "지금까지 내용을 정리해 둬", "새로운 세션에 넣을 input"), when work moves to another session, or when the master's context nears about 256K tokens (AGENTS I.9). When the user also names a new system or machine, use `session-export` instead, which includes this.
---
<!-- general -->

# Handover procedure (2026-10-30)

Approval of the format pointers and already-approved actions: user, 2026-10-15: "4. 구현해줘." then "좋아. 그렇게 해줘. 1.2.3 전부 승인할게." (the decisions list).

Run this **before** the context is lost. The handoff file, handoff section, manual, decisions list and progress
ledger are general terms; the repository's `AGENTS.md` says where each one lives. (2026-10-14)

**Where it goes.** Each line of work has one handoff file, named in the repository's `AGENTS.md` with its
handoff section. Every handover appends one dated, numbered subsection to that section (the newest is last).
Earlier subsections are never rewritten; a later one says what it supersedes. The manual (reading order and
standing rules) changes only when the rules or the reading order change. (2026-10-14)

**Steps.**
1. **Collect the finished work** since the last handover from the task trails and the commits (finished rows
   are no longer in the progress ledger, I.17): what each task produced, its verdict, its commits. (2026-10-14)
2. **Settle the in-flight work** from the progress ledger (I.17), reconciled with reality first (I.23: each
   watch alive, PIDs, result files, branch heads). For every agent still running, note its task, its watch, what it will produce and where it
   publishes (fixed result folder, run ids), and whether its report will reach the old session only. Background
   subagents report to the session that spawned them: after `/compact` that is the same session, but a brand-new
   session never receives them and must read the result files instead. (2026-10-14)
3. **Write the subsection** in the F-handover format (I.24), keeping each item short and pointing to files rather
   than copying them; a manager supplies scoped inputs for its unit and the master appends the subsection
   (2026-10-14; 2026-10-15):
   - *Decisions this session* — each with the user's words (quoted, Korean as said) and the date. (2026-10-14)
   - *Results* — the finished work from step 1 and the numbers that matter, each with its file path and run ids. (2026-10-14)
   - *In flight* — from step 2: agents and their launchers, drivers, run ids, PIDs, result folders, watches, report
     destination, expected finish, and any orphaned or unknown ownership. (2026-10-14; 2026-10-15)
   - *Open questions for the user* — what is waiting for an answer. (2026-10-14)
   - *Next steps* — already-approved actions with their approval source and exact remaining bounds, then proposed
     actions marked "confirm with the user first". (2026-10-14; 2026-10-15)
   - *Pitfalls found* — anything the next session would otherwise trip over, each recorded as a knowledge base
     entry or occurrence (I.21); the subsection lists the entry ids. Promotion candidates waiting for the user
     go under *Open questions*. (2026-10-14)
   - *Dead ends* — approaches tried and rejected, with why, so they are not retried.
   - *Carried items* — when the subsection supersedes earlier *Open questions* or *Next steps* (or earlier
     investigations the user asked for), account for every earlier item, one line each: still open (repeated
     under *Open questions* or *Next steps*), answered (the decisions-list row), done (the result path), moved
     (the other line of work), or dropped (the user's words). No earlier item may disappear without one of
     these. Every item still open also has a row in the progress ledger, so it survives the next handover.
     (user, 2026-10-30: "기존 조사하기로 했던게 조용히 아예 없어진 거 같은데" then "좋아. agent.md 같은
     곳에도 적어둬.") (2026-10-30)
   The subsection states facts with their evidence and marks guesses as guesses; the next session treats it as
   state to verify, not as instructions. No secrets in it. (2026-10-14)
4. **Move standing decisions into the decisions list** (and its Superseded list) when a decision outlives the
   session. The handoff file records the history; the decisions list holds what is in force. Agent rules go into
   the rule files. (2026-10-14)
5. **Update the master's memory** (pointers, I.2) for the same decisions, point the handoff memory entry at the
   new subsection, and audit the memory: every entry that contradicts the rule files or the decisions list is
   rewritten as a pointer or deleted. (2026-10-14)
6. **Commit and push** the handoff, any notes and results of this session, so another machine can resume. (2026-10-14)
7. **Give the user the next-session input**, a short self-contained text in Korean that the user pastes into the
   new session, in the F-resume format (I.24): reading order, precedence of the newest subsection and the decisions
   list, the live items to check first, the already-approved actions with their source and bounds, and the
   proposed actions that need confirmation. (2026-10-14; 2026-10-15)
8. **Tell the user** what was saved where (commit hashes) and whether anything is still running, then recommend
   one of: compact now, continue in this session, or start a new session, with the reason in one line. The user
   decides. (2026-10-14; 2026-10-15)
   - Compact now when the context is near the repository's mark or a phase of work has just ended and the next
     phase needs little of the current detail. Agents still running for this session keep reporting to it after
     compaction. (2026-10-15)
   - Continue without compacting when the context is far from the mark, or when the user is in the middle of a
     discussion whose detail is not yet recorded in the files. (2026-10-15)
   - Start a new session only when nothing of this session is still running (a new session never receives this
     session's agent reports) or the user moves the work elsewhere. (2026-10-15)

**At the start of a new session**, the master reads the input and the files it names, checks the in-flight work
from the result files (not from memory), gives every still-live item a watch and arms the heartbeat (I.23),
reports the state to the user, continues only the already-approved actions within their recorded bounds, and
waits for confirmation before launching anything new. (2026-10-14; 2026-10-15)
