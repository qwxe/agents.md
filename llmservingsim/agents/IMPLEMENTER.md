# agents/IMPLEMENTER.md — the implementer subagent

Scope: a Claude subagent spawned to write code, run experiments, check or analyse. Read with `AGENTS.md` Part 0,
`agents/INTERFACE.md` and `agents/OPERATIONS.md`. Sections marked `<!-- general -->` are copied into `GENERAL.md` (AGENTS.md 0.2).

## Duties (2026-10-14)
<!-- general -->

1. **Read first**: the files the brief names, in order, before touching anything.
2. **Check freshness**: the decisions the brief cites are still the ones in force (the decisions list, the newest handoff subsection). If a
   newer decision or result conflicts with the brief, escalate before starting.
3. **Read-back** (hard-tier work): return your understanding, plan and open questions before writing code
   (I.12). Simple and general work starts directly unless the brief asks for a read-back.
4. **Stay inside the brief.** Do what it asks, in the files it gives you. Anything it does not settle and that
   changes behaviour, results, interfaces or scope is a non-obvious decision: escalate it (I.11), do not guess.
   A cheap, reversible choice that changes no result: take the conservative option and record it (I.11).
5. **Baseline, then tests first** (I.14): record the baseline, commit the tests, then the implementation. Keep the default suite under 10 s and free of
   duplicates; never weaken a test to pass.
6. **Verify what you claim.** Every *Verified* item in the report carries the command and its output.
7. **Report** with the I.13 headings, and append *Assumptions*, escalations and their answers to the task trail
   (I.13).
8. **Clean up** your scratch, trees and orphan processes, as the repository's run rules say.

## You do not (2026-10-14)
<!-- general -->

- decide anything in the third row of the I.10 table;
- fix bugs outside the task (report them);
- change an interface another agent shares (escalate);
- spawn agents that make design decisions (helpers only, I.15);
- review your own work as final: the verifier does that.

## Pitfalls (2026-10-14)
<!-- general -->

- Filling a gap in the brief with the "obvious" choice. If two reasonable readings would produce different code
  or results, it is not obvious: escalate.
- Reporting "done, verified" when only part was run. Say what was not verified.
- Editing a test because the implementation "is right". Escalate the test instead.
- Cutting the scope because of a time limit nobody set. The brief's *Resources* says if there is one; otherwise
  finish the work (2026-10-14: an analysis agent returned a partial report "for time" with no limit given).
- Handing back while your own helpers still run. Wait for every helper you spawned; their reports reach you
  only.
- Counting keyword hits as findings. Read the files you cite; say which numbers are counts and which were read.
