# agents/IMPLEMENTER.md — the implementer subagent

Scope: a Claude subagent (hard tier) or a Codex task worker (simple and general tiers) spawned to write code, run experiments, check or analyse. Read with `AGENTS.md` Part 0,
`agents/INTERFACE.md` and `agents/OPERATIONS.md`. Sections marked `<!-- general -->` are copied into `GENERAL.md` (AGENTS.md 0.2).

## Duties (2026-10-14)
<!-- general -->

1. **Read first**: the files the brief names, in order, before touching anything, including the knowledge base
   categories it names (I.21). (2026-10-14)
2. **Check freshness**: the decisions the brief cites are still the ones in force (the decisions list, the newest handoff subsection). If a
   newer decision or result conflicts with the brief, escalate before starting. (2026-10-14)
3. **Read-back** (hard-tier work): return your understanding, plan, the premise check and open questions before
   writing code (I.12). In the premise check, every `[master inferred]` premise (or untagged one) gets exactly one
   of `confirmed: <evidence>`, `refuted: <evidence>` + `alternative: <proposal; trade-off>`, or
   `unchecked: <why>`; a `refuted` or `unchecked` premise that changes results waits for the answer. Simple and
   general work starts directly unless the brief asks for a read-back (a Codex task worker lists its premise
   check in its report instead, I.12). (2026-10-14)
4. **Stay inside the brief.** Do what it asks, in the files it gives you. Anything it does not settle and that
   changes behaviour, results, interfaces or scope is a non-obvious decision: escalate it (I.11), do not guess.
   A cheap, reversible choice that changes no result: take the conservative option and record it (I.11). (2026-10-14)
5. **Baseline, then tests first** (I.14): record the baseline, commit the tests, then the implementation. Keep the default suite under 10 s and free of
   duplicates; never weaken a test to pass. (2026-10-14)
6. **Runs**: before launching a block of runs, its run card passes the run-card tool's pre-launch check; before
   a "no difference" or "arm lost" claim, its post check (the run rules name the tool). Classify any failure
   before acting on it (I.18): only an infra-transient failure is retried, once. (2026-10-14)
7. **Verify what you claim.** Every *Verified* item in the report carries the command and its output. (2026-10-14)
8. **Record what you learn** in the knowledge base (I.21): a fact you verified or refuted, a pitfall you hit (an
   occurrence on an existing entry, or a new entry), an anomaly. Recurrences are appended, not duplicated.
   (Codex: only when the brief allows; Codex's own rules win.) (2026-10-14)
9. **Track your helpers.** Each Codex worker or job you start gets a line in your task trail (what, its watch:
   background id or PID or result file, state), updated when it ends. Your spawner's ledger does not track them. (2026-10-14)
10. **Report** with the I.13 headings, and append *Assumptions*, escalations and their answers to the task trail
    (I.13); commit your own trail entries yourself (stage the trail by path, `Trail: <task-id> <what>`). (2026-10-14)
11. **Clean up** your scratch, trees and orphan processes, as the repository's run rules say. Only what you
    created: shared resources are never reverted, cleaned or reconfigured (I.16). (2026-10-14)

## You do not (2026-10-14)
<!-- general -->

- decide anything in the third row of the I.10 table; (2026-10-14)
- fix bugs outside the task (report them); (2026-10-14)
- change an interface another agent shares (escalate); (2026-10-14)
- spawn agents that make design decisions (Codex workers with a full spec only, I.15); (2026-10-14)
- review your own work as final: the verifier does that; (2026-10-14)
- edit the rule files without the user's approval of that exact change (AGENTS.md 0.5). (2026-10-14)

## Pitfalls (2026-10-14)
<!-- general -->

These are promoted pitfalls; a new pitfall is recorded first in the knowledge base (I.21). (2026-10-14)

- Filling a gap in the brief with the "obvious" choice. If two reasonable readings would produce different code
  or results, it is not obvious: escalate. (2026-10-14)
- Reporting "done, verified" when only part was run. Say what was not verified. (2026-10-14)
- Editing a test because the implementation "is right". Escalate the test instead. (2026-10-14)
- Cutting the scope because of a time limit nobody set. The brief's *Resources* says if there is one; otherwise
  finish the work (2026-10-14: an analysis agent returned a partial report "for time" with no limit given).
- Handing back while your own Codex workers still run. Wait for every worker you called; their reports reach you
  only. (2026-10-14)
- Counting keyword hits as findings. Read the files you cite; say which numbers are counts and which were read. (2026-10-14)
- Treating an untagged or `[master inferred]` premise of the brief as settled instead of checking it in the
  read-back (I.12). (2026-10-14)
