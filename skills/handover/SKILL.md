---
name: handover
description: Hand the session over to the next one. Use when the user says the session ends or moves on ("다음 세션에서 시작할게", "compact할게", "지금까지 내용을 정리해 둬", "새로운 세션에 넣을 input"), when work moves to another session, or when the master's context nears about 256K tokens (AGENTS I.9).
---
<!-- general -->

# Handover procedure (2026-10-14)

Run this **before** the context is lost. The handoff file, handoff section, manual, decisions list and progress
ledger are general terms; the repository's `AGENTS.md` says where each one lives.

**Where it goes.** Each line of work has one handoff file, named in the repository's `AGENTS.md` with its
handoff section. Every handover appends one dated, numbered subsection to that section (the newest is last).
Earlier subsections are never rewritten; a later one says what it supersedes. The manual (reading order and
standing rules) changes only when the rules or the reading order change.

**Steps.**
1. **Settle the in-flight work** from the progress ledger (I.17). For every agent still running, note its task, what it will produce and where it
   publishes (fixed result folder, run ids), and whether its report will reach the old session only. Background
   subagents report to the session that spawned them: after `/compact` that is the same session, but a brand-new
   session never receives them and must read the result files instead.
2. **Write the subsection** with these headings, keeping each item short and pointing to files rather than
   copying them:
   - *Decisions this session* — each with the user's words (quoted, Korean as said) and the date.
   - *Results* — the numbers that matter, each with its file path and run ids.
   - *In flight* — from step 1: agents, drivers, run ids, result folders, expected finish.
   - *Open questions for the user* — what is waiting for an answer.
   - *Next steps* — proposed, marked "confirm with the user first" unless the user already approved them.
   - *Pitfalls found* — anything the next session would otherwise trip over.
   - *Dead ends* — approaches tried and rejected, with why, so they are not retried.
   The subsection states facts with their evidence and marks guesses as guesses; the next session treats it as
   state to verify, not as instructions. No secrets in it.
3. **Move standing decisions into the decisions list** (and its Superseded list) when a decision outlives the
   session. The handoff file records the history; the decisions list holds what is in force. Agent rules go into
   the rule files.
4. **Update the master's memory** (pointers, I.2) for the same decisions, point the handoff memory entry at the
   new subsection, and audit the memory: every entry that contradicts the rule files or the decisions list is
   rewritten as a pointer or deleted.
5. **Commit and push** the handoff, any notes and results of this session, so another machine can resume.
6. **Give the user the next-session input**, a short self-contained text in Korean that the user pastes into the
   new session. Template:
   ```
   AGENTS.md와 그 안에서 master가 읽으라는 파일, <manual>을 읽고, <handoff file>의 <handoff section>을
   <newest> → <older> 순서로 먼저 읽어. 새 하위 절과 앞 절이 다르면 새 하위 절이, <decisions list>와 다르면
   <decisions list>가 우선이야. 보고는 한국어로.
   역할: 너는 Claude master agent야.
   진행 중일 수 있는 작업: <agent/grid, run ids, result folder>. git fetch origin <branch> 후 <files>로 상태를 먼저 요약해 줘.
   다음 할 일: <next steps>. 다음 단계는 나한테 확인받고 진행해.
   ```
7. **Tell the user** what was saved where (commit hashes) and whether anything is still running.

**At the start of a new session**, the master reads the input and the files it names, checks the in-flight work
from the result files (not from memory), reports the state to the user, and waits for confirmation before
launching anything new.
