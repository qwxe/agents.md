---
name: debug
description: Diagnose a mismatch, hang, crash or non-determinism. Use when a check fails unexpectedly, two trees disagree, or a run stalls.
---
<!-- general -->

# Debugging (2026-10-14)

1. **A deterministic red command first**: one command that reproduces the failure every time (compare two trees,
   a check on a clock or digest, `git bisect run` with that check).
2. **Minimise** the reproduction (smallest input, config, commit range).
3. **Hypotheses**: write 3-5 falsifiable ones in the task trail, each with the observation that would refute it.
4. **One variable at a time**; tagged debug output, removed before commit.
5. **Three failed fixes -> stop** and escalate: the design, not the line, may be wrong.
6. The fix comes with a regression test that fails when the fix is reverted (I.14).
