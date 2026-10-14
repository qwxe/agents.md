---
name: review
description: Send a finished implementation to an independent verifier and act on the verdict. Use when an implementer reports Done (AGENTS I.14).
---
<!-- general -->

# Review by a verifier (2026-10-14)

1. **Start a verifier** with the `spawn-agent` steps: a Codex verifier (Sol, medium), or the Claude subagent type
   `verifier` (Opus, medium) when byte-exact core code changed. The verifier did not write the code.
2. **Give it**: the implementer's brief; the branch and commit range (test commit to head); the checks named in
   *Done when*; and only the *Verified*, *Assumptions* and *Test changes* sections of the implementer's report,
   not its narrative.
3. **Say whether this ends a line of work.** Only then does the verifier run the full golden run, the reference
   checks and targeted mutation testing; for hard-tier work, also a Codex review of the same diff.
4. **Ledger row** -> `review`.
5. **On the verdict**: PASS -> ledger `done`, relay. PASS with notes -> relay the notes; the user decides whether
   they become tasks. REJECT -> resume the implementer with the numbered findings (`SendMessage`; Codex: a new call with the findings), then re-review
   the fix range only. **Cap**: after three REJECT rounds, one new agent a tier higher (Codex work goes to Opus) gets one attempt; after that
   take it to the user. A disputed finding goes to the user. The verdict is appended to the task trail.
6. **Several reviewers** (e.g. verifier and Codex review): collect each first verdict before showing any of them
   the others'.
7. The master does not review the code itself; it relays the verdict.
