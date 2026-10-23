---
name: claim-audit
description: Audit the claims and numbers of a write-up, handoff or paper against raw results before they are published or reported as findings. Use after a grid or experiment finishes and before any number goes into a paper or a result summary.
---
<!-- general -->

# Claim audit (2026-10-23)

Approval: user, 2026-10-15: "좋아. 그렇게 바꿔줘."; formats and Opus judging: user, 2026-10-15: "4. 구현해줘." then "좋아. 그렇게 해줘. 1.2.3 전부 승인할게." (the decisions list); Codex default verifier: user, 2026-10-23: "검증을 opus로 하라는 게 있을텐데. default는 codex로 하도록 해줘." then chose "hard 작업만 Opus (Recommended)" and fallback "Sonnet/Haiku" (the decisions list).

1. **Numbers come from records.** Every number in a handoff, results README, report or paper is either generated
   from the result records by a script, or carries the path of the record it was read from (and the run ids).
   A number with neither is removed or traced before the audit goes on. (2026-10-14)
2. **Claims file** in the F-experiment-audit schema (I.24). List every claim with its number, the result file, the run ids, the configuration and the run
   card of the block it comes from, and the comparison and threshold it rests on (the repository's claim
   threshold, e.g. a difference above the paired noise). (2026-10-14)
3. **Mechanical check first.** A script confirms every number exists in the named result file with the stated
   value and run ids; mismatches are fixed before any judgement. Then, with the run-card tool named in the run
   rules:
   - Independently validate comparisons and fingerprints using `experiment-plan` The order, before the audit verdict; (2026-10-15)
   - Independently validate post-check kind and controls using `experiment-plan` The order, before the audit verdict; (2026-10-15)
   - Independently validate scoring and raw-read-on-miss using `experiment-plan` The order, before the audit verdict. (2026-10-14; 2026-10-15) (2026-10-15)
4. **Wording check.** Independently check the text against the cards and the `experiment-plan` Wording requirements before the verdict, including exploratory labels, evidence for strong words and reporting misses honestly. (2026-10-15)
5. **Zero-context audit.** A fresh independent verifier (I.3, I.14, read-only; Opus when the numbers enter a paper, a Codex Sol task worker otherwise), assigned by the caller, gets only the claims file, the cards and the raw result
   paths, not our summary or reasoning, and checks: number provenance, the baseline is the stated one, no
   normalisation to our own output, the scope (n, seeds, rates, configurations) matches the wording, nothing
   claimed beyond the threshold, metrics actually computed. For citations: the cited work exists (two indexes)
   and says what we attribute to it. (2026-10-14; 2026-10-23)
6. **Verdict per claim**: supported / weaken the wording / remove, returned with an F-verdict in the designated verdict artifact; missing noise evidence is never turned into an invented sd of 0. The writer applies it; disputes go to the user. Document or source claims mixed in take the `document-audit` skill too. (2026-10-14; 2026-10-15)
7. Record the audit in the task trail. (2026-10-14)
