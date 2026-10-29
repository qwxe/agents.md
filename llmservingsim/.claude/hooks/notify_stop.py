#!/usr/bin/env python3
"""Stop hook: show the user a Windows desktop notification when the master finishes an answer.

Stop fires for the main session only (subagents fire SubagentStop), so only the master's answers notify.
WSL2: the notification is a Windows toast raised through powershell.exe and the WinRT toast API, run
synchronously (about 1-2 s). A toast stays on screen after PowerShell exits; the earlier balloon tip
needed a live process and was lost when the hook's child process ended (2026-10-29). Any failure is silent: a missing notification must never block the session.

The balloon title names the session, so the user can tell which of several sessions finished: the last
user-set title in the transcript ("custom-title" record), else the last automatic title ("ai-title"),
else the first 8 characters of the session id. The script goes to PowerShell as -EncodedCommand (base64
of UTF-16LE), so Korean titles and quotes survive.
"""
import base64
import json
import os
import subprocess
import sys

PS = "/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe"
SCRIPT = (
    "[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null;"
    "[Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null;"
    "$x = New-Object Windows.Data.Xml.Dom.XmlDocument;"
    "$x.LoadXml('<toast><visual><binding template=\"ToastGeneric\"><text>{title}</text><text>{msg}</text></binding></visual></toast>');"
    "$id = '{{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}}\\WindowsPowerShell\\v1.0\\powershell.exe';"
    "[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier($id).Show([Windows.UI.Notifications.ToastNotification]::new($x))"
)
MAX_TITLE = 60


def ps_quote(text):
    """Text for toast XML inside a PowerShell single-quoted string: XML-escaped, quotes doubled,
    control characters dropped."""
    text = "".join(ch for ch in text if ch >= " ")
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
    return text.replace("'", "''")


def transcript_title(path):
    """The last custom title, else the last automatic title, in the transcript; None if neither."""
    if not isinstance(path, str) or not path or "\0" in path:
        return None
    custom = auto = None
    with open(path, "rb") as fh:
        for raw in fh:
            # Cheap filter before parsing: transcripts can be tens of MB.
            if b'-title"' not in raw:
                continue
            try:
                rec = json.loads(raw)
            except ValueError:
                continue
            if not isinstance(rec, dict):
                continue
            if rec.get("type") == "custom-title":
                value = rec.get("customTitle") or rec.get("title")
                if isinstance(value, str) and value.strip():
                    custom = value.strip()
            elif rec.get("type") == "ai-title":
                value = rec.get("aiTitle")
                if isinstance(value, str) and value.strip():
                    auto = value.strip()
    return custom or auto


def session_name(data):
    try:
        name = transcript_title(data.get("transcript_path"))
    except Exception:
        name = None
    if not name:
        sid = data.get("session_id")
        name = sid[:8] if isinstance(sid, str) and sid else "session"
    return name[:MAX_TITLE]


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
        if not os.path.exists(PS):
            return
        title = ps_quote(f"Claude Code: {session_name(data)}")
        msg = ps_quote(f"{project}: answer finished")
        script = SCRIPT.format(title=title, msg=msg)
        encoded = base64.b64encode(script.encode("utf-16-le")).decode("ascii")
        subprocess.run([PS, "-NoProfile", "-NonInteractive", "-EncodedCommand", encoded],
                       stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                       timeout=8)
    except Exception:
        # Notifications are best effort, including malformed input and launch failures.
        return


if __name__ == "__main__":
    main()
