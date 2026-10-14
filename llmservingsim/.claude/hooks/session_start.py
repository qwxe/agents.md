#!/usr/bin/env python3
"""SessionStart hook: point a new session at the progress ledgers (AGENTS.md I.17) without printing their contents.

Prints at most 10 lines to stdout (Claude Code adds SessionStart stdout to the session's context): one line per
`notes/ledger/*.md` with the number of table rows whose state is not `done`, then one line pointing to AGENTS.md 0.4.
Any error prints nothing and exits 0.
"""
import os
import sys
from pathlib import Path

MAX_LEDGERS = 8


def open_rows(path):
    """Count table rows whose `state` column is not `done`. Returns None if the file has no state column."""
    state_col, n = None, 0
    for line in path.read_text(errors="replace").splitlines():
        if not line.lstrip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if state_col is None:
            low = [c.lower() for c in cells]
            if "state" in low:
                state_col = low.index("state")
            continue
        if all(set(c) <= set("-: ") for c in cells):
            continue
        if state_col < len(cells) and cells[state_col].strip("*` ").lower() != "done":
            n += 1
    return None if state_col is None else n


def main():
    root = Path(os.environ.get("CLAUDE_PROJECT_DIR") or Path(__file__).resolve().parents[2])
    lines = []
    ledgers = sorted((root / "notes" / "ledger").glob("*.md"))
    for p in ledgers[:MAX_LEDGERS]:
        n = open_rows(p)
        rel = p.relative_to(root)
        lines.append(f"Progress ledger {rel}: " + ("no state column" if n is None else f"{n} row(s) not done"))
    if len(ledgers) > MAX_LEDGERS:
        lines.append(f"... and {len(ledgers) - MAX_LEDGERS} more in notes/ledger/")
    lines.append("Research ledger and handoff: see AGENTS.md 0.4 (where the current state lives).")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
