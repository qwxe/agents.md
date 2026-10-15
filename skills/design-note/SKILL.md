---
name: design-note
description: Write a decision-complete design note before hard-tier implementation, and run the builder check. Use before spawning an implementer for anything in the hard tier.
---
<!-- general -->

# Design note and builder check (2026-10-15)

Approval: user, 2026-10-15: "좋아. 그렇게 바꿔줘."

1. **The note** holds: problem and intent; goals, non-goals and anti-goals; the decisions already made (pointers
   into the decisions list, quoted user words); interfaces and data formats; the algorithm or behaviour, precise
   enough to code; edge cases; **contingencies** ("if X turns out true, do Y": the foreseeable surprises and
   the pre-agreed response to each, so the implementer does not have to decide them); acceptance criteria that
   can fail; what would show the design wrong. Every premise carries its source tag (I.12); the knowledge base
   entries the design relies on are named, with their status (I.21). (2026-10-14)
2. **Decision complete** means an implementer would have nothing left to decide that changes behaviour, results
   or interfaces. (2026-10-14)
3. **Builder check.** A fresh Codex Sol medium worker (I.3) reads the note as the implementer would and lists every question it would
   have to answer. Sort each: answered in the note / trivial (implementer's choice, I.10) / the user's. Put the
   answers into the note; take the user's questions to the user. (2026-10-14) Hard-tier work starts only from this decision-complete note, leaving the implementer no unsettled design decision; settle the user's questions before spawning (I.12). (2026-10-14) (2026-10-15)
4. Only then spawn the implementer, with the note as its main document. (2026-10-14)
