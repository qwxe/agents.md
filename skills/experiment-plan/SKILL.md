---
name: experiment-plan
description: Plan an experiment or grid before launching it, for the user's approval. Use before any new grid, sweep or set of runs.
---
<!-- general -->

# Experiment plan (2026-10-14)

1. **Claim and anti-claim**: what the experiment should show, and what result would refute it.
2. **Setup**: configurations, arms, workloads, seeds, metrics, all as pointers into the decisions list.
3. **Expected results** per block, and how each outcome would be read (success, failure, ambiguous).
4. **Must and nice**: the runs the claim needs, and the optional ones.
5. **Gates**: go/stop conditions after the first runs (sanity checks, noise level), and the budget (runs, slots,
   wall time).
6. **Approval**: the user approves the plan before launch (new runs need the user's approval). After the runs,
   `claim-audit`.
