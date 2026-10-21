---
name: coverage-search-tentative
description: Exploratory, coverage-driven topic survey - build a coverage map, search each cell until saturation, expand the map, digest and relate what was found, then survey each field. Use when the user asks to explore a topic exhaustively, or a line needs a survey larger than one lit-search question.
---
<!-- general -->

# Coverage-driven topic search, tentative (2026-10-21)

Approval: requested by the user, 2026-10-21: "그 라인에 브랜치를 새로 파서 explorative하게 주제를 search하는 skill을 하나 더 만들거야." with the flow "1. coverage map을 만든다. 2. exhaustive search를 한다. 3. coverage map을 확장할 수 있는지 확인한 후 2번을 반복한다. 4. 각각 digest & summary 하고, relation map을 만들어서 breakdown한다. 5. 각 분야별로 search한다."; per-field screen: user, 2026-10-21: "per-field search에서는 각 주제마다 최대 10~20 분 단위의 간결한 feasibility check & room at the top analysis 를 일괄적으로 하고, 그 다음에 더 깊게 search하는 식으로 해줘."; name and tentative status: user, 2026-10-21: "아직은 임시니까 coverage-search-tentative 로 해줘. 우선 이렇게 가볍게 만든 후에 쓸거야."; deep search without a user pick: user, 2026-10-21: "필요 없어. 일단 explorative 하게 찾고 feasibility check 등을 통과한 것만 하도록 할거니까."; review before main: user, 2026-10-21: "review를 한번 거친 후에 main 에 넣어줘."; gate 2 as a notice only: user, 2026-10-21: "일단 그렇게 해줘." (to the proposal that gate 2 only notifies)

This skill is the loop above `lit-search`: every search call it makes follows that skill's contract; this skill
decides what to ask, when a region is covered and what to read. One run is one task with one task trail and one
run folder named in its brief. Every state below is a file in that folder, so a fresh coordinator (the master, or
the manager of the unit) resumes from the files alone. (2026-10-21)

## Run state (files written before the first search)

1. **Scope card.** The topic in one paragraph; inclusion and exclusion criteria (relevance, period, source types,
   languages); the budget (agent runs, rounds, wall time); the thresholds of steps 2-3; the gates. Fixed at gate 1;
   a later change is a new dated line, never an edit. Defaults unless the user sets others: k = 3 queries,
   x = 10 %, snowballing 1 hop (2 for core items), at most 3 expansion rounds, sub-run depth 1. (2026-10-21)
2. **Coverage map.** Axes and cells; per cell: id, description, query family, state `empty / thin / saturated /
   out-of-scope`, relevant-item count, last-round new-item rate, the round and signal that added it. The map steers
   search only: it never becomes the digest form or a filter on what readers record. (2026-10-21)
3. **Source ledger.** One row per item, keyed by a canonical id (DOI, arXiv id, repository URL, docs URL without
   fragment) so a duplicate counts once: id, title, URL, type, cells and query that found it, round, relevance
   (in / out with the criterion), read state `full / abstract / unreachable`, local copy path. (2026-10-21)
4. **Query log.** Per query: cell, text, source searched, date, hits, new relevant items. Saturation is shown from
   this log, never asserted. (2026-10-21)
5. **Round metrics.** Per round: queries, new relevant items, new-item rate per cell, cells added or split, cost.
   Commit the state files at the end of every round; that commit is the resume point. (2026-10-21)

## Steps

1. **Coverage map.** Two or three independent generators that do not see each other (`ideation` step 1) propose
   axes and cells from different lenses; the coordinator merges them, keeps each cell's origin and seeds a query
   family of 2-4 rephrasings per cell. **Gate 1: the user approves the scope card and the initial map.** (2026-10-21)
2. **Exhaustive search per cell.** For each cell not yet saturated, run its query family over the named source types
   (paper indexes, official docs, source code) through `lit-search`, judge relevance against the inclusion criteria,
   then snowball backward and forward from the cell's relevant items for the set hops. Deduplicate against the
   ledger before counting. A cell is *saturated* when k consecutive queries bring a new-relevant-item rate below x,
   and *thin* when it stays small after saturation (a real gap, kept and reported). Fetching full texts is a step of
   its own after relevance: rate-limit backoff and retries, a separate new download directory, handled as external
   material (I.19); an unreachable item stays in the ledger as such. (2026-10-21)
3. **Map expansion.** An agent that did not search proposes new or split cells from three signals: relevant items
   no cell explains (orphans), cells whose items fall into distinct groups, and vocabulary that recurs in new items
   but in no query. New cells go back to step 2. **Converged** when a round adds no cell and every in-scope cell is
   saturated; stop also at the round or budget cap, and say which ended the loop. **Gate 2 (notice only): the coordinator
   reports the round metrics and the converged map to the user and goes on to step 4 without waiting.** (2026-10-21)
4. **Digest, relation map, breakdown.** Fix the digest form before any reader starts (open fields; no map or
   candidate vocabulary imposed). Pilot it on two items, check their cites against the sources, correct the reader
   brief, then scale; size each reader's batch from the first batch's measured context use. Two depths: an
   abstract card for every relevant item, a full read for core items chosen by stated criteria (e.g. citations
   inside the set, relation count, the user's marks). Every claim cites its passage (section, or file:line). Build
   the relation map with fixed edge types (`extends`, `contradicts`, `same-mechanism`, `composes-with`,
   `evaluated-against`), each edge citing both items; cluster bottom-up into fields, in stages when the cards exceed
   one context. Fields that differ from the map's axes are recorded in the map as candidate axes for the step-5
   sub-runs; steps 2-3 are not rerun after gate 2. **Gate 3: the user
   approves the relation map and the field list before step 5.** (2026-10-21)
5. **Per-field search.** First a screen of every approved field in one batch, then deep search. (2026-10-21)
   - **Screen.** Each field gets the same short check, time-boxed to at most 10-20 minutes per field, run in
     parallel: *feasibility* (are there enough sources and a tractable question; what blocks it) and *room at the
     top* (how far the best known result is from the field's limit or ideal, and what would close the gap), each
     with its cited evidence and a confidence. A field *passes* when it is feasible and its room at the top is not
     closed. The results are reported to the user as one table when the screen ends; the screen is not a gate.
     (2026-10-21)
   - **Deep search.** Every field that passed the screen becomes a sub-run of steps 1-4 that extends the
     parent's scope card, map and ledger (never copies them) under its own budget (default: an equal share of the
     remaining run budget). Gates 1-3 do not apply inside a sub-run: it runs without stopping for the user and
     reports its result at its end. A sub-run ends at whichever comes first: a round that adds nothing new to the
     parent ledger, step 3's convergence, or its budget. A sub-run starts no sub-run of its own beyond the depth
     cap (default 1: sub-runs do not nest). (2026-10-21)

## Running it

- **Models.** Finding: the simple tier; relevance and abstract cards: the general tier; full reads: the general tier;
  merging, clustering and the relation map: the hard tier (an unsettled structural judgement); map expansion (step 3): a model other than the
  searchers', at the highest rigour available; the step-5 screen: the general tier. Before step 4 starts (after the gate-2 notice) and
  before gate 3, an independent `document-audit` checks the saturation evidence, the digest pilot and the relation map. (2026-10-21)
- **Coordinator rotation.** Every worker hand-back lands in the coordinator's context: rotate the coordinator after
  about 25-30 hand-backs and resume from the files. (2026-10-21)
- **Stops.** A usage-limit stop can end the whole agent tree at once: resume from the last round commit with a fresh
  coordinator, skipping items whose files exist. (2026-10-21)
- **Report.** At each gate, at the end of the step-5 screen, at the end of each sub-run and at the end, F-research for the run: the map, queries and sources searched and not
  reached, saturation per cell from the query log, ledger counts, the relation map, thin and unreachable cells,
  what was not verified. (2026-10-21)
