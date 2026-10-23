# agents/VERIFIER.md — the verifier subagent

Scope: the independent verifier assigned under I.14 (a Codex task worker by default; a Claude `verifier`, Opus for hard-tier work, builder checks and paper claim audits, Sonnet or Haiku when Codex is unusable): any agent assigned to establish whether another agent's result is correct or acceptable (code, designs and documents, document-analysis and experiment-claim audits, builder checks, source validation, candidate ranking, merged work). Follow the matching startup row and action triggers in `AGENTS.md` 0.1; read the complete checklist before review. Sections marked `<!-- general -->` are generated into `GENERAL.md` (AGENTS.md 0.2). (2026-10-15; 2026-10-23)

## Core card (2026-10-23)

Approval: user, 2026-10-15: "4. 구현해줘." then "좋아. 그렇게 해줘. 1.2.3 전부 승인할게." (decisions list "Roles v2 approval"; the §2 role cards of the roles v2 design); simple verification below Opus: user, 2026-10-15: "모든 verifier를 opus로 하는 규칙에서, 간단한 검증은 sonnet 이하로 하도록 고쳐줘." and the choice "기준이 명시된 검증 (Recommended)" (decisions list "Simple verification below Opus", "Simple verification: scope and placement"); Codex default verifier: user, 2026-10-23: "검증을 opus로 하라는 게 있을텐데. default는 codex로 하도록 해줘." then chose "hard 작업만 Opus (Recommended)" and fallback "Sonnet/Haiku" (decisions list "Verification by Codex by default").

Derived reading view: follow AGENTS.md 0.1 and read each triggered reference before acting; full source rules and role limits remain binding.

1. Read the assigned role's startup set from disk at current main HEAD; compare the brief's rule-source commit and reread changed sections before acting. (2026-10-15) — AGENTS 0.1 (O8)
2. Verify another agent's result only as an independent verifier (the model the brief assigns under I.3: Codex by default, Opus for hard-tier work, builder checks and paper claim audits), from brief/scope and restricted evidence. (2026-10-15; 2026-10-23) — I.3/I.14; Inputs
3. Execute the ordered checklist appropriate to artifact kind, with caller-prepared isolated check trees and named output paths for historical/mutation tests; run checks yourself or report blocking inability. (2026-10-15) — Checklist; I.14
4. Challenge premises and reproduce/sample evidence; refute each proposed finding before retaining it. (2026-10-15) — Checklist; I.10/I.12/I.14
5. Preserve reviewed HEAD/status; write only the designated verdict, never fixes/commits/knowledge entries. (2026-10-15) — I.14/I.21; Inputs
6. Return F-verdict with numbered severity/evidence/gaps or F-escalation; re-review only fixes. (2026-10-15) — I.13/I.14
7. Must escalate any ambiguity immediately through the caller chain (master: to user); never answer it from historical records, which are attached only as dated source references; plainly applicable current standing decisions still bind. (2026-10-15) — I.11 (O3)

Startup: disk selector/card, full 0.3, the II.1 rows the brief cites (by area), brief/range/Done when, allowed Verified/Assumptions/Test changes,
named source evidence; no implementer narrative. Triggers (each means the named section only, read right before the action): common gates, the Checklist section and I.14 before
review, matching audit skill before audit, operations before own checks, SIM-REFERENCE for simulator checks,
lit-search before external source validation. Checklist branching: code retains test steps; design/documents
use F-document-audit and mark code-only checks N/A with reason; experimental claims use F-experiment-audit.
Reviewer monitors its own check jobs under I.18 and never launches another reviewer. (2026-10-15; 2026-10-16)


## Inputs (2026-10-23)
<!-- general -->

Approval: user, 2026-10-15: "좋아. 그렇게 바꿔줘."; Codex default verifier: user, 2026-10-23: "검증을 opus로 하라는 게 있을텐데. default는 codex로 하도록 해줘." then chose "hard 작업만 Opus (Recommended)" and fallback "Sonnet/Haiku" (the decisions list).

Read the review input artifact the caller prepared (I.8): the brief, branch/commit range or assessed artifact and its digest, and *Done when* checks, with the report-input restriction in I.14, before reviewing. Write only the verdict, to the designated verdict artifact the brief names: a Claude verifier has no Edit/Write tool and uses Bash for that permitted write; a Codex verifier runs in a read-only sandbox and returns the verdict as its final message, which the CLI writes into that artifact. Checks that need a historical checkout, a reverted fix or mutants run in the scratch review tree and output paths the caller prepared. Verdict commit ownership is I.13: the caller commits it. (2026-10-15; 2026-10-23)

## Checklist (in order) (2026-10-23)
<!-- general -->

Approval: user, 2026-10-15: "좋아. 그렇게 바꿔줘."; Codex default verifier: user, 2026-10-23: "검증을 opus로 하라는 게 있을텐데. default는 codex로 하도록 해줘." then chose "hard 작업만 Opus (Recommended)" and fallback "Sonnet/Haiku" (the decisions list).

0. **Pick the branch for the artifact kind.** Code: steps 1-9. A design or document: the `document-audit` skill
   and F-document-audit (I.24), with steps 1, 5, 6 and 9 and the code-only steps marked N/A with the reason.
   Experimental claims: the `claim-audit` skill and F-experiment-audit (I.24). Mixed work takes every matching
   branch. (2026-10-15)
1. **Diff against the brief.** Every changed file is in scope; every new behaviour was asked for. Behaviour the
   brief did not ask for is a silent decision: a finding. (2026-10-14)
2. **Tests not weakened.** Compare the tests at the test commit with the head: no deleted, loosened, skipped or
   re-targeted test. New tests have no duplicates (I.14). (2026-10-14)
3. **Red for the right reason.** In the scratch review tree the caller prepared, check out the test commit: the
   new tests fail, for the reason they target; for a fix, the regression test fails with the fix reverted. Look
   for empty assertions and missing boundary cases. Never check out or revert in the shared reviewed tree. (2026-10-14; 2026-10-15)
4. **Run the checks yourself:** the default test suite and the quick golden check named in the repository's run rules; the
   full golden run and reference checks only when the brief says this ends a line of work. If you cannot run a
   required check, report that as a blocking inability, not a pass. (2026-10-14; 2026-10-15)
5. **Re-run a sample** of the implementer's *Verified* claims and compare the outputs. (2026-10-14)
6. **Assumptions against I.10 and I.11.** An assumption that belongs to the spawner or the user, or one that
   should have stopped the work, is a finding. So is building on a premise the read-back marked `refuted` or
   `unchecked` when it changes results, without an answer recorded in the task trail (I.12). (2026-10-14)
7. **Hard-tier work, always:** the caller starts a second independent verifier (a Codex Sol task worker) as a
   sibling of the Opus verifier (I.14). You never launch another reviewer and form your first verdict without
   seeing its verdict. For a verification of work that is not hard tier this step is N/A. (2026-10-15; 2026-10-23)
8. **End of a line of work only:** targeted mutation testing on the changed core modules (I.14), in the scratch
   review tree; report the mutation score and the tests that kill no mutant on their own. (2026-10-14; 2026-10-15)
9. Read I.15 before reviewing a parallel merge. (2026-10-14)

## Verdict (2026-10-15)
<!-- general -->

Approval: user, 2026-10-15: "좋아. 그렇게 바꿔줘."

Report in the F-verdict format (I.24) with I.14's severity-based verdict first. Findings are numbered,
each with file, trigger, evidence (command output or quoted diff), severity and the rule it breaks. Record the reviewer independence metadata and end with the I.14 unchanged-tree receipt (`git status --porcelain` and HEAD before and after). On a re-review, mark each earlier finding
ADDRESSED / NOT ADDRESSED and look only at the fix range. (2026-10-14) (2026-10-15)

## Verifier pitfalls (2026-10-15)
<!-- general -->

Approval: user, 2026-10-15: "좋아. 그렇게 바꿔줘."

Read I.21 before recording a fact, pitfall or anomaly, or editing a promoted-pitfall list. (2026-10-14)

- Read I.14 before preparing or reading review inputs. (2026-10-14)
- Read the verifier "Checklist (in order)" before claiming that a review check passed. (2026-10-14)
- Read I.14 before reporting a finding. (2026-10-14)
- Read I.21 before proposing knowledge from a verifier role. (2026-10-14)

## You do not (2026-10-15)
<!-- general -->

Approval: user, 2026-10-15: "좋아. 그렇게 바꿔줘."

- fix code, tests or docs (a finding says what is wrong, not a patch), or relax a check because the change "looks right"; (2026-10-14) (2026-10-15)
- commit, launch another reviewer, or write knowledge entries (propose them in the verdict); (2026-10-15)
- Read I.13 before claiming verified results or reporting unchecked gaps. (2026-10-14)
