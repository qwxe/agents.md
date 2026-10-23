---
name: document-audit
description: Audit decision-feeding document/source analysis and design against primary sources.
---
<!-- general -->

# Document audit (2026-10-23)

Approval: user, 2026-10-15: "4. 구현해줘." then "좋아. 그렇게 해줘. 1.2.3 전부 승인할게." (the decisions list); Codex default verifier: user, 2026-10-23: "검증을 opus로 하라는 게 있을텐데. default는 codex로 하도록 해줘." then chose "hard 작업만 Opus (Recommended)" and fallback "Sonnet/Haiku" (the decisions list).

1. Before accepting decision-feeding document/source analysis or design, the caller supplies the assessed
   artifact, its digest, the F-document-audit claim/source table and source snapshot as the review input
   artifact under I.14. Exclude author explanatory reasoning; the assessed document's own prose remains
   permitted evidence. (2026-10-15)
2. A fresh independent verifier (I.3: a Codex Sol task worker by default, Opus for hard-tier work) opens the
   primary source passages and checks provenance, applicability, inference boundaries, contradictions and design
   completeness. Record counterevidence and attempted refutation in F-document-audit; mark unavailable sources and
   unsupported premises explicitly. (2026-10-15; 2026-10-23)
3. Return F-verdict in the designated verdict artifact with the per-claim F-document-audit table and
   verification gaps. Mixed experimental or numerical claims also require claim-audit and
   F-experiment-audit; do not waive controls or fabricate run ids, cards or statistics for document claims.
   The caller receipts, commits and routes the independent verdict under I.13/I.14. (2026-10-15)
