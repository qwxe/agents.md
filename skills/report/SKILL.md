---
name: report
description: Build a report, chart page or meeting summary for the user from results. Use whenever the user asks for a report, charts, a summary to show, or meeting material.
---
<!-- general -->

# Report (2026-10-16)

Approval: user, 2026-10-16: "보여주고자 하는 주장에 대해서만 최소한으로, 깔끔하고 직관적으로 보고서를 만들어줘. 먼저 물어서 어떤 부분이 명시적으로 드러나는지도 물어보고, 애매한 부분도 묻고." then "paper-write 말고 report 로 바꿔줘. ... 내가 말한 부분도 추론해서 넣어줘." and, on the draft, "Recommended 기반. 그런데 3번 등 only if asked는 너무 강하고. 필요하면 맥락에 따라 추가할 수 있어." (session e030368e). Items 2-6 are inferred from the user's requests in that session.

1. **Ask first**, in one round, each question with a recommended option: the claim the report must show; what
   must be explicit on it (runs, metrics, axes, numbers); every ambiguous definition or data choice. Ask again
   only when an answer is blank or unclear. (2026-10-16)
2. **Scope follows what the user named**: the runs, arms, settings and quantities the user named come first.
   Add another run, comparison or derived quantity when the claim needs it in context, and say in its label why
   it is there. (2026-10-16)
3. **Prefer distributions to summaries** when the claim is about spread, timing or overlap: plot the
   distributions themselves (PDF or CDF on a shared axis). Add a summary number (median, share, mean) beside a
   chart when it helps the reading. (2026-10-16)
4. **Minimal by default**: the claim in one line, the charts that carry it, a one-line environment label per
   run (configuration, load), axis labels and the numbers the user named. Background, method notes or caveats
   go in only when the reader needs them to read a chart correctly, in one line each. (2026-10-16)
5. **Evidence status in one line** where it changes how a number reads: seeds, upper bound versus exact,
   audited or not. (2026-10-16)
6. **Result tables**: configuration on top, arms as rows, unless the user asks otherwise. (2026-10-16)
7. **Deliver** as a page or file the user can open and share, and give its location; keep the generating script
   beside it so the report can be rebuilt. (2026-10-16)
8. A report whose numbers feed a paper or a decision still takes `claim-audit` before those numbers are reused;
   prose for a paper uses `paper-write`. (2026-10-16)
