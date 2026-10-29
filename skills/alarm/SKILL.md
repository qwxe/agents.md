---
name: alarm
description: Set an alarm that wakes the master after a set time so it resumes the work (wakes subagents, renews the heartbeat, reports). Use when the user asks for an alarm or a delayed resume ("1시간 이후 알람을 울려줘", "N분 뒤에 다시 재개해줘", "알람 맞춰줘", "리밋 걸리니까 나중에 이어서 해줘").
---
<!-- general -->

# Alarm (2026-10-30)

Approval: user, 2026-10-30: "비슷하게 alarm skill을 만들어줘. 정해진 시간 이후 알람이 울리고, master agent가 받아서
나머지 이어서 작업하는거야. subagent들을 깨우고 등." then "skill 작성 권한은 승인할게." (session c462661d).

The alarm is a background Bash task of the master. When it exits, the harness notification wakes the master,
which then resumes. It also shows a Windows toast. (2026-10-30)

## Setting it

1. If the user wants usage saved (for example a session limit is near), stop the master heartbeat task with
   TaskStop; the alarm replaces it until it fires. Leave running subagents alone unless the user asks to stop
   them. (2026-10-30)
2. Start the `alarm.py` script in this skill's folder (`python3 <skill folder>/alarm.py <minutes> "<short message>"`) with `run_in_background: true`
   from the repository root. Never wrap it in a foreground sleep or poll its output. (2026-10-30)
3. Write the alarm time and what resumes into the ledger heartbeat line (I.17/I.23) and push it, so a new
   session can see it too. (2026-10-30)
4. Tell the user in Korean the wall-clock time it fires and what will resume. (2026-10-30)

## When it fires

1. Read the ledger heartbeat line and the live rows; fetch and fast-forward the worktrees involved. (2026-10-30)
2. For each live subagent: check its output file and branch commits. If it finished, process its report as
   usual. If it stopped (usage limit, error) or is idle while work remains, wake it with SendMessage (agent id
   from the ledger) and a short continue message naming the next step; never spawn a duplicate. (2026-10-30)
3. Restart the 30-minute master heartbeat and renew the ledger heartbeat line. (2026-10-30)
4. Report to the user in Korean: what happened while waiting, what was resumed, and any queued questions.
   Continue the work; do not wait for the user unless a decision is needed. (2026-10-30)
