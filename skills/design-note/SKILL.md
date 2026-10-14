---
name: design-note
description: Write a decision-complete design note before hard-tier implementation, and run the builder check. Use before spawning an implementer for anything in the hard tier.
---
<!-- general -->

# Design note and builder check (2026-10-14)

1. **The note** holds: problem and intent; goals, non-goals and anti-goals; the decisions already made (pointers
   into the decisions list, quoted user words); interfaces and data formats; the algorithm or behaviour, precise
   enough to code; edge cases; acceptance criteria that can fail; what would show the design wrong.
2. **Decision complete** means an implementer would have nothing left to decide that changes behaviour, results
   or interfaces.
3. **Builder check.** A fresh agent reads the note as the implementer would and lists every question it would
   have to answer. Sort each: answered in the note / trivial (implementer's choice, I.10) / the user's. Put the
   answers into the note; take the user's questions to the user.
4. Only then spawn the implementer, with the note as its main document.
