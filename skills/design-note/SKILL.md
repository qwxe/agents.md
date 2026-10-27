---
name: design-note
description: Write a decision-complete design note before hard-tier implementation, and run the builder check. Use before spawning an implementer for anything in the hard tier.
---
<!-- general -->

# Design note and builder check (2026-10-27)

Approval: user, 2026-10-15: "좋아. 그렇게 바꿔줘."; formats and Opus judging: user, 2026-10-15: "4. 구현해줘." then "좋아. 그렇게 해줘. 1.2.3 전부 승인할게." (the decisions list); Codex default verifier: user, 2026-10-23: "검증을 opus로 하라는 게 있을텐데. default는 codex로 하도록 해줘." then chose "hard 작업만 Opus (Recommended)" and fallback "Sonnet/Haiku" (the decisions list).

1. **The note** uses the F-design fields (I.24) and holds: problem and intent; goals, non-goals and anti-goals; the decisions already made (pointers
   into the decisions list, quoted user words); interfaces and data formats; the algorithm or behaviour, precise
   enough to code; edge cases; **contingencies** ("if X turns out true, do Y": the foreseeable surprises and
   the pre-agreed response to each, so the implementer does not have to decide them); acceptance criteria that
   can fail; what would show the design wrong. Every premise carries its source tag (I.12); the knowledge base
   entries the design relies on are named, with their status (I.21). (2026-10-14)
   The note also states its **scope ceiling**: the files the change may touch and what it must not add (new schema
   versions, manifest kinds, validation layers or diagnostic fields nobody asked for), so that the implementation is
   the smallest change that delivers the decided behaviour; a revision that adds an interface requirement says
   which decision asks for it (user, 2026-10-16: "좋아. 그리고 그건 개념을 상정할 때만 코드 구현을 상관하지 않아도 된다는 의미였어. 실제 구현할 때는 최소 구현으로."). (2026-10-16)
2. **Decision complete** means an implementer would have nothing left to decide that changes behaviour, results
   or interfaces. (2026-10-14)
3. **Builder check.** A fresh independent Opus verifier (I.3, I.14) reads the note as the implementer would and lists every question it would
   have to answer; builder acceptance is a verification. Sort each: answered in the note / trivial (implementer's choice, I.10) / the user's. Put the
   answers into the note; take the user's questions to the user. (2026-10-14) Hard-tier work starts only from this decision-complete note, leaving the implementer no unsettled design decision; settle the user's questions before spawning (I.12). (2026-10-14) (2026-10-15)
4. **Reader test.** The brief built on the note gets a separate comprehension probe (F-reader, I.24; Codex Terra
   allowed, I.3); it reports only what it understands and what is ambiguous, and a reader that starts judging
   correctness stops and goes back to the caller for a verification assignment (I.3). (2026-10-15; 2026-10-23) (2026-10-27)
5. Only then spawn the implementer, with the note as its main document. A hard investigation may start earlier with
   a bounded question-and-evidence brief and a read-back, without implementation authority (I.12). (2026-10-14; 2026-10-15)
