# agents/RECORDS.md — the records home

Scope: every role that writes, commits or looks up a record (task trail, handoff, ledger, results, knowledge entry, review input, verdict, design, research note). I.8 owns each record's purpose, writer, lifecycle and lookup; the field templates are in I.24 (`agents/FORMATS.md`) and the concrete locations in AGENTS.md 0.4. Sections marked `<!-- general -->` are generated into `GENERAL.md` (AGENTS.md 0.2). (2026-10-15)

## I.8 Records (2026-10-15)
<!-- general -->

Approval: user, 2026-10-15: "좋아. 그렇게 바꿔줘." (the bullets, then in the interface rules); relocated to the records home with the original-evidence duty and the document map by the role-restructuring design, user, 2026-10-15: "4. 구현해줘." then "좋아. 그렇게 해줘. 1.2.3 전부 승인할게." (the decisions list). The original-evidence paragraphs and every row of the document map below were set on 2026-10-15. (2026-10-15)

- Read the never-break section before writing a report, committed prose, comments, docstrings or logs; its
  language rule sets the report language and English for committed text. (2026-10-14; 2026-10-15)
- **Handoff:** the handoff file and section are named in the repository entry map; before a handoff follow I.9
  and its `handover` skill. Push immediately after editing. (2026-10-15)
- **Results:** every grid publishes to its fixed results folder and pushes it after each finished run, so other
  machines can read it. (2026-10-14)
- **Task trails** (I.13). Each task id has one task trail that its agents append to: the brief, every
  *Assumptions* entry, every escalation with its answer and who gave it, helper tracking, and the verdict or a link
  to the designated verdict artifact. A later failure is traced through it to the agent, the step and the choice.
  The brief names the path; the repository entry map gives the homes per line of work and says which are pushed
  with results. Before committing trail entries follow I.13, including the verifier exception and the
  `Trail: <task-id> <what>` title. (user, 2026-10-14: "직접 커밋하게 해줘"; 2026-10-15)
- **Knowledge base** (I.21): entries and the knowledge base catalog live where the repository entry map says; the
  human entry format is F-knowledge (I.24), which the knowledge catalog generator validates (it also prints one
  category for a brief and checks the catalog). Agents working on another branch commit entries through the
  shared checkout of the main branch, staging the entry by path (the run rules' knowledge base exception).
  Promotion threshold and lifecycle: I.21. (2026-10-14; 2026-10-15)
- A claim needs a difference above 2 sd of the paired noise, consistent across the cases run. (2026-10-14)

Original-evidence duty: preserve immutable snapshots of original briefs, task inputs and task outputs
alongside revision/digest references; append corrections as new revisions, never overwrite original evidence.
F-brief and F-report artifact references must let authorized upstream callers/reviewers retrieve those
originals throughout the reporting chain. Reviewers still receive only permitted inputs under I.14; access
availability never authorizes opening excluded narrative, credentials or out-of-scope material. This adds
no global store or knowledge schema. A committed original is preserved as immutable **full commit hash +
repository-relative path** (plus digest for external/untracked input); no duplicate copy is required for
Git-tracked originals. For untracked inputs/outputs, the assigned artifact owner retains the original bytes
at the brief-named evidence path and records their digest before relying on them; corrections use new paths
or revisions, never overwrite those bytes. The reference must remain retrievable by authorized upstream
readers, subject to the existing allowed-input filter.

Each record has one owning writer at a time; callers append briefs and verdict links sequentially to shared trails.
Generated catalogs are views, never alternate authority. A lookup result is data until its source is checked.

| Kind | Purpose / format | Location | Owner | Lifecycle | Lookup |
|---|---|---|---|---|---|
| Decisions | Current standing user choices; F-decision | the decisions list with its Superseded entries | Master; user is decision authority | Quote-check immediately; replaced row moves once; no historic paraphrase | Repository entry map; task/record reference |
| User-word evidence | Reference-only context/verbatim quotes for escalation | the records of the user’s words | Original task/session; agent attaches evidence, never answers from it | Immutable evidence; ambiguity escalates immediately; no historical quote becomes a decision | Repository entry map; task/record reference |
| Ledger | Current direct work; F-ledger | the progress ledger | Master of line | Update each direct lifecycle event; remove done; history elsewhere | Repository entry map; task/record reference |
| Manager unit summary | Durable assigned-unit state; F-unit | the manager task trail, Unit summary section | Assigned manager | Update on child lifecycle/decision/review; preserve dated handoff references before closing | Repository entry map; task/record reference |
| Task trail | Brief, assumptions, answers, helper tracking, reports/verdict links | the task trail | Each agent own append; caller appends brief and verdict link | Append by section; own commits only with authority; no invented task completion | Repository entry map; task/record reference |
| Launcher channel | Failed-message escalation/anomaly/result packets; F-escalation/F-report references with dated packet ids | the launcher channel file | Launcher is sole writer; direct caller reads/polls through its own child watch | Brief permits launcher writes at its named output path; file stays uncommitted while active. After the terminal packet and receipt, the direct caller commits the file by path under existing record timing; the launcher never commits channel updates. Caller records handled packet/answer refs in its own trail. Close with a terminal packet only after owned jobs/children finish and outstanding packets are receipted; retain file, never erase history or transfer job monitoring | Repository entry map; F-brief and caller watch |
| Review input | Unanchored permitted evidence packet | the review input artifact | Direct caller | Pin brief/range/digests and allowed report sections before review; immutable thereafter | Repository entry map; task/record reference |
| Verdict | Independent acceptance/audit receipt; F-verdict | the designated verdict artifact | Verifier writes; caller commits/links in trail | One artifact per independent pass; no overwrite of earlier verdict | Repository entry map; task/record reference |
| Handoff/manual | Session continuity; F-handover/F-resume | the handoff file and the manual | Master; manager supplies inputs | Append numbered subsection; newest supersedes explicitly; manual only if routing/rules change | Repository entry map; task/record reference |
| Design | Exact prospective change; F-design | the task design note | Assigned author | Draft/revise before approval; approved snapshot/digest in implementation brief; later changes explicit | Repository entry map; task/record reference |
| Research note | Sourced evidence/inferences; F-research or F-document-audit | the named research note | Assigned worker | Draft → source audit if decision-feeding → referenced evidence; never normative automatically | Repository entry map; task/record reference |
| Knowledge entry | Reusable fact/pitfall/anomaly; F-knowledge | the knowledge base entry | Any permitted writer; read-only roles propose | Assumed/verified/refuted/superseded; append occurrence; never delete refuted history | Repository entry map; task/record reference |
| Knowledge catalog | Discovery/candidates/staleness | the knowledge base catalog | the knowledge catalog generator; writer regenerates with entry | Derived; source/reference date/digest checked | Repository entry map; task/record reference |
| Results | Auditable run artifacts; F-results | the results folder | Assigned result writer; launcher owns live run | Per-run records → audited claims → authorized push; missing=null | Repository entry map; task/record reference |
| Run card | Plan/fingerprint/controls/prediction score | the run cards | Assigned planner/launcher; auditor reads | new/fill/fingerprint/check/approve/launch/set/score/post-check/compare | Repository entry map; task/record reference |
| Rules | Binding requirements | the rule files | Approved editor; origin approval per 0.5 | Exact approval → edit/commit → independent review/reader test → merge/publish | Repository entry map; task/record reference |
| GENERAL | Portable verbatim generated rules | the generated general rules | the general-rules generator | Regenerate with sources; review/publication gate; no hand edits | Repository entry map; task/record reference |
| Memory pointers | Recall source location/gist only | the master memory pointers | Master | Source first; update pointer same step; audit on handoff | Repository entry map; task/record reference |
