#!/usr/bin/env python3
"""Stop hook: show the user a Windows desktop notification when the master finishes an answer.

Stop fires for the main session only (subagents fire SubagentStop), so only the master's answers notify.
WSL2: the notification is a Windows balloon tip raised through powershell.exe, started detached so the
hook returns at once. Any failure is silent: a missing notification must never block the session.
"""
import json
import os
import subprocess
import sys

PS = "/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe"
SCRIPT = (
    "Add-Type -AssemblyName System.Windows.Forms;"
    "$n = New-Object System.Windows.Forms.NotifyIcon;"
    "$n.Icon = [System.Drawing.SystemIcons]::Information;"
    "$n.Visible = $true;"
    "$n.ShowBalloonTip(8000, 'Claude Code', '{msg}', 'Info');"
    "Start-Sleep -Seconds 9; $n.Dispose()"
)


def main():
    try:
        data = json.load(sys.stdin)
        if not isinstance(data, dict) or data.get("stop_hook_active"):
            return
        cwd = data.get("cwd")
        if cwd is not None and not isinstance(cwd, str):
            return
        project = os.path.basename(cwd or os.environ.get("CLAUDE_PROJECT_DIR", "")) or "session"
        if "\0" in project:
            return
        msg = f"{project}: answer finished".replace("'", "")
        if not os.path.exists(PS):
            return
        subprocess.Popen([PS, "-NoProfile", "-WindowStyle", "Hidden", "-Command", SCRIPT.format(msg=msg)],
                         stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                         start_new_session=True)
    except Exception:
        # Notifications are best effort, including malformed input and launch failures.
        return


if __name__ == "__main__":
    main()
