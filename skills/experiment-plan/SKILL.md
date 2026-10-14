---
name: experiment-plan
description: Plan an experiment or grid before launching it, for the user's approval, and write its run cards. Use before any new grid, sweep or set of runs.
---
<!-- general -->

# Experiment plan and run cards (2026-10-14)

The plan says what the runs are for and what we expect; the **run card** is the same reasoning in a form a tool
checks. Each run block (a set of runs launched for one purpose) gets one card, made and checked with the run-card
tool named in the run rules. The card is enforced by the tool, not by asking: a block without a card that passes
`check` is not launched, and a comparison or claim without the checks below is not made (user, 2026-10-14).

## What the plan contains

1. **Claim and anti-claim**: what the experiment should show, and what result would refute it. Each block's card
   carries its `claim` (a pointer to the plan or the paper claim) and its `intent` (why this block is needed now). (2026-10-14)
2. **Retrodiction first.** Before planning runs, look at the results that already exist and ask whether they
   answer the question. List what was checked; if they answer it, do not launch (the tool refuses a card whose
   `retrodiction.answerable` is true). Otherwise say why they do not (`why_not`). (2026-10-14)
3. **Setup**: configurations, arms, workloads, seeds, metrics, all as pointers into the decisions list. (2026-10-14)
4. **Label**: each block is `confirmatory` (tests a stated prediction; its tree must be clean) or `exploratory`
   (looks for something; its results are leads, not findings, until a confirmatory block repeats them). (2026-10-14)
5. **Predictions** per block: for each, the metric, the arm, the expected value or direction and the tolerance,
   and how each outcome would be read (success, failure, ambiguous). These replace a free-text "expected
   results". (2026-10-14)
6. **Control plans**:
   - *Arm-active check* (`arm_active_check.how`): how we will see that each arm actually ran as intended (a log
     line, a counter, a statistic that only that arm produces). An arm that silently fell back to the baseline
     is the commonest false null.
   - *Positive control* (`positive_control.how`): a known difference the pipeline must detect (e.g. a setting
     known to change the metric), so that "no difference" means no difference and not a blind measurement. (2026-10-14)
7. **Must and nice**: the runs the claim needs, and the optional ones. (2026-10-14)
8. **Gates**: go/stop conditions after the first runs (sanity checks, noise level), and the budget (runs, job
   slots, wall time). (2026-10-14)

## The order (one card per block; every step uses the run-card tool)

1. `new`: create the block's card. (2026-10-14)
2. Fill claim, intent, label, retrodiction, predictions and both control plans from the plan above. (2026-10-14)
3. `fingerprint` it from the tree the runs use: the md5 of every input file, the environment variables that
   affect results (an unset variable is recorded as unset, since its default may differ from any explicit
   value), the command-line flags (verbatim, in order), the build, the configuration and the tool versions.
   A tree that is its own repository is identified by its commit and whether tracked files are modified; any
   other directory (e.g. a copied measurement tree) by a content hash of its files plus the commit it was built
   from (`--source-commit`, required). Per arm, `fingerprint --arm <name>` records what differs per arm (its
   variables, flags and arm-specific inputs). (2026-10-14)
4. `check` must pass. (2026-10-14)
5. The user approves the plan together with its checked cards (new runs need the user's approval). (2026-10-14)
6. Run the block. (2026-10-14)
7. `set` the run ids and seeds as the runs launch, and the control results (`--control positive|arm-active`)
   once they are read; nobody edits the card by hand. (2026-10-14)
8. `score` every prediction as hit or miss with the observed value. A miss means our model of the system was
   wrong somewhere: read the raw results (logs, per-request records), not only the summary, before explaining
   it; rescore with `--raw-read` once done. (2026-10-14)
9. `check --post --claim <kind>` must pass before the result is reported: the arm-active result is required for
   every claim; the positive-control result is required for a null ("no difference") or an "arm lost" claim. (2026-10-14)
10. `compare` two blocks before putting their numbers side by side: it refuses when their fingerprints differ in
    anything but the named arm variables and arm flags. A refused comparison is not made; rerun instead. (2026-10-14)

## Wording

- A rerun with the same seed and inputs checks determinism; it is **not a replication**. A replication changes
  what the claim says should not matter (seed, arrival order, workload slice) and says so. (2026-10-14)
- "Confirmed", "significant" or "robust" only with the evidence stated next to it (n, the noise measure, the
  threshold of the repository); otherwise say "observed once" or "in this run". (2026-10-14)
- Results from an exploratory block are reported as exploratory. (2026-10-14)

After the runs, run `claim-audit` before any number leaves the task trail. (2026-10-14)
