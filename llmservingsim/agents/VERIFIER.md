# agents/VERIFIER.md — the verifier subagent

Scope: a Claude subagent spawned by the master to review a finished implementation. Read with `AGENTS.md` Part 0,
`agents/INTERFACE.md` and `agents/OPERATIONS.md`. Sections marked `<!-- general -->` are copied into `GENERAL.md` (AGENTS.md 0.2).

## Inputs (2026-10-14)
<!-- general -->

The implementer's brief, the branch and commit range, the checks named in the brief's *Done when*, and only the
*Verified*, *Assumptions* and *Test changes* sections of the implementer's report (I.14). You have no Edit or
Write tool; you write your verdict to the task trail through Bash only.

## Checklist (in order) (2026-10-14)
<!-- general -->

1. **Diff against the brief.** Every changed file is in scope; every new behaviour was asked for. Behaviour the
   brief did not ask for is a silent decision: a finding.
2. **Tests not weakened.** Compare the tests at the test commit with the head: no deleted, loosened, skipped or
   re-targeted test. New tests have no duplicates (I.14).
3. **Red for the right reason.** Check out the test commit: the new tests fail, for the reason they target; for
   a fix, the regression test fails with the fix reverted. Look for empty assertions and missing boundary cases.
4. **Run the checks yourself:** the default test suite and the quick golden check named in the repository's run rules; the
   full golden run and reference checks only when the brief says this ends a line of work.
5. **Re-run a sample** of the implementer's *Verified* claims and compare the outputs.
6. **Assumptions against I.10 and I.11.** An assumption that belongs to the spawner or the user, or one that
   should have stopped the work, is a finding.
7. **End of a line of work only:** targeted mutation testing on the changed core modules (I.14); report the
   mutation score and the tests that kill no mutant on their own. For hard-tier work, run the Codex review
   yourself through the Codex CLI (I.4) and report its findings separately.
8. **Parallel merges** (I.15): look for the same thing done two ways.

## Verdict (2026-10-14)
<!-- general -->

Report with the I.13 headings and, first, one of: **PASS**, **PASS with notes**, **REJECT** (rules in I.14:
refuted-and-survived findings only, severity decides the verdict, "no findings" is normal). Findings are numbered,
each with file, trigger, evidence (command output or quoted diff), severity and the rule it breaks. End with
`git status --porcelain` and HEAD of the reviewed tree, unchanged. On a re-review, mark each earlier finding
ADDRESSED / NOT ADDRESSED and look only at the fix range.

## Verifier pitfalls (2026-10-14)
<!-- general -->

- Starting from the implementer's narrative instead of the brief and the diff.
- Counting a check as passed because the implementer reported it: re-run it.
- Padding findings, or reporting one you could not trigger.

## You do not (2026-10-14)
<!-- general -->

- fix code, tests or docs (a finding says what is wrong, not a patch);
- relax a check because the change "looks right";
- report a check you did not run as passed.
