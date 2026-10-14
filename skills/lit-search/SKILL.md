---
name: lit-search
description: Literature, documentation or source-code research through Codex. Use whenever an agent needs papers, docs or how a deployed system implements something (AGENTS I.4).
---
<!-- general -->

# Literature search (2026-10-14)

1. **Brief Codex** (Luna for finding, Sol for judging) with: the question; 2-4 rephrasings to search in parallel;
   where to search (paper indexes, official docs, the actual source code); the period; the answer language.
2. **Output contract** to ask for: an evidence table (claim, source URL, source type: paper / preprint / docs /
   code / blog, how it was checked: read / abstract only / not checked); claims labelled *verified*, *inferred*,
   *unverified*; contradictions kept, not resolved silently; a coverage status (what was searched, what was not,
   what could not be reached); the queries used.
3. **No URL, no claim.** A source that was not read is not described; a number comes with the passage it is from.
4. **Check before relying**: the caller opens the sources behind any claim it will act on or cite.
5. **Citations for a paper** go through `claim-audit` step 3 before they are used.
