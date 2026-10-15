---
name: review
description: Send a finished implementation to an independent verifier and act on the verdict. Use when an implementer reports Done (AGENTS I.14).
---
<!-- general -->

# Review by a verifier (2026-10-15)

Approval: user, 2026-10-15: "좋아. 그렇게 바꿔줘."

0. Read `agents/INTERFACE.md` I.13 before accepting a report or stopping for a time limit. (2026-10-14)
1. **Start a verifier** with `spawn-agent`, using I.14's independent verifier/model selection. (2026-10-15)
2. Read `agents/INTERFACE.md` I.14 before preparing or reading review inputs. (2026-10-14)
3. **Review depth:** follow I.14 for the independent second opinion; tell the verifier whether this ends a line of work so the complete verifier checklist selects its full/reference/mutation checks. (2026-10-15)
4. **Ledger row** -> `review`. (2026-10-14)
5. **On the verdict:** PASS -> ledger `done` (remove row, I.17), relay. PASS with notes -> relay notes; the user decides whether they become tasks. REJECT -> resume the implementer with numbered findings (`SendMessage`; Codex: a new call), following I.14's capped fix/re-review/dispute loop. Read I.13 before recording/committing the verdict; it owns the caller-commits exception. (2026-10-15)
6. Read `agents/INTERFACE.md` I.14 before collecting several reviewers' first verdicts. (2026-10-14)
7. The master does not review the code itself; it relays the verdict. (2026-10-14)
