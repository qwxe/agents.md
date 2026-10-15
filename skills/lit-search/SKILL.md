---
name: lit-search
description: Literature, documentation or source-code research through Codex. Use whenever an agent needs papers, docs or how a deployed system implements something (AGENTS I.4).
---
<!-- general -->

# Literature search (2026-10-15)

Approval: user, 2026-10-15: "좋아. 그렇게 바꿔줘."; formats and Opus judging: user, 2026-10-15: "4. 구현해줘." then "좋아. 그렇게 해줘. 1.2.3 전부 승인할게." (the decisions list).

1. **Brief Codex** (Luna for finding, Sol for judging) with: the question; 2-4 rephrasings to search in parallel;
   where to search (paper indexes, official docs, the actual source code); the period; the answer language. (2026-10-14)
2. **Output contract** to ask for: the F-research format (I.24), with an evidence table (claim, source URL, source type: paper / preprint / docs /
   code / blog, how it was checked: read / abstract only / not checked); claims labelled *verified*, *inferred*,
   *unverified*; contradictions kept, not resolved silently; a coverage status (what was searched, what was not,
   what could not be reached); the queries used. (2026-10-14)
3. **No URL, no claim.** A source that was not read is not described; a number comes with the passage it is from. (2026-10-14)
4. **Check before relying**: the caller (a manager, for its unit) opens the sources behind any claim it will act on or cite. (2026-10-14) Codex output is a second opinion, not a verified source. Validating another agent's answer beyond the passages the caller opens is an independent Opus source audit (`document-audit` skill, F-document-audit); the master receives a concise evidence packet. (2026-10-14; 2026-10-15)
5. **Citations for a paper** go through `claim-audit` step 3 before they are used. (2026-10-14)
6. **Keep what was verified.** Before recording reusable deployed-system behaviour or tool flags, follow I.21's evidence/status/write policy. The caller opens relied-on sources (step 4) and records verified facts; unread claims remain unchecked/assumed under I.21. The research worker proposes entries in its report. (2026-10-14; 2026-10-15)
