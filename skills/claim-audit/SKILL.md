---
name: claim-audit
description: Audit the claims and numbers of a write-up, handoff or paper against raw results before they are published or reported as findings. Use after a grid or experiment finishes and before any number goes into a paper or a result summary.
---
<!-- general -->

# Claim audit (2026-10-14)

1. **Claims file.** List every claim with its number, the result file, the run ids and the configuration it comes
   from, and the comparison and threshold it rests on (the repository's claim threshold, e.g. a difference above
   the paired noise).
2. **Mechanical check first.** A script confirms every number exists in the named result file with the stated
   value and run ids; mismatches are fixed before any judgement.
3. **Zero-context audit.** A fresh Codex (Sol, read-only) gets only the claims file and the raw result paths, not
   our summary or reasoning, and checks: number provenance, the baseline is the stated one, no normalisation to
   our own output, the scope (n, seeds, rates, configurations) matches the wording, nothing claimed beyond the
   threshold, metrics actually computed. For citations: the cited work exists (two indexes) and says what we
   attribute to it.
4. **Verdict per claim**: supported / weaken the wording / remove. The writer applies it; disputes go to the user.
5. Record the audit in the task trail.
