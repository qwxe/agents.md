---
name: claim-audit
description: Audit the claims and numbers of a write-up, handoff or paper against raw results before they are published or reported as findings. Use after a grid or experiment finishes and before any number goes into a paper or a result summary.
---
<!-- general -->

# Claim audit (2026-10-14)

1. **Numbers come from records.** Every number in a handoff, results README, report or paper is either generated
   from the result records by a script, or carries the path of the record it was read from (and the run ids).
   A number with neither is removed or traced before the audit goes on. (2026-10-14)
2. **Claims file.** List every claim with its number, the result file, the run ids, the configuration and the run
   card of the block it comes from, and the comparison and threshold it rests on (the repository's claim
   threshold, e.g. a difference above the paired noise). (2026-10-14)
3. **Mechanical check first.** A script confirms every number exists in the named result file with the stated
   value and run ids; mismatches are fixed before any judgement. Then, with the run-card tool named in the run
   rules:
   - every compared pair of blocks passes `compare` (fingerprints equal except the arm variables and arm flags);
   - every card passes `check --post` with the claim's kind (`null`, `arm-lost` or `difference`): arm-active
     result always, positive-control result for a null or "arm lost" claim;
   - the card is scored, and every miss was explained after reading the raw results (`raw_read`). (2026-10-14)
4. **Wording check.** Against the cards: a same-seed rerun is not called a replication; "confirmed",
   "significant" or "robust" appears only with its evidence stated; results of exploratory blocks are labelled
   exploratory; a missed prediction is reported as a miss, not reworded into a hit. (2026-10-14)
5. **Zero-context audit.** A fresh Codex (Sol, read-only) gets only the claims file, the cards and the raw result
   paths, not our summary or reasoning, and checks: number provenance, the baseline is the stated one, no
   normalisation to our own output, the scope (n, seeds, rates, configurations) matches the wording, nothing
   claimed beyond the threshold, metrics actually computed. For citations: the cited work exists (two indexes)
   and says what we attribute to it. (2026-10-14)
6. **Verdict per claim**: supported / weaken the wording / remove. The writer applies it; disputes go to the user. (2026-10-14)
7. Record the audit in the task trail. (2026-10-14)
