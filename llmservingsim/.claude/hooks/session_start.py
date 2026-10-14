#!/usr/bin/env python3
"""SessionStart hook: point a new session at the progress ledgers (AGENTS.md I.17) and the knowledge base's promotion
candidates (AGENTS.md I.21) without printing their contents.

Prints at most 10 lines to stdout (Claude Code adds SessionStart stdout to the session's context): one line per
`notes/ledger/*.md` with the number of table rows whose state is not `done`; one line with the number of rows in the
"Promotion candidates" table of `knowledge/KNOWLEDGE.md` (only when that file exists); then one line pointing to
AGENTS.md 0.4. Any error prints nothing and exits 0.
"""
import os
import sys
from pathlib import Path

MAX_LEDGERS = 7
CATALOG = Path("knowledge") / "KNOWLEDGE.md"


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


def promotion_candidates(path):
    """Count the data rows of the table under the `Promotion candidates` heading (0 if there is no table)."""
    n, inside, header_seen = 0, False, False
    for line in path.read_text(errors="replace").splitlines():
        if line.startswith("#"):
            inside = "promotion candidates" in line.lower()
            header_seen = False
            continue
        if not inside or not line.lstrip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not header_seen:
            header_seen = True
            continue
        if all(set(c) <= set("-: ") for c in cells):
            continue
        n += 1
    return n


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
    cat = root / CATALOG
    if cat.is_file():
        lines.append(f"Knowledge base {CATALOG.as_posix()}: {promotion_candidates(cat)} promotion candidate(s) "
                     "(the master proposes them to the user, AGENTS.md I.21)")
    lines.append("Research ledger and handoff: see AGENTS.md 0.4 (where the current state lives).")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
