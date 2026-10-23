# agents/FORMATS.md — the formats home

Scope: every role, when a card, rule or skill names an F-* format. I.24 is the only normative home of the field templates; cards and skills say when to use a format, I.24 says which fields it has. Sections marked `<!-- general -->` are generated into `GENERAL.md` (AGENTS.md 0.2). (2026-10-15)

## I.24 Formats (2026-10-23)
<!-- general -->

Approval: user, 2026-10-15: "4. 구현해줘." then "좋아. 그렇게 해줘. 1.2.3 전부 승인할게." (the role-restructuring design, the decisions list). Codex default verifier: user, 2026-10-23: "검증을 opus로 하라는 게 있을텐데. default는 codex로 하도록 해줘." then chose "hard 작업만 Opus (Recommended)" and fallback "Sonnet/Haiku" (the decisions list). Every format, field list and rule paragraph of this section was set on 2026-10-15, except the verifier-model wording of F-verdict, F-document-audit and F-reader, changed on 2026-10-23. (2026-10-15; 2026-10-23)

Fields below are exact headings/columns in order; empty fields say `none`; N/A carries a reason. `<...>` are
placeholders. Every factual premise carries I.12 provenance; evidence claims are verified/inferred/unverified.
Format F-reasoning is a **concise decision rationale**, not a request to expose private chain-of-thought.
Scores/formats do not establish authority. Source dates, English committed prose and role language remain.

Caller output-format precedence: the caller's specified output format wins over the role-native default.
This changes presentation only and grants no decision, write, spawn, verification or approval rights.
Every report or returned packet, including one in a caller-specified format, must preserve these minimum fields, irrespective of headings or layout:

- Status word first (the role's status/verdict vocabulary).
- An explicit **Not verified** field, including `none` when applicable.
- For any review: the unchanged-tree receipt (reviewed HEAD/status before and after, with allowed scratch/output paths).
- For any review: Reviewer independence metadata (reviewer/model/version or unknown with reason; authorship independence;
  evidence access; prior exposure to the artifact, author reasoning and other verdicts).

A format that cannot express these fields or other mandatory evidence/limits requires immediate escalation
to the direct caller, with dependent work stopped. Cards, reports, verdicts and fallback adapters route here.

**F-brief** — caller before any agent assignment; use these ten ordered headings and fields:

```text
# <task-id> — <title>
## Brief (<caller/session>, <date>)
1. Role line and task id: role; custom type; report language; caller; parent_task; actual depth; maximum permitted depth; reporting destination.
2. Read first: brief rule-source commit (current reviewed main HEAD when brief is written); actual read revision
   (worker records separately in F-assumptions/F-report after freshness check); disk startup row/card;
   named sources/categories; every decisions-list row (by area) the task rests on (the worker reads only the cited rows); newest handoff; timing of each reference; for every Codex role, the full never-break section copied
   verbatim from that committed source, including heading/approval/dates/explanatory text (not a pointer).
3. Goal and intent: outcome/purpose; dated verbatim user intent.
4. Decided: current decision/approved-design pointers; provenance tags.
5. Not yours to decide: unresolved choices; required escalation.
6. Scope: branch/tree/files; artifact owner; decision owner; other owners; exclusions; permitted writes/launch/kill/commit/push.
7. Interfaces: exact inputs/outputs and immutable original artifact/version/digest references; shared signatures/formats/run ids; monitoring owner; task dependency edges,
   dependency depth (longest prerequisite chain in the declared task graph; independent of spawn depth),
   required artifact transfers (from/to, artifact/version, readiness condition) and integration owner;
   expected next artifact/checkpoint set by caller; for launchers, launcher channel file path, permitted writes,
   direct caller watch id/mechanism, polling cadence, and terminal-packet commit owner.
8. Resources: tier, model, effort, criterion; slots/lifetime; fallback; read-back requirement.
9. Done when: falsifiable acceptance checks; delivery/commit/publication authority.
10. Report: F-report or F-verdict; full record destination; inline summary; matching audit kind.
```

The exact I.12 provenance tag vocabulary is `[user <date> "<quote>"]`, `[decisions <area>]`, `[rule <id>]`,
`[knowledge <id> <status>]`, `[code <path>]`, `[master inferred]`. No tag means inferred. Record `caller` metadata; historical
`[master inferred]` means spawner inference at any depth.
Every brief must name the full commit of main whose rule files it was written against;
every Codex brief must also quote the rules that must never be broken verbatim, because guard hooks do not watch Codex commands.
The caller checks the copy against that committed section before launch; a newer rule commit requires the
worker's source-freshness reread, and a changed never-break section requires the caller to refresh the brief's safety copy before launch.
F-brief references the canonical never-break section rather than maintaining another independently edited template.

**F-assumptions** — worker before dependent action and in report; called by read-back.
Record separate `brief rule-source commit` (master: session-start reference commit) and `actual read revision`
fields, even when equal; link changed-section rereads and any freshness escalation. These fields also appear
under F-report Read/Assumptions rather than being inferred from an artifact commit:

```text
| Premise/choice + source tag | confirmed / refuted / unchecked | Evidence or why unchecked | Alternative + trade-off if refuted | Result/scope/interface effect | Cost if wrong | Answer/authority reference |
```

**F-read-back** — hard implementer/investigator before code; general work only when brief requires:

```text
READ_BACK
## Goal and plan
<understanding, bounded plan>
## Premise check
<F-assumptions; confirmed evidence OR refuted evidence + alternative OR unchecked reason>
## Open questions
<F-escalation or none; dependent work waits>
## Not verified
<unchecked premises/checks or none>
```

**F-report** — full writing-worker report; cards and skills reference this field list:

```text
<DONE | DONE_WITH_CONCERNS | ESCALATION | BLOCKED | NEEDS_CONTEXT | READ_BACK>
## Done
<artifacts and completed scope, evidence labels; immutable original brief/input/output version/digest references under I.8>
## Not done
<missing requested scope and reason>
## Read
<files/sections actually read, not hit counts>
## Assumptions
<F-assumptions; local choices and deviations with cost>
## Escalations
<F-escalation packets or none>
## Verified
<claim; exact command/read passage; exit/result; relevant output; scope; evidence label>
## Test changes
<added/changed/removed, separately from results>
## Rule use
<F-rule-use only after phase-1 activation; before activation say not active>
## Not verified
<unexecuted checks, unread sources, runtime limits, audit still pending>
## Commits / files
<branch, hashes or commit subject/current patch before own commit, owned paths, result folders>
```

DONE continues to mean ready for review. Inline reply: status, commit(s), one-line check and trail path; include
open escalation packets in full. Research report and verifier use their variants below; apart from the full never-break
startup addition, formats impose no further research startup reading. A writer may identify its own pending commit by subject/path in the committed trail,
then return the resulting hash inline, avoiding self-referential hashes.

**F-escalation** — any agent before dependent work; one packet for related questions:

```text
ESCALATION
Question: <quote ambiguous text/code; decision owner>
Blocker category: <missing intent | missing evidence | missing capability | missing approval | unresolved conflict>;
  responsible recipient: <agent/authority that can resolve it; delivery through direct caller>.
Search references only: <already available current standing decision/closed entries and dated historical
  quote/source; or not searched yet (immediate delivery); or searched <where> for <words>: nothing.
  Bounded lookup may supplement later; never delay delivery or adopt a historical answer>
Options: <2–3; interpretation; effects/cost/risk>
Recommendation: <option and evidence strength>
Independent work done / remaining: <paths and boundaries>
Delivery / monitoring: <mid-run destination; named manager relay if needed; pending packet/watch path;
  live owned jobs and continued health loop; resumed agent id or Codex new-call boundary>
On each answer: <actions immediately authorized; actions still requiring confirmation>
Answer: <pending OR date/decider/verbatim words/source; routed back through caller chain>
Not verified: <unconfirmed evidence, choices or channel capability; none if applicable>.
```

**F-verdict** — independent review/audit output (Codex by default, Opus for hard-tier work, builder checks and paper claim audits, I.3/I.14) in the designated verdict artifact, without opening the
author's explanatory report narrative; the assessed artifact itself, including a design/document's prose, is permitted input. The caller commits and links the verdict:

```text
<PASS | PASS WITH NOTES | REJECT | ESCALATION | BLOCKED>
Task / reviewer / model / independence: <ids; exact model/version or unknown with reason; authored none of assessed result;
  evidence access (available/unavailable sources); prior exposure to artifact/author reasoning/other verdicts>.
Reviewed scope: <brief, branch/base/head, diff/artifact digest, allowed report sections>
## Findings
<number; blocking/non-blocking; file/claim; trigger; evidence; rule; attempted refutation; survives why>
## Checks and gaps
<command/read passage, exit/output, scope; N/A reasons>
## Not verified
<unexecuted checks, unavailable evidence, runtime limits or none>
## Assumptions / Escalations
<premise challenges; F-escalation if needed>
## Test changes
none
## Rule use
<F-rule-use after activation>
## Re-review
<fix range; previous numbers ADDRESSED / NOT ADDRESSED, or none>
## Unchanged-tree receipt
<reviewed HEAD and git status --porcelain before/after; caller-prepared scratch tree/output paths; verifier-executed checks or recorded blocking inability>
## Proposed knowledge
<entry proposals only, or none>
```

Reviewer independence is procedural: no authorship of the assessed result, restricted evidence packets and
independent first verdicts before sharing reviews. Record model/version, evidence access and prior exposure
in F-verdict; disclose missing metadata and any compromised separation to the caller before acceptance.
Separate model instances can share errors: procedural independence does not establish statistically independent
error distributions or measured reliability.

Blocking findings imply REJECT; only nonblocking imply PASS WITH NOTES; none imply PASS. Audit per-claim
dispositions below accompany this verdict, not replace it with writer acceptance. Caller commits verdict
without sending implementer narrative to reviewer.

### Source and experiment formats

**F-document-audit** — the assigned verifier (I.3) auditing document analysis/design, including design notes:

```text
Artifact/digest; task; source snapshot; audit scope; reviewer independence.
| Claim id | Exact claim/policy proposal | Primary source path/URL + section/passage | Provenance/decision applicability | verified / inferred / unverified | Counterevidence/refutation attempt | supported / weaken / remove / decision-needed |
Coverage: <sources opened; unread/unreachable sources; searches; scope exclusions>.
Design completeness: <interfaces, ownership, contingencies, acceptance, moved-rule map, unresolved user choices>.
Experiment fields: N/A — document sources; <mixed experimental claims instead reference F-experiment-audit>.
Verdict: <F-verdict; no fabricated run ids/cards/statistics>.
```

Before decision-feeding document/source analysis is accepted, use the document-audit skill with F-document-audit; mixed experimental claims also use F-experiment-audit.

**F-experiment-plan** — author before approval; experiment-plan uses these fields:

```text
Claim / anti-claim; intent; existing-results retrodiction (checked, answerable, why_not).
Setup: decision pointers for configuration/arms/workload/seeds/metrics.
Block label: confirmatory | exploratory.
Predictions: metric, arm, expected value/direction, tolerance, success/failure/ambiguous interpretation.
Controls: arm_active_check.how; positive_control.how.
Required runs / optional runs; go/stop gates; slots/run/wall budget; approval source.
Run-card paths and checked fingerprints.
```

**F-experiment-audit** — claim-audit uses this claims-file schema; procedural checks belong to the skill:

```text
| Claim id + wording | Number/metric + value | Result path + raw record | Run ids | Configuration/arm/baseline | Block card | Comparison/fingerprint evidence | Threshold/noise + scope (n/seeds/rates/configurations) | Prediction/control/post-check evidence | supported / weaken / remove |
Mechanical number/provenance checks: <commands/output>.
Independent raw-result checks: <comparison, baseline, normalization, scope, metric computation>.
Wording/citations: <exploratory labels, strong-word evidence, misses/raw-read, two-index citation check>.
Verdict: <F-verdict; missing noise evidence cannot become invented sd=0>.
```

**F-research** — read-only research worker, supplied in brief:

```text
<DONE | DONE_WITH_CONCERNS | ESCALATION | BLOCKED | NEEDS_CONTEXT>
Answer: <bounded synthesis; no correctness/acceptance verdict on another agent>.
| Claim | Source URL/file + passage | Source type | read / abstract-only / unchecked | verified / inferred / unverified | Contradiction/limit |
Coverage: <queries, source sets/dates, opened vs unopened/unreachable>.
Assumptions / open choices: <F-assumptions/F-escalation as needed>.
Proposed knowledge: <category/title/status/evidence or none>.
Rule use: <supplied F-rule-use excerpt after activation>.
Not verified: <limits; caller's independent verification remains pending>.
```

**F-reasoning** — design/investigation decision rationale; no internal thought transcript:

```text
Question/intent; binding constraints with provenance.
Evidence: <observations and counterevidence; verified/inferred/unverified>.
Alternatives: <effects/trade-offs; objective exclusions only>.
Recommendation and concise rationale; what would refute it.
Decision owner/status; approved action boundary; contingencies; next falsifiable check.
```

**F-design** — design author, including hard implementation input:

```text
Problem/intent; goals/non-goals/anti-goals; settled decisions with provenance.
Interfaces/data formats; exact behaviour/algorithm; edge cases; contingencies.
Ownership/resources/monitoring; acceptance criteria; what would show the design wrong.
Per-file patch/move map; migration/commit order; open choices with effects/recommendation/action boundary.
Evidence/verification limits; builder-check and reader-test references when completed.
```

**F-reader** — Sol comprehension probe:

```text
<DONE_WITH_CONCERNS | DONE>
Input paths/digests; no prior context.
What I would do; claims/instructions I understand; ambiguous text; questions I would need answered.
No acceptance verdict. Caller assigns a verifier (I.3) if a correctness judgment is required.
Not verified: <scope limits; no correctness/acceptance check performed>.
```

### Records and lifecycle formats

**F-decision** — master light-path record: preserve the decisions list table columns `area | decision | date | source`;
retain its row-format requirements, verbatim words/date/source, why in one clause, what it supersedes, and
the rejected option/reason/reopening condition when an option is rejected. Date is the user's KST date;
source includes session/trail and UTC stamp when available. No paraphrase creates authority. Source applicability
must say standing versus task-local; task-local answers remain in that task's trail unless user states otherwise.

**F-notice** — master after approved rule changes:

```text
Change/key; exact home; why/evidence; approval owner/date/source; independent verdict; effective commit.
Important: <separate notice for never-break rules/decision rights/user contract/standing decisions; user may reverse>.
Other: <one line per ordinary change>.
```

**F-ledger** — master direct items only; I.17 uses this layout:

```text
Heartbeat: <id> since <time> | none
| task id | owner (agent/session) | state | blocked on | watch | next action | task trail |
Own-job progress: <task/job id -> F-helper progress record in own task trail; health, artifact evidence/time,
  caller-set checkpoint, pending decision/recipient; none if no own job>.
```

States remain queued/running/escalated/blocked/review/done; remove done row immediately with task-id commit.
**F-helper** — non-master caller's own trail, never master's ledger:

```text
| item/task/job | launcher/monitor owner | actual depth | PID/agent id | watch + session/cross-session marker | result path | state | last health observation + time | artifact progress + evidence/time | expected next artifact/checkpoint | pending decision + recipient | next action |
```

**F-unit** — manager's durable scoped summary, owned and updated in its own task trail under
`## Unit summary` (not the progress ledger or another manager's trail):

```text
Unit / manager task / parent task; assigned scope and current decision references.
Direct live items: <F-helper rows and watches; monitoring stays with each launcher>.
Completed artifacts / receipts / reviews: <links, scope, unresolved findings>.
Open escalations / dependencies: <packet and answer references; required transfers and integration owner from F-brief>.
Progress: <F-helper observation/progress/checkpoint/decision fields; current semantic-stall assessment>.
Next actions / authorization bounds; handoff inputs; last-updated source commit.
```

**F-handover** — master authoritative handoff, managers supply scoped inputs:

```text
### <next subsection> <date> — <session/line>
Decisions this session: <dated verbatim words; authoritative decision pointers>.
Results: <artifact/commit/verdict/run references; audited numbers only>.
In flight: <launchers; PIDs/result paths; watches; report destination; ownership uncertainty>.
Open questions for user: <F-escalation pointers>.
Next steps: <already-approved actions with source and exact remaining bounds; proposed actions requiring confirmation>.
Pitfalls found: <knowledge ids; pending promotion pointers>.
Dead ends: <approach/why; no authority to reopen closed decisions>.
```

**F-resume** — next-session input, supplied in Korean by master:

```text
역할: master. <the repository entry>를 디스크에서 읽고 해당 시작 규칙과 <manual/handoff newest section>을 읽어.
<handoff section>은 <newest> → <older> 순서로 읽어. 새 하위 절과 앞 절이 다르면 새 하위 절이,
현재 결정 목록과 다르면 현재 결정 목록이 우선한다. <live ids/result paths/owners>의 상태를 먼저 확인해.
git fetch origin <branch> 후 <files>로 상태를 먼저 요약해 줘. 보고는 한국어로.
이미 승인된 행동: <action, source, remaining bounds>. 제안된 행동: <requires confirmation>.
먼저 상태를 한국어로 보고하고, 승인된 범위에서 계속 진행해. 새 행동은 해당 승인 절차를 따른다.
```

**F-knowledge** — standard entry front matter retains existing knowledge parser subset:

```text
---
id: <category/slug>
title: <one line>
category: <existing category>
status: verified | assumed | refuted | superseded
updated: YYYY-MM-DD
by: <role/session/task>
read_when: <trigger>
evidence:
  - <command/output, source path/commit/run>
# optional: supersedes, tags
# pitfalls additionally: type, logic, occurrences, fix, promote; promoted_to when required
# anomalies additionally: detect, healthy, action
---
<fact/evidence/limits; refutation/replacement; no binding new instructions>
```

Pitfall occurrences retain `YYYY-MM-DD <task id> <one line>`; three distinct non-legacy tasks per type/logic
and promotion lifecycle stay I.21. F-knowledge is the human schema home; parser validates it. Additional migration
metadata/schema extension is deferred; do not insert unsupported fields into today's strict parser.

**F-results** — the results folder retains the question/setup/arm/metric/evidence-scope/audit overview,
run-grid/status record, run-record index, per-run measured fields/nulls, the run cards and raw-record
pointers. Keep the existing result schema; this change invents no metric, numerical default or rewrite of
historical results. The repository entry map names the results location and its existing file-name/schema
bindings; F-experiment-audit records accepted claim scope.

**F-rule-use** — phase-1 `rule-use-v1` JSON block/schema, with role enum
in the approved rule-evolution specification. The template is illustrative JSON, not a production rating:

````text
```rule-use-v1
{
  "schema": 1,
  "task_id": "<task-id>",
  "role": "<canonical role>",
  "source_commit": "<full source commit>",
  "feedback_revision": 1,
  "context_digest": "<selection-context SHA-256>",
  "uses": [
    {"key":"<permanent key>","revision":1,"epoch":1,"lifecycle":"established",
     "score":1,"reason":"<task-local help/friction>","action_ref":"<task action anchor>"}
  ],
  "pending": [
    {"key":"<selected pending key>","revision":1,"epoch":1,"outcome":"no-opportunity",
     "reason":"<why not applied>","action_ref":null}
  ],
  "none_reason": null
}
```
````

`uses` scores are integers -5..5, never booleans/floats. Applied pending also has one matching use/score/action
and `outcome:applied`; no-opportunity/conflict has no score. Empty uses requires nonempty none_reason. Preserve
per-row optional pinned source_commit, revision/epoch/lifecycle isolation and correction semantics from the approved rule-evolution
specification. It records applied-rule feedback only, never unused evidence.

**F-proposal** — exact field set from the approved rule-evolution specification: `schema:1`, `id`, `origin`, `owner`, `evidence_refs[]`,
`searched_keys[]`, `searched_type_logic[]`, `existing_principle_insufficient`, `exact_text_ref`,
`exact_text_digest`, `intended_home`, `roles[]`, `triggers[]`, `overlaps[]`, `conflicts[]`, `resolution_ref`,
`pending_key`, `before_after_budget_ref`, `approval_ref`, `review_ref`. `exact_text_ref` and `exact_text_digest` are two separate explicit fields. `resolution_ref` is null only when conflicts empty;
approval/review references are null until granted, and null prevents binding activation. I.24 owns the schema;
0.5 owns approval/pending policy. The approved rule-evolution specification defines the removed fields and algorithms.

**F-debug** — implementer documenting a diagnosis, used by debug skill:

```text
Failure class; deterministic reproduction command and output.
Minimal input/config/commit range.
| Hypothesis (3–5) | Falsifying observation/check | Evidence/result | retained / refuted / unchecked |
One-variable change; outcome; failed-fix count; escalation at three failures.
Regression/check evidence; cause/knowledge occurrence proposal; remaining uncertainty.
```

**F-run-card** — the existing machine schema of the run-card tool remains authoritative: block id/by,
claim/intent/label, retrodiction, predictions, control plans/results, tree/per-arm fingerprints, run ids/seeds,
scores/raw-read/post-check/comparison records. Create/update through that tool, never copy a hand-authored
JSON alternative into a role card. I.24 routes to the tool schema; the run rules map its commands, and experiment-plan
owns procedural order. No additional machine field or default is defined here.
