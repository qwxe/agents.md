---
name: review
description: Assign independent verification (Codex by default, Opus for hard-tier work, builder checks and paper claim audits, I.3) of another agent's finished result and act on the verdict. Use for every correctness or acceptance check the upper tier orders under I.14 (verification on demand), routing document and experimental claims to their matching audit skills.
---
<!-- general -->

# Review by an independent verifier (2026-10-27)

Approval: user, 2026-10-15: "좋아. 그렇게 바꿔줘."; the procedure below: user, 2026-10-15: "4. 구현해줘." then "좋아. 그렇게 해줘. 1.2.3 전부 승인할게." (the decisions list); simple verification below Opus: user, 2026-10-15: "모든 verifier를 opus로 하는 규칙에서, 간단한 검증은 sonnet 이하로 하도록 고쳐줘." and the choice "기준이 명시된 검증 (Recommended)" (the decisions list); verification on demand: user, 2026-10-15: "그리고 검증은 manager/agent 등 상위 계층이 내리는데, 검증이 필요한지 판단해서 필요 없으면 하지 않아도 되는걸로." then chose "큰 변경만 필수 (Recommended)" (the decisions list); Codex default verifier: user, 2026-10-23: "검증을 opus로 하라는 게 있을텐데. default는 codex로 하도록 해줘." then chose "hard 작업만 Opus (Recommended)" and fallback "Sonnet/Haiku" (the decisions list).

0. Read I.13 before receiving the result; mechanically receipt its files/commits/outputs before assigning
   review. Read I.14 before preparing or opening review inputs. (2026-10-15)
   Then decide, as the upper tier, whether the result needs verification (I.14 *Verification on demand*:
   always for byte-exact core code, structural rule-file changes and claim audits of numbers entering a paper
   or a handoff). If not, record the skip with a one-line reason in the task trail and the report and stop
   here. (2026-10-15)
1. **Assign independent review.** The master or manager acting as caller uses spawn-agent and I.3/I.12/I.15
   to assign the verifier I.3 and I.14 name for every correctness/acceptance check of another agent's result:
   a Codex task worker by default (Terra medium; Luna medium for purely mechanical checks; read-only sandbox,
   verdict only), a Claude Opus `verifier` only for hard-tier work, builder checks and claim audits of numbers
   that enter a paper, and a Claude Sonnet/Haiku `verifier` in place of Codex Terra/Luna when Codex is unusable.
   Supply only the permitted immutable review input artifact and a separate designated verdict artifact;
   omit author explanatory narrative and other reviewers' first verdicts. Neither manager nor master
   self-reviews a result it authored. Master and manager receive and relay the independent verdict;
   they never substitute their own correctness/acceptance judgment. (2026-10-15; 2026-10-23) (2026-10-27)
2. **Select checks.** Use I.14 and the complete verifier checklist for the artifact kind: code review,
   document-audit or claim-audit. State whether the task ends a line of work so required full/reference/
   mutation checks are selected. The caller prepares any permitted scratch review tree and output paths;
   the verifier preserves the reviewed HEAD/status and writes only its designated verdict artifact.
   (2026-10-15)
3. **Hard-work independence.** The caller launches two independent verifier siblings, an Opus verifier and a
   Codex Terra task worker, with the same permitted evidence, without either prior verdict or author reasoning.
   Neither launches the other. Collect independent first verdicts before sharing them; preserve the I.14
   capped fix/re-review loop and F-verdict independence metadata. (2026-10-15; 2026-10-23) (2026-10-27)
4. **Track direct review.** Only the master sets its direct F-ledger item to `review` and maintains its
   I.23 heartbeat. A non-master caller tracks the verifier in F-helper in its own trail; a manager also
   updates F-unit. The launcher monitors its own direct item exclusively under I.18. (2026-10-15)
5. **Act on the verdict.** Perform I.13 receipt checks; the caller commits the verdict by path and links it
   from the task trail. PASS closes the item (master removes its done ledger row under I.17; non-master
   updates its own trail). PASS WITH NOTES forwards the notes; the user decides whether they become tasks.
   REJECT returns numbered findings to the implementer by SendMessage, or a new Codex call, within I.14's
   fix cap and fix-only re-review. A blocking finding prevents acceptance; disagreement or disputed reject
   goes through the master to the user, never majority voting. Managers report upward; only the master
   relays the verdict to the user. Receiving a verdict adds no self-review authority. (2026-10-15)
