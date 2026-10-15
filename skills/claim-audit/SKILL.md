---
name: claim-audit
description: Audit the claims and numbers of a write-up, handoff or paper against raw results before they are published or reported as findings. Use after a grid or experiment finishes and before any number goes into a paper or a result summary.
---
<!-- general -->

# Claim audit (2026-10-15)

Approval: user, 2026-10-15: "좋아. 그렇게 바꿔줘."

1. **Numbers come from records.** Every number in a handoff, results README, report or paper is either generated
   from the result records by a script, or carries the path of the record it was read from (and the run ids).
   A number with neither is removed or traced before the audit goes on. (2026-10-14)
2. **Claims file.** List every claim with its number, the result file, the run ids, the configuration and the run
   card of the block it comes from, and the comparison and threshold it rests on (the repository's claim
   threshold, e.g. a difference above the paired noise). (2026-10-14)
3. **Mechanical check first.** A script confirms every number exists in the named result file with the stated
   value and run ids; mismatches are fixed before any judgement. Then, with the run-card tool named in the run
   rules:
   - Independently validate comparisons and fingerprints using `experiment-plan` The order, before the audit verdict; (2026-10-15)
   - Independently validate post-check kind and controls using `experiment-plan` The order, before the audit verdict; (2026-10-15)
   - Independently validate scoring and raw-read-on-miss using `experiment-plan` The order, before the audit verdict. (2026-10-14; 2026-10-15) (2026-10-15)
4. **Wording check.** Independently check the text against the cards and the `experiment-plan` Wording requirements before the verdict, including exploratory labels, evidence for strong words and reporting misses honestly. (2026-10-15)
5. **Zero-context audit.** A fresh Codex (Sol, read-only) gets only the claims file, the cards and the raw result
   paths, not our summary or reasoning, and checks: number provenance, the baseline is the stated one, no
   normalisation to our own output, the scope (n, seeds, rates, configurations) matches the wording, nothing
   claimed beyond the threshold, metrics actually computed. For citations: the cited work exists (two indexes)
   and says what we attribute to it. (2026-10-14)
6. **Verdict per claim**: supported / weaken the wording / remove. The writer applies it; disputes go to the user. (2026-10-14)
7. Record the audit in the task trail. (2026-10-14)
