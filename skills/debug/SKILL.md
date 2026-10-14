---
name: debug
description: Diagnose a mismatch, hang, crash or non-determinism. Use when a check fails unexpectedly, two trees disagree, or a run stalls.
---
<!-- general -->

# Debugging (2026-10-14)

0. **Classify the failure** (I.18): infra-transient (retry once, logged), infra-permanent, content, spec
   mismatch or integrity. A content failure of a deterministic program is not retried: it repeats. Search the
   knowledge base for the same failure `type` or `logic` before starting (I.21). (2026-10-14)
1. **A deterministic red command first**: one command that reproduces the failure every time (compare two trees,
   a check on a clock or digest, `git bisect run` with that check). (2026-10-14)
2. **Minimise** the reproduction (smallest input, config, commit range). (2026-10-14)
3. **Hypotheses**: write 3-5 falsifiable ones in the task trail, each with the observation that would refute it. (2026-10-14)
4. **One variable at a time**; tagged debug output, removed before commit. (2026-10-14)
5. **Three failed fixes -> stop** and escalate: the design, not the line, may be wrong. (2026-10-14)
6. The fix comes with a regression test that fails when the fix is reverted (I.14). (2026-10-14)
7. **Record it** in the knowledge base (I.21): the cause as a pitfall (or an occurrence on the existing entry),
   with the refuted hypotheses as evidence. (2026-10-14)
