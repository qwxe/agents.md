# agents/RESEARCH.md — research context: lower-tier partial eviction

Scope: agents on research branches. Section ids (II.x) are kept from the old single-file AGENTS.md, so references to "II.1" still work. Read II.1 always; other sections when the brief names them.


Applies to agents on research branches. Research code is **not on `main`**: it lives on `explore/rate-wl-phase3`
plus feature branches (II.3).

## II.1 Decisions in force (2026-10-15)

Every standing user decision, newest wins. Source = where the reasoning (why) is recorded; a new row also
states its why in one clause. Superseded and ruled-out entries are reopened only when the user names them (I.10). (2026-10-14)

**Row format** (user, 2026-10-15: "좋아. 추천한대로 해줘. 그리고 B 라우터는 dynamo로." (one turn, session c7bfd3df, 2026-10-14T15:15Z)). Every new row carries the user's words verbatim, with
the date and the source (a trail path or a session id; the master appends it by the light path, AGENTS.md 0.5).
A decision that rejects an option names the rejected option and its reason, and says it is reopened only when the
user names it. Existing rows are not rewritten except to add a missing quote. Session ids below are Claude Code
session transcripts (`~/.claude/projects/-home-asd-LLMServingSim/<id>.jsonl`). The date of a row is the KST
(UTC+9, the user's local) date of the turn; the source gives the session id and the UTC stamp, e.g. a turn at
15:15Z is dated the next day. (2026-10-15)

| area | decision | date | source |
|---|---|---|---|
| Role and model | Resolve the assigned role independently of the model/provider, so GPT/Codex does not imply worker duties; AGENTS.md 0.1 is the canonical reading rule. Existing roles and I.3 routing remain unchanged; no standing decision is superseded. | 2026-10-14 | User: "3개밖에 밖에 역할이 없나? 모델 역할을 구분하도록 하기만 해줘."; AGENTS.md 0.1 |
| Worker model routing | Sol medium by default; Luna for fully specified mechanical work; Opus only for the explicit hard criteria in I.3. Builder checks and reader tests default to Sol. Replaces the broad judgement/question and higher-tier-on-ambiguity criteria, to avoid unnecessary Opus spawns. | 2026-10-14 | User: "좋아. gpt에 대한 기준을 좀 더 명확히 해줘."; I.3 |
| Codex fallback | When Codex is unusable (auth or availability failure), Sol-tier work goes to a Claude Sonnet subagent (medium) and Luna-tier work to a Claude Haiku subagent; the hard tier stays Opus. See I.3. | 2026-10-14 | User: "codex 사용이 불가능한 경우 이전처럼 sonnet 이하를 사용하는 걸로."; I.3 |
| Paper themes | Three themes, all on the hole structure: (1) the `rate` cost, (2) CP-degree-aware eviction cost, (3) CP partition. The router is not a theme. | 10-13 | `EX/PAPER-ALGORITHM.md` |
| Framework principle | The paper's system is a real framework configuration **as shipped** plus our eviction policy only. Features no framework has are out of scope. "Minimal" is conceptual: the implementation may be large (e.g. patching Mooncake master's eviction order). | 10-14 | HANDOFF 10.13 |
| Hole lookup | The lookup that reuses blocks past a miss is part of our eviction and is **always** implemented (one lookup-function change), although SGLang/LMCache stop at the first miss. | 10-14 | — |
| Claim 1 | `rate` uses session behaviour only (tool gaps, decode, p_end), never router rules, move fractions or load; load/routing effects belong to claim 2. Every chunk is priced by its session's latest request (`RATE_SESS_STATE=1`). | 10-13 | `R/rsess/NOTES.md` |
| Claim 2 | Cost = expectation at eviction time with **windowed** W/lambda/rho **averaged over all instances of the reader's CP degree** (eviction != execution), so the cost depends only on the CP degree, not on which instance the reader lands on. The reader's group (CP degree) is still fixed at eviction (an eviction that crosses a threshold re-homes the session; unchanged from 10-13/14). No part split, no burstiness model; the argument only has to refute "the current burst carries over to when the eviction's cost lands". Why: the user chose the per-degree average so the instance need not be known. Replaces the own-instance queue (Superseded). | 2026-10-15 | User: "cp degree 전체의 평균으로 해줘. 그러면 cp degree에만 의존하고 인스턴스는 몰라도 되잖아." (session 635beb74); earlier quotes: 2026-10-14 "즉 eviction은 바로 일어나는게 아니기 때문에 평균을 쓰는게 정당화된다. 현재의 burstiness 를 고려하지 않아도 괜찮다. 이런 논리로 가야 해.", 2026-10-15 "지연으로 bursty 영향이 사라지는 게 아니라 "현재의 burstiness가 eviction때까지 영향을 미친다" 라는 주장을 반박하기만 하면 돼."; evidence `R/qacf`, `R/evlog`, `R/claim2chk` |
| Claims 2-3 experiments | Run the claim-2 (CP-degree-aware eviction) and claim-3 (hole CP partition) experiments on **both** configurations A and B; compare both deployment variants for mixed CP degrees (mixed CP1+CP2 prefill within 8 GPUs, and more GPUs), both partitioners (per-hole zigzag and c2e, concatenated zigzag as baseline), and both saturated and unsaturated load for the burst check. Merge scope of the CP code is still under discussion. Why: the user chose to compare both in each case. | 2026-10-15 | User: "1,3,4 는 둘 다 비교하는 걸로. 2는 좀 더 논의해보자." then, asked A or B, "둘 다로." (session 635beb74); the reading of "1,3,4" (which two variants) is the master's, stated to the user and not contradicted |
| CP timing evidence | Claims 2-3 are evaluated **in simulation only**: CP2 ranks priced from the existing H100 Qwen tp1 profiles plus the simulator's CP communication model; no measured multi-GPU CP2 profile is required before running. Rejected for now: waiting for a measured H100 CP2 validation. Why: the user chose simulation for everything. Reopened only when the user names it. | 2026-10-15 | User: "일단 모두 시뮬레이션 기반으로 하자." (session 635beb74); design note `R/design/T20261015-cp23.md` Q8 |
| Claims 2-3 stage 1 | Stage 1 has **no re-home**: CP compute and partition (claim 3), the same-degree claim-2 cost, and a session's CP degree chosen at its first request and then fixed. Group-crossing re-home (KV move, reservation, contention) is deferred to a stage 2, decided after stage 1 results. Why: re-home brings most of the open design questions (builder check of `R/design/T20261015-cp23.md`). | 2026-10-15 | User: "1단계에서는 재배치를 하지 않기 (권장) 이렇게 해줘." (session 635beb74) |
| Claims 2-3 stage 1 design | (1) A session's CP degree is set at its first request by a miss-token threshold T: miss > T -> CP2; T is calibrated once by a stated method before any arm result and frozen for all arms; within the group the shipped router (A consistent_hash, B Dynamo) picks the instance. This is a stated exception to the framework principle (group assignment is ours). Rejected: degree by session hash. (2) Deployments 8 GPU (CP1 + CP2 + 5 decode) and 12 GPU (2 x CP1 + 2 x CP2 + 6 decode), total CPU tier fixed at 256 GiB in both. Rejected: 128 GiB per instance. (3) superseded by the row Claim-2 cost terms. Reopened only when the user names it. | 2026-10-15 | User: "좋아. threshold T를 적당히 정하는 방법으로 해줘." (session 635beb74), answering the three recommendations; (2) and (3) are the master's reading of "좋아" as accepting the recommended options, stated to the user |
| Claim-2 cost terms | Victim score = rate_sum score x [1/kappa_d] x [M_d], each bracket a separate on/off option, so four variants: none (= claim-1 ours), kappa only, M only, kappa and M. kappa_d = calibrated recompute speedup of CP degree d; M_d = 1 + lambda_d W_d from the 180 s windowed averages over the instances of degree d (finite at rho >= 1). Rejected: the form 1 + lambda (W + S)/(1 - rho) (diverges at rho >= 1). Why: the user wants both terms in, with removal as the ablation. | 2026-10-15 | User: "일단 둘 다 넣고 빼는거를 abalation으로, 즉 4개를 각각 옵션으로 주는 걸로 해보자." (session 635beb74), answering the master's options (kappa only / kappa x (1 + lambda W) / old M form); the M form 1 + lambda W is the master's recommendation, not contradicted |
| Claim-2 M and kappa | Refines the row Claim-2 cost terms. (1) M has two forms, both run as ablation arms: M_lw = 1 + lambda_d W_d (that row) and M_queue = 1 + mean over the degree-d instances of N_i, N_i = 180 s time average of the number of requests at instance i whose prefill is not finished (waiting or partly prefilled), counted in requests, idle instances included, a logical CP2 counted once. Why: added work delays every request that finishes after it, whatever the scheduling order, so no FCFS or queueing-model assumption. Variants become kappa {off,on} x M {off, lw, queue} = 6. (2) kappa_d = d x eta_d, the wall-clock recompute speedup of degree d over CP1 (same compute split over d GPUs); eta_d = a rough average parallel efficiency (rank imbalance plus CP communication) from the calibration. Rejected: GPU-second cost (c/eta). | 2026-10-15 | User: "좋아. M_d에 대해서는 이것도 권고안이랑 기존이랑 둘 다 ablation을 해보자. k_d는 그렇게 해줘. η_d는 대략적인 평균값으로." (session 635beb74), answering the master's M_d recommendation (unfinished-prefill count, 180 s average, requests) and kappa_d = d eta_d |
| Claim-2 eta per partitioner | eta_d (row Claim-2 M and kappa) is calibrated separately for each partitioner (zigzag, c2e, per-hole zigzag): the simple mean of eta over the calibration training shapes for that partitioner. Rejected: one common eta for all partitioners (would erase the partitioner difference in imbalance). | 2026-10-15 | User: "partitioner마다 따로 둬줘." (session 635beb74), answering the master's recommendation (per partitioner; mean over training shapes) |
| Claims 2-3 stage 1 U5, U7 | (U5) RATE_PARAMS are extracted from each cell's own LRU run (configuration x layout x partitioner) and shared by all six cost variants of that cell. Rejected: fixing the main zigzag LRU params for every partitioner. (U7) Service diagnostic: at every actual eviction store, for each reader of the victim, the before/after prediction (design note T20261015-cp23 section 4.2); at that reader's later first admission compare with the actual worker and observed state, reporting worker-choice error and intervening cache-state error separately. Rejected: fixed sampling or separate diagnostic runs; the master's alternative (log score terms on a hash-chosen sample). | 2026-10-15 | User: "둘 다 a로 해줘." (session 635beb74), answering builder check T20261015-cp23-builder2 U5 and U7 options (a) after the master recommended (b) for U5 and its own (c) for U7 |
| Claims 2-3 stage 1 U2, U3, U4, U6 | Builder check T20261015-cp23-builder2 options (a): (U2) eta/calibration service = one request run alone to completion at the real step budget (uncontended), same condition for paired marginal runs. (U3) the partition cost surrogate (a, b) = the coefficients of the CP1 service/marginal fit, intercept excluded from partition cost. (U4) the A-control gate checks order preservation among ordinary candidates only; keep the finite protection score unscaled and report cases where a scaled ordinary score crosses it. (U6) the Decode capacity row (2P + 3D tp2) applies to the FI overflow line only; CP23 keeps E8/E12. | 2026-10-15 | User: "그대로 해줘." (session 635beb74), answering the master's question whether U2, U3, U4, U6 follow the recommended (a) |
| Claims 2-3 stage 1 impl Q1-Q5 | Implementer read-back T20261015-cp23-impl: (Q1) with EP = 1 the MoE expert blocks carry no expert communication: the ASTRA CP conversion lowers them to ordinary compute rows. (Q3) CP ring traffic between the ranks of a CP2 instance runs on the cluster network link (the FI config link), not NVLink. Rejected: NVLink for CP. (Q4) CP2 recall: PCIe per GPU, the network link shared per host. (Q5) calibration oracle: one simulation per manifest with requests spaced so they do not overlap; P/D send rows included in S_d; recall charged 0 in the oracle; run a subset first and report its cost before the full calibration. | 2026-10-15 | User: "1. EP = 1이라 없어. 3. CP 사이에선 network를 타는걸로. 4. 권고대로. 5. 권고대로 일부만 돌려." (session 635beb74), answering the master's relay of read-back Q1, Q3, Q4, Q5; Q1 read as option (a) lower to compute, Q3 as option (a) keep the cluster link |
| Claims 2-3 stage 1 E1-E3, CP link | Implementer escalation T20261015-cp23-impl (calibration subset): (CP link) the CP ring between the ranks of a CP2 instance runs on its own 400G network link, 50 GB/s, latency 20 us as now; P/D transfers and remote L3 recall keep their current links. Supersedes the 16 GB/s CP link of row Claims 2-3 stage 1 impl Q1-Q5 (Q3), keeps "network" for CP. Rejected: 400G for the whole cluster network (would change P/D and recall and break comparison with the FI results). (E1) the recompute service model becomes step-aware (per-step fixed cost amortized plus token terms), the marginal gate is aggregated per shape or step, and the oracle's P/D send carries only the newly computed tokens. (E3) physical chunk = 128 tokens (LT_CHUNK_TOKENS of the FI runs). | 2026-10-15 | User: "400G network로 가정하자 그러면." then "진행해줘." (session 635beb74), answering the master's options (CP link only recommended; E1 step-aware model and E3 128 recommended, stated as the default if no objection) |
| Claims 2-3 stage 1 E4, kappa shapes | Implementer escalation E4 (rev4 step-aware fit still fails held-out p90): (1) the fit leaves the score path: kappa_d is computed from oracle-measured services (eta(R) = O_1(R)/(d O_d(R))), T from interpolated measured cold services; the fit is used only for the c2e partition weights and the U7 diagnostics, its errors reported, not gated. (2) kappa_d averages eta over the calibration shapes whose miss length is >= T only (the region where CP is used). Why: "짧은 구간은 원래 CP를 쓸 이유가 없으니까 괜찮아. miss length 기반으로 CP가 동작하니까." (3) Results report the later turns of CP2 sessions separately (their recompute time and realized versus predicted kappa) as the stage-1 limitation of the frozen degree. Rejected: whole-grid average; workload-weighted average; adding a segment term to make the fit pass (rev5 option a). | 2026-10-15 | User: "짧은 구간은 원래 CP를 쓸 이유가 없으니까 괜찮아. miss length 기반으로 CP가 동작하니까." then "1번대로 해줘." (session 635beb74), answering the master's options (kappa shapes 1/2/3, with (b) fit out of the score path and separate later-turn reporting as the stated recommendation); (1) and (3) are the master's reading of "1번대로" as accepting that recommendation |
| Claims 2-3 stage 1 pass-Q, c_base, full calibration | (1) Pass-Q is not compared in stage 1: pass-KV ring only. Why (user): pass-Q has no imbalance, and it does not help where KV is small and Q is large (miss above T). (2) The RTX/Llama coefficients of c_base `_chunk_s` are ignored (not checked or replaced in stage 1). (3) The full calibration (card `R/results/cp23-calib/cards/cp23-calib-full.json`) is approved and launched now, while the verifier review is still running; it is rerun if the review changes the code it measures. | 2026-10-15 | User: "pass-Q 는 imbalance가 없어. 그리고 KV 가 작고 Q가 큰 (>32K=T) 소용이 없고. 일단 무시하고 CP를 돌려봐. RTX/Llama 계수는 무시해." (session 635beb74), answering HANDOFF 10.18 open questions 2 and 4 and the full-calibration approval request; (3) "launched now ... rerun if the review changes the code" is the master's reading of "CP를 돌려봐". Note: the user wrote T as 32K; the rev5 subset calibration gives T = 3277 tokens (told to the user). |
| Claims 2-3 stage 1 T and layout | (1) T is set to 10K tokens for now (fixed), replacing the workload-calibrated T of the design note (section 4.1 GPU-second share; rev5 subset T = 3277). (2) The layout changes from E8/E12 to two CP1 instances and one CP2 instance; details (decode count, CPU-tier split, whether E8/E12 are both replaced) are open. (3) The user asked that T be judged from all requests, not only first requests; how assignment uses T (first request frozen versus each request by its miss length) is open. Rough evidence (master, not audited): FI-A r0.15 per-request miss, 2 CP1 + 1 CP2, T about 1.8K would balance work. | 2026-10-15 | User: "첫 요청이 아니라 전체 요청을 봐야 하고, CP=1인 GPU를 몇개 둘거야." then "T는 우선 기존 run을 보고 cache miss의 분포가 어땠는지 봐서 그걸로 대략적으로 추정해봐. 엄밀하지 않아도 괜찮아. 그걸로 2 * CP1, 1 * CP2 상황에 적용해서 분배해봐." then "1. 배치를 바꿔야 돼. 2. T는 우선 10K로 나누자." (session 635beb74) |
| Claims 2-3 stage 1 T by sweep | T is chosen by a simulation sweep on the new layout (2 CP1 + 1 CP2) using measured TTFT, which includes all computation (attention etc.), communication and queueing; replaces "T = 10K for now" and the GPU-second-share calibration of T. Master proposal accepted: LRU arm, T in {2K, 5K, 10K, 20K}, rates 0.15 and 0.20, after the review fixes and the layout change are implemented; the run block goes to the user for approval with its cost. | 2026-10-15 | User: "T 를 어떻게 구했는진 모르겠는데, attention cost 등 computation cost를 전부 고려해야 해. TTFT토 고려해야 하고." then "좋아. T를 sweep으로 한번 정해줘." (session 635beb74), answering the master's sweep proposal |
| Hardware | H100 (`RWL_HW=H100`, H100NVL-long profiles). Decode instances `mem_size` 141 GB (H200-class) so decode capacity does not bind. | 10-12/13 | `R/fi/NOTES.md` |
| Model, layout | FI runs: Qwen/Qwen3-30B-A3B-Instruct-2507, tp1, **2P6D** (8 GPUs; 2P is the floor under "prefill takes as much load as possible, decode never saturates"). | 10-13 | `R/models/NOTES.md`, `R/fi/DECODE-NEED.md` |
| Configurations | Run **both**. **A:** prefill `consistent_hash` (vllm-router, session sticky) + private CPU tier 128 GiB per prefill instance. **B:** SGLang HiCache + Mooncake shared L3 (one pool, 2 x 128 GiB) + per-instance staging L2 = 2 x device KV pool (SGLang `--hicache-ratio 2`, LRU, L3 ⊇ L2) + Dynamo v1.5.1 KV router `--shared-cache-type hicache` (0.5). Our eviction acts on A's private tiers and on B's shared L3. | 10-14 | HANDOFF 10.13 (the B router: user 2026-10-15 "B 라우터는 dynamo로.", session c7bfd3df, see the next rows) |
| Routing of A | Prefill `consistent_hash` (session sticky); decode least-load by **tokens**. The same for the DeepSeek runs. Why: the router discussion was already held and is not repeated. | 2026-10-14 | User: "라우터는 prefill은 stikcy, decode는 token에 대해서 least load야. 이것도 이미 했던 논의야 deepseek는 그렇게 해." and "라우터는 A는 이전에 했던 대로." (session c7bfd3df, 2026-10-14T14:49Z and 14:51Z) |
| Routing of B | Prefill router = Dynamo v1.5.1 KV router `--shared-cache-type hicache`; decode least-load by tokens as above. Why: the user chose Dynamo for B. | 2026-10-15 | User: "B 라우터는 dynamo로." (session c7bfd3df, 2026-10-14T15:15Z) |
| Routing of A: first assignment | Prefill stays session sticky, but a session's first request goes to an instance chosen by load; every later request of the session follows it. Replaces the hash placement (`consistent_hash`) of the row "Routing of A" for the prefill; decode unchanged. Load = outstanding prefill tokens of the instance (queued and running requests' prefill tokens not yet computed); user chose "남은 prefill 토큰 (Recommended)" (2026-10-15). A request not yet admitted counts only its miss tokens: when it is queued at its instance, that instance's reusable tokens are looked up without recording (`lookup_with_holes(..., record=False)`) and subtracted; after admission the actual remaining work counts. User chose "적중분 빼고 셈 (Recommended)" (2026-10-15, T20261015-sticky-load Report 1). Why: the user judged the hash-only router wrong after the r0.15 one-instance collapse. | 2026-10-15 | User: "그러면 load를 보는 걸로 바꿔줘. router가 이상하니까>" then, on the options, "sticky인데 처음에 세션을 할당할 때만." (session 5ff874eb, 2026-10-15) |
| Decode lower tier | Use `--no-decode-lower-tier` whenever a configuration has no decode CPU tier (A, for example): clocks and CSVs are identical (checked on A, `R/nodec/VERIFY.md`) and long runs get faster. Why: runtime only. | 2026-10-14 | User: "a없애는 게 이미 실행 옵션으로 있지 않아? run이 긴 걸 최적화한다고." (session c7bfd3df, 2026-10-14T14:49Z). The user's approval of the switch for long runs is recorded in `R/results/fi-A/README.md` ("user approved", 2026-10-14 ~18:45); that quote was not found on this machine |
| Configuration Bd | B plus the decode hosts' CPU memory in the prefill pool: L3 = 8 x 128 GiB = 1 TiB, used by **prefill only**; decode has no CPU tier (so `--no-decode-lower-tier`); everything else as B. Run for the Qwen model. Rejected option: decode instances using the pool; the user's design is prefill using the decode hosts' memory. Reopened only when the user names it. | 2026-10-14 | User: "qwen 모델에 데해서 B를 decode pool을 추가해서 돌려줘" (session c7bfd3df, 2026-10-14T13:54Z), then "decode가 pool을 쓰는게 아니라 prefill이 decode의 pool을 쓰는거야." (2026-10-14T14:17Z); design note `R/design/T20261014-bdec.md` |
| DeepSeek rate | DeepSeek-V2-Lite on configuration A: option 1, raise the session rate (LRU probe at r0.5 and r0.75). Why: the LRU probe at r0.15 and r0.25 showed no cache pressure on the 128 GiB tier. | 2026-10-15 | User: "1번. rate를 높여줘." (session c7bfd3df); `R/tasks/T20261014-dsA.md` Report 4 |
| DeepSeek grid | DeepSeek-V2-Lite on configuration A: r0.5 / 0.75 / 1.0 x the 5 arms (LRU, Belady, ideal, AsymCache, ours), CPU tier as is (128 GiB). Rejected options: CPU tier about 41 GiB; stopping. Why: the user approved the recommended option (HANDOFF 10.14 question 2). Reopened only when the user names it. | 2026-10-15 | User: "2. 좋아." (session 168c3bb8); `R/HANDOFF.md` 10.14 question 2 |
| Bd decode routing | For the Bd decode overflow (r>=0.15), route decode by least-load on the **actual KV in use** per decode instance (prompt + generated tokens), not on booked prompt blocks (`load_tokens`). Rejected options: request-count least-load (`--kv-decode-policy load`); 4P+4D with decode tp2; decode KV fp8; accepting the overflow. Why: the user chose actual-KV least-load. Reopened only when the user names it. | 2026-10-15 | User: "1. decode는 routing을 least load 로 바꿔서 실행해줘." then "그래서 답변은 Least-load by actual KV in use를 써." (session 168c3bb8) |
| Decode capacity | **2P + 3D(tp2)** on the same 8 GPUs (2 prefill instances tp1, 3 decode instances tp2; decode KV about 6.45M tokens vs 4.59M in 2P6D), after fixing the simulator's mixed-TP topology (`config_builder._compute_network_dims` builds `[1,10]` for a mixed layout, `R/results/fi-A4p4d/`); first one run, configuration A, LRU, r0.15. Rejected: 4P + 2D(tp2) (less decode KV than 2P6D: 4.30M tokens); a decode admission queue; accepting the overflow. Why: the user chose option 1. Reopened only when the user names it. | 2026-10-15 | User: "1번으로 해줘." (session 168c3bb8), choosing "2P + 3D(tp2), 같은 GPU 8장" |
| TP link (mixed TP) | In mixed-TP layouts (2P + 3D(tp2)), the TP collectives inside a tp2 instance run on an NVLink-class link; P/D transfers stay on the cluster link as in 2P6D. Rejected: the cluster link for TP (option a); NVLink for the whole first topology dimension (option c, would speed P/D too). Why: the user chose NVLink for TP. Reopened only when the user names it. | 2026-10-15 | User: "TP 통신 링크는 NVLINK로 둬." (session 168c3bb8); `R/tasks/T20261015-mixed-tp.md` Report A Q1 |
| ASTRA-Sim tp2 leak | The backend memory leak in tp2 collectives (about 16 MB per simulated second; `R/tasks/T20261015-mixed-tp.md` Report A2) is audited and fixed in a separate build path (e.g. `.wt/astra-build-mtp`), not in the shared build; every reference clock is rechecked on it. Rejected: replacing the shared build (conflicts with running grids); raising `ulimit -v` (a full run would need about 200 GB). | 2026-10-15 | User chose option "별도 빌드에서 수정 (Recommended)" (session 168c3bb8, AskUserQuestion) |
| NVLink latency | NVLink link latency 1800 ns (secondary source, unverified; the results README states the bias); bandwidth 279.4 GiB/s per direction (`R/design/T20261015-mixed-tp.md` section 11). | 2026-10-15 | User chose option "1800 ns (Recommended)" (session 168c3bb8, AskUserQuestion) |
| Decode routing | Least-load by **tokens** (`load_tokens`: booked unique prompt blocks, Dynamo-style), in A and B. No decode admission queue: an overflow still fails the run. | 10-14 | `R/results/fi-A/README.md` "User decisions 2026-10-14" item 2 |
| Bandwidth | PCIe 50 GB/s per GPU; network 100 Gbps = 12.5 GB/s. B's remote-node reads: min(PCIe, net) + 10 us per remote chunk; same-node reads at PCIe. | 10-14 | — |
| Arms | LRU, Belady (TTL 0), ideal (infinite tier), AsymCache (plain CostAwarePool), **ours = `rate_sum`** (`RATE_POLICY=rate RATE_HOLE=after RATE_SEG=sum`, `RATE_SESS_STATE=1`). `rate_tail` is an ablation. Quick checks: LRU vs ours only. | 10-13 | `R/results/fi-pd/README.md` |
| Router overlap | `--router-overlap-past-holes` reports reusable tokens past holes to an unchanged router, identically for every arm; not claimed. | 10-13 | — |
| Arrivals, seeds | Sessions start by Poisson at a controlled rate and keep their recorded tool gaps; the session **order is random** (permuted). **One seed** (1); no seed mean +- sd. | 10-13/14 | `R/fi/mkds2.py` |
| Run length | Every run goes **to completion** (FI has no steady state). Headline = full-run TTFT; also report (A) TTFT of arrivals in [1800 s, t1] with per-arm counts and (D) all requests of sessions started in [1800 s, 0.75 t1]. | 10-14 | `R/fi/LOADTIME.md` |
| Load knob | Session arrival rate only. FI grid rates 0.1 / 0.15 / 0.2 (all arms) plus 0.05 and 0.25 (LRU, ours). | 10-13/14 | HANDOFF 10.12-10.13 |
| Workloads | II.6. | 10-12/13 | — |
| Scope | FCFS prefill only; inclusive lower tier only (an exclusive tier would need DRAM-bandwidth modelling). | 10-07 | `EX/SETUP.md` |
| Rule evolution | The rule files evolve by: a size budget per role checked mechanically (set large for now); agents cite the rules they applied in their reports, each with a short review score from -5 to 5, and unused rules become retirement candidates; a bar for new rules; GENERAL.md as a versioned hub with a return path; periodic consolidation. Rejected: scenario regression tests of rules (option 3), because they are an A/B test; reopened only when the user names it. Why: rules grew without an outflow or a measure. | 2026-10-15 | User: "좋아. 1.2,4,5,6번을 하는데 예산은 일단 크게 줘. 인용이랑 같이 짧은 review도 (-5 to 5) 줘. 3 번은 A/B 테스트니까 하지 말도록 하고." (session 639434b8, 2026-10-15T06:24Z); options 1-6 in that session |
| Rule evolution: pending rules | The budget is fixed; a new rule waits in a pending list and is reviewed (the -5 to 5 rule-use reviews) before it enters the budgeted rules. Adds to "Rule evolution". Why: keep the budget fixed while new rules still get in on evidence. | 2026-10-15 | User: "좋아. 그래서 예산은 고정돼있지만, 대기 규칙을 만들어서 리뷰를 받도록 해줘." (session 639434b8, 2026-10-15); design `notes/design/T20261015-rules-evolve.md` |
| Rule evolution: parameters | Answers to Q1-Q10 of `notes/design/T20261015-rules-evolve.md` Part 6: Q1 fixed caps = current x1.2; Q2 retirement candidates by mean score only, threshold 1; Q3 retirement automatic, then reported; Q4 recommended (structured block + per-task/role JSON); Q5 open, to discuss; Q6 consolidation when rule changes accumulate past a count; Q7 score = task-local help/friction; Q8-Q10 recommended, but scores only, no time windows or deadlines. Adds to "Rule evolution" and "Rule evolution: pending rules". | 2026-10-15 | User: "1. 고정 예산 수치는 현재의 1.2배로. 2. 은퇴 후보 기준은 평균 점수로만. 1 이상. 3. 자동적으로 한 후 보고 4, 좋아. 5. 이건 논의를 좀 더 해보자. 6. 좋아. 규칙 변경이 일정 이상 쌓였을 때. 7. 맞아. 8, 9, 10 좋아. 시간 단위 말고 무조건 점수로." (session 639434b8, 2026-10-15) |
| Rule evolution: rollout | Q1 and Q2 as the master recommended (caps = A+B measured startup and card values x1.2; established rule becomes a retirement candidate when its mean score is below 1 over at least 5 rated tasks; unscored rules are not candidates); implement in two phases (phase 1 without Q5, phase 2 later); rule checks run periodically as rule changes accumulate. Refines "Rule evolution: parameters". | 2026-10-15 | User: "Q1,2 추천대로 1,2 차 나눠서. 규칙은 쌓일 때마다 주기적으로 검사하는 걸로." (session 639434b8, 2026-10-15), answering the master's Q1/Q2 interpretations and the phase question |
| Rule evolution: unused rules, protected | Q3 as the master recommended: protected categories (AGENTS 0.3, I.10/I.11 decision rights, USER contract, II.1 decisions) are never auto-retired; they are listed and reported as candidates. Unused rules are also removed periodically (automatic retirement with archive and report, protected categories excepted). Supersedes "unscored rules are not candidates" in "Rule evolution: rollout". | 2026-10-15 | User: "Q3도 추천대로. 쓰이지 않은 규칙도 주기적으로 없애는 걸로." (session 639434b8, 2026-10-15) |
| Verification, monitoring, spawn depth | (1) Every verification is done by Opus (supersedes Codex Sol verifiers for changes outside the byte-exact core, I.3/I.14). (2) The agent that launches a job or worker monitors it itself, exclusively. (3) The concentration of gates in the master is intended, but spawn depth becomes three with a separate middle manager tier (supersedes spawn depth two, I.15). Answers to findings F1/F2/F15 of `notes/agent-research/T20261015-agent-review.md`; rule text not yet changed. | 2026-10-15 | User: "1. verify는 뭐든지 opus가 하도록 바꿔줘. 2. 띄운 작업은 그 agent가 전담해서 모니터링하는걸로. ... 15. 이부분은 의도된 거지만, 우선 spawn을 3단계로 하는걸로 바꾸도록 하자. 그래서 중간 manager 단계를 따로 만드는 걸로." (session 639434b8, 2026-10-15; items 3/5/12 of the same turn are questions) |
| Review findings F3, F5, F12 | F3: separate formats per kind of work (an audit format for document analysis apart from the experiment claim-audit, a reasoning format, etc.); the user reviews the core cards first. F5: option (a), harden the guard hook and its tests to block `pkill <name>` and `git stash drop`/`clear` as the rules already forbid. F12: as proposed, the spawn-agent ledger/heartbeat steps apply to the master only; a non-master caller tracks helpers in its own trail and reports upward. Findings of `notes/agent-research/T20261015-agent-review.md`; rule text not yet changed. | 2026-10-15 | User: "F3. card를 좀 봐야겠어. 감사 양식, 생각 양식 등등을 다르게 둔다는 거에는 동의해. F5. 가로 해줘. 12. 제안대로 해줘." (session 639434b8, 2026-10-15) |
| Manager model; unused rules reopened | The manager tier runs on Opus. The automatic removal of unused rules (row "Rule evolution: unused rules, protected") is put back under discussion: not to be designed or implemented until the user settles it; K is not chosen. | 2026-10-15 | User: "쓰이지 않는 규칙은 좀 더 논의하자. manager는 opus를 쓰자." (session 639434b8, 2026-10-15) |
| Roles v2: formats, verifier, records | Formats (brief, read-back, report, verdict, audits, reasoning, etc.) are separated from the role cards, and the cards are restructured to route to them. A verifier is defined as any agent that verifies another agent's result, and it is always Opus; other simple work may go to other agents. The document and report formats and the knowledge/records system are organized too. Unused-rule handling is split off for a later, separate discussion. | 2026-10-15 | User: "1. 좋아. 양식 분리는 맞아. 역할 카드는 그렇게 정리해야 해. 2. 다른 에이전트의 결과를 verify하는건 모두 opus. verifier의 정의를 그렇게 적어줘. 나머지 간단한 작업은 다른 에이전트한테 맡겨도 돼. 3. 그리고 문서 보고서 양식 등 지식 체계도 정리해야 해. 쓰이지 않는 규칙 등은 나중에 따로 빼서 논의하자." (session 639434b8, 2026-10-15) |
| Review findings O2, O3, O8, O9 | O2: keep the current rule: rule-file changes on main stay local until their review passes, then push (notes that would carry them wait with them). O3: past records (decisions list, trails, handoffs, transcripts) are only referenced in an escalation, never used by an agent to answer the question itself; anything ambiguous is escalated at once, stated strongly (supersedes "a quote that plainly settles the question answers it" in I.11 Search before you escalate). O8, O9: left to the master's judgement. Findings of `notes/agent-research/T20261015-agent-review-opus.md`. | 2026-10-15 | User: "o2. local에 두고 review 후에 push로 그대로 가줘. o3. escalate는 과거 기록을 참조만 하도록. 애매한 부분은 바로 escalate하도록 강하게 명시해줘. o8, o9 이 부분은 알아서 정해줘." (session 639434b8, 2026-10-15) |
| Parallel workers | Many workers, research workers included, may be launched at once; the limits are those of I.15 (job slots, memory, one writer per file, spawn depth). The clause "don't run many at once" in `agents/CODEX.md` "Calling Codex" is to be removed in the roles v2 patch. | 2026-10-15 | User: "워커는 한꺼번에 많이 띄워도 돼. 관련 규칙은 어디있지?" (session 639434b8, 2026-10-15) |
| Master delegates to managers | The master hands general (not simple) work to a manager agent; simple work may still go directly to a worker. Applies once the manager tier of roles v2 is in the rule files. | 2026-10-15 | User: "그리고 master agent는 (간단한 작업이 아닌) 일반적인 작업은 manager agent한테 맡기는 걸로 해줘." (session 639434b8, 2026-10-15) |
| Rule edits on a branch; decisions list binds | (1) Rule-file edits are always made on a separate branch (worktree) and merged into main only after their review passes, so main carries only reviewed rules and the light path and note pushes go on as now (resolves O2 vs light path). (2) A row of the decisions list that plainly covers a question binds as a standing decision; the other records of the user's words (trails, handoffs, transcripts) are only referenced in an escalation; anything ambiguous is escalated at once (refines "Review findings O2, O3, O8, O9"). Both as the master recommended. | 2026-10-15 | User: "1,2 추천대로." (session 639434b8, 2026-10-15), answering the master's questions 1 (branch for rule edits) and 2 (decisions list binds) |
| Roles v2 Q1-Q5 | The recommended option of each open choice in `notes/design/T20261015-roles-v2.md` Part 8 (round 4, `35fe8c3d`), as the master presented them: Q1-A one manager per ledger line/unit; Q2-A Opus for acceptance/correctness checks of another agent's result (reader probes for comprehension and mechanical receipt/extraction may use other agents); Q3-A include the directly necessary role/format/record consistency fixes; Q4-A native nested custom manager spawned in the background, gated on the §5.3 preflight; Q5-A cap baseline measured after roles v2 is merged (refines "Rule evolution: rollout" A+B timing). | 2026-10-15 | User: "1, 2, 3, 4, 5 전부 추천안대로." (session 639434b8), answering the master's Q1-Q5 table |
| Roles v2 synthesis items | Add to the roles v2 design the merged synthesis items (`notes/agent-research/SYN-merged.md`) M05, M23, M26, M28, M29, M30 as proposed there, and M10 as: the output format the caller sets wins; the authority-based precedence (the higher agent wins) is decided later, together with the L6 (oversight) discussion. | 2026-10-15 | User: "M10: 호출자가 정한 출력 양식 우선. 이건 나중에 권한에 따라서 상위 에이전트가 우선하는대로. M26, M23, M28, , M29, M30, M05. 맞아." (session 639434b8), answering the master's list of role items; clarified: "아. M10에 대한 내용은 나중에 L6 관련 논의할 때 같이 정한단 얘기였어." (same session) |
| Roles v2 depth-3 Opus | Depth three may hold Opus (Claude) agents as well as Codex helpers: a depth-2 Claude agent may spawn an Opus subagent at depth three; nothing spawns below depth three. The harness depth setting stays three. Supersedes "Roles v2 depth-3 helpers" (Codex only at depth three). | 2026-10-15 | User: "깊이 3에는 Codex만 두기로 했으므로 / 이 부분을 다시 바꿔줘. opus를 둘 수 있도록." (session 639434b8), quoting the master's report |
| Codex concurrency | Run about 20 Codex workers at once for now; whether to go higher is decided after that run. | 2026-10-15 | User: "codex 는 우선 20개 정도로 해줘. 더 늘릴지는 실행한 후에 보자." (session 639434b8) |
| Verifier exception (this time) | For this time only, verification runs first on Codex; only items filtered as ambiguous or important are verified again by Opus. An exception to "Roles v2: formats, verifier, records" (Opus verifies other agents' results), not a change of it. | 2026-10-15 | User: "그리고 verifier는 이번만 예외로 둬서 codex로 1차적으로 실행하고, 애매하거나 중요한 걸로 필터된 것만 opus가 다시 검증하는 걸로 해줘." (session 639434b8) |
| Roles v2 approval | Approve the roles v2 design (`notes/design/T20261015-roles-v2.md`, round 9 `bf583b64`) for implementation: the §2 role cards, the §2.3.1 Manager duties, and the `.claude/settings.json` settings of §5.3 (depth three, about 20 concurrent Claude agents); implement it on a `rules/` branch, merged after review. | 2026-10-15 | User: "2. Manager duties 좋아." and "4. 구현해줘." then "좋아. 그렇게 해줘. 1.2.3 전부 승인할게." (session 639434b8), answering the master's questions 1 (§2 cards), 2 (depth-3 role, next row), 3 (settings) |
| Roles v2 depth-3 role | In this repository a depth-three Opus agent may take any working activity (e.g. one of many brainstorming generators), launched with the `implementer` custom type; it never coordinates other agents (manager) and never judges or accepts a result it is part of (acceptance verification and candidate ranking are assigned by its caller as independent siblings). Refines "Roles v2 depth-3 Opus". | 2026-10-15 | User: "가는 애매한 부분이 있는게, 브레인스토밍 등을 할 때처럼 역할이 고정되지 않고 계속 생길 수 있어. 어떻게 할까? 일단 이 레포에서는 가로 할까?" then "좋아. 그렇게 해줘. 1.2.3 전부 승인할게." (session 639434b8), approving the master's proposed wording |
| Models per machine | On this machine (DESKTOP-TAT32DD) Codex is available and used for Sol/Luna-tier work; in the other environment Claude Sonnet is the main worker model (Sol-tier work to Sonnet, as in the Codex-unusable fallback of I.3). Machine details: `knowledge/environment/machine.md`. | 2026-10-15 | User: "여기 환경에선 codex를 쓸 수 있는데, 다른 환경에서는 sonnet을 주로 쓸거라서." (session 639434b8) |

**Superseded** (do not reintroduce):
- "Roles v2 depth-3 helpers" (only Codex helpers at depth three; the implementer type loses the subagent-spawning tool; user 2026-10-15 "가로 해줘.") → Roles v2 depth-3 Opus above (2026-10-15).
- "4P + 4D with decode tp2" (4 prefill tp1 + 2 decode tp2; user 2026-10-15 "좋아. TP2로 일단 해보자.") → 2P + 3D(tp2) above (2026-10-15).
- Broad hard-tier triggers "design or judgement", "anything that may need to stop and ask" and "between two
  tiers, use the higher one" (2026-10-14) → Worker model routing above; I.3 explicit criteria.
- "Every arm runs the stock Dynamo KV router" and "P and D both `consistent_hash`" (10-13) → configurations A/B
  and token least-load decode above.
- "Main configuration = one shared pool", "private tier only", "all shared, no private tier" (10-13) → A and B both.
- RTXPRO6000 / Llama-3.1-8B as the experiment setup, TraceLab regimes R1-R3/S → H100 / Qwen3-30B-A3B FI. The
  constants in II.2 are still the RTXPRO6000 fit.
- `RATE_POLICY=rate` alone as "ours", and the successor-prefilled -> 0 row → `rate_sum` + `RATE_SESS_STATE=1`.
- Claim 2 "each CP group shares one FCFS queue" with an open "instantaneous vs windowed W" → own queue, windowed.
- Claim 2 cost from the instance's **own** queue (windowed) (10-13/14) → windowed average over all instances of the reader's CP degree (2026-10-15, II.1 Claim 2).
- Seeds 1-3 with file-order arrivals; decode least-load by request count; the old `fi-pd` sweep (killed 10-14).
- "Research on Sonnet" → Codex. "Only the main session monitors" → I.5.
- Haiku (simple) and Sonnet (general) tiers, and the Claude `helper` subagent type (10-14) → Codex Luna / Sol
  medium task workers; hard work Opus medium (I.3). They stay superseded as defaults, but Sonnet and Haiku
  subagents are the fallback when Codex is unusable (2026-10-14, I.3).

## II.2 Paper claims

All three are about **FCFS prefill** with an inclusive CPU/CXL lower tier behind P/D-disaggregated prefill
instances. Theme 1 is load- and routing-independent; every load- or routing-dependent effect belongs to theme 2.

1. **Partial eviction with the `rate` cost model** — decided as is (`EX/PAPER-ALGORITHM.md` section 2). The lower
   tier evicts block-granularly and leaves holes; a later request reuses the blocks around a hole and recomputes
   only the hole. Victim = lowest `score(x) = p_s / max(tau_s, 1 s) * c(pos_x)`: `p_s` = probability the owning
   session returns and reads x, `tau_s` = expected time until that reader is admitted, `c(pos)` = recompute
   seconds at that position from `S = A + b1 (L - H) + b2 (L^2 - H^2) / 2` (A = 0.0175 s, b1 = 3.87e-5 s/token,
   b2 = 1.85e-9 s/token^2; RTXPRO6000, Llama-3.1-8B fit). Owner states: prefilling or successor queued -> 1e6
   (finite protection); decoding -> `q / max(MRL_dec(e) + mean tool gap, 1)`; idle t s after decode ->
   `p / max(MRL_tool(t), 1)` with `p = qS(t) / (qS(t) + p_end)`. Params (`RATE_PARAMS`) come from the same
   config's LRU run.
2. **CP-degree-aware eviction** — open, being designed (`EX/PAPER-ALGORITHM.md` section 3). Prefill instances
   form groups by CP degree d; a request goes to a group by its miss tokens (thresholds T_1 < T_2 < ...). A miss's
   cost includes the queueing delay it causes: same group `dT = M_k * c(pos) / (d_k * eta_k)`, M_k from the own
   instance's windowed queue (II.1). Open: the M form, the thresholds T, the destination queue for the
   group-crossing term, whether the token budget scales with d.
3. **Hole-balanced CP kernel** — decided in principle (`EX/PAPER-ALGORITHM.md` section 4). A prefill with holes
   is a set of compute ranges; standard zigzag CP assumes one contiguous sequence, so holes unbalance the ranks.
   The balanced partitioner lays computed tokens out in position order, takes the cumulative cost of
   `c(i) = a + b*i`, and cuts it into d equal pieces. Metric: max rank cost / mean; eta_k feeds claim 2. Open:
   per-step vs per-request balance, zigzag over concatenated vs absolute positions, SPP-style dynamic chunking.

Ruled out by exploration (keep out of proposals unless the user reopens them): "SRPT evicts long more" (an
artifact of a cache-blind SRPT key); TTFT following C_s (it follows rho); an exclusive tier; LOAD routing for
prefill under private tiers (chaotic). Under hit-aware SRPT `rate` loses to LRU, hence the FCFS scope. (2026-10-14)

Evidence tables (claim 1 ablations, M2, queueing models, CP profile limits): `AN/CLAIM-EVIDENCE.md`.

## II.3 Code and branches

| branch | what it is |
|---|---|
| `main` | Stock LLMServingSim (`agents/SIM-REFERENCE.md`). Upstream docs and validation. |
| `perf/fast-et-encoder` (`ea5b243`) | The fast simulator base research branches are cut from. |
| `feat/pe-srpt` | Reviewed research code: cost-aware pool, `--return-dist`, `--queue-cost`, hit-aware SRPT, `--pd-reserve`. |
| `explore/rate-wl-phase3` | The current notes, drivers and results (`R`), worktree `.wt/p3/pe`, pushed. |
| `feat/chash-router` | vllm-router `consistent_hash` (`--request-routing-policy CHASH`, `--chash-decode-policy hash|load`). |
| `feat/fi-dec-tok` | `--chash-decode-policy load_tokens`. |
| `run/fi-shB` | Option B stack: staging L2, PCIe/net bandwidths, remote latency, `--kv-decode-policy`. |
| `run/fi-ab` | chash-router + fi-dec-tok + fi-shB combined: the tree both FI grids run from (`.wt/p2v/ab`). |
| `feat/rate-sess-state` | `RATE_SESS_STATE=1`. |
| `feat/wl-codec` | Compact workload codec, router decoder, generator options, bench closed-loop driver (pushed). |
| `feat/cp-impl`, `feat/cp-fidelity`, `feat/cp-pipeline`, `feat/cp-astra` | CP groups, shared CP pool, CP eviction value; CP communication/KV layout/partitioners; pipeline CP; CP traffic in ASTRA-Sim (on origin, 10-09). Map: `R/cp-code/CP-CODE.md`. |

- The vLLM fork `/home/asd/vllm-dev` has the kernel side on `holes/{core,cp,kernel,mla,rate,server}`.
- Code map of claim 1 (hole-aware lookup in `kv_cache_manager.py`, hole scheduling, per-segment attention,
  `CostAwarePool`/`SessRatePool`/`ProbePool`, `rate` scoring): `AN/CODE-MAP.md`. The lower tier evicts 256-token
  chunks; the NPU block is 16 tokens.
- Research branches pin astra-sim at `99a368d`; `main` pins `d346994`.

## II.4 Research environment (2026-10-15)

Approval: user, 2026-10-15: "좋아. 그렇게 바꿔줘."

Facts (machine, container, `.wt/` layout, builds, reference values) are knowledge entries; read the ones named here
before the step they cover. (2026-10-14) Rules:

- Only the simulator runs on this machine, never the profiler or bench (no GPU: `knowledge/environment/machine.md`). (2026-10-14)
- The simulator container sees only the repository directory, and stops on every host or Claude Code restart:
  `knowledge/environment/sim-container.md`. Layout of `.wt/`: `knowledge/environment/wt-layout.md`. (2026-10-14)
- Research trees use the research ASTRA-Sim build, not `astra-sim/build`: `knowledge/environment/research-astra-build.md`. (2026-10-14) Research trees link `.wt/astra-build/build`; read `knowledge/pitfalls/research-wrong-astra-build.md` before linking a build. (2026-10-14) (2026-10-15)
- **Code vs runs:** write code in a worktree `.wt/p3/<id>` on your own branch; never build or run inside a
  worktree, and never nest worktrees. Run from a measurement tree `.wt/p2v/<id>`, built as
  `knowledge/environment/measurement-tree.md`; one tree per variant; delete it when done. (2026-10-14)
- Stock simulator on main: build and validate as `knowledge/environment/stock-build-main.md`. (2026-10-14)
- Reference checks are exact; their expected values and what to check when a clock differs:
  `knowledge/experiments/reference-clocks.md`. (2026-10-14)

## II.5 Experiment run line

- **Current grids (10-14):** FI, seed 1, rates as in II.1, five arms, configurations A and B, from tree
  `.wt/p2v/ab`. Drivers `R/fi/drv_pd2.py` (A) and `R/fi/drv_shB.py` (B); dataset builder `R/fi/mkds2.py`
  (`fi/ds/fi_swe128K_pois_perm_r<rate>_s<seed>.jsonl`). Run ids `xFI_A_r<rate>_<arm>`, `xFI_B_r<rate>_<arm>`.
  Results `R/results/fi-A/`, `R/results/fi-B/`. Setup and state: `R/HANDOFF.md` 10.13.
- Per rate, the LRU run goes first: ours (params), Belady (T_res, oracle) and AsymCache derive inputs from the same
  configuration's LRU run. (2026-10-14)
- Older lines: `R/results/fi-pd/` (killed sweep, file-order arrivals, request-count decode load).
- Analyses: `R/fi/LOADTIME.md` (phases, no steady state, stop rules), `R/fi/DECODE-NEED.md` (decode sizing),
  `R/prof/PROFILE.md` (profiling).

## II.6 Workloads (2026-10-15)

Approval: user, 2026-10-15: "좋아. 그렇게 바꿔줘."

Rules (user, 2026-10-12/13):
- **Use the whole source.** Never `--num-sessions`, never cut a session with `--max-context`, never drop single
  requests. A source whose requests exceed the served model's window is left out, except FreeInference, where a
  session with any over-length request is dropped **whole** (the simulated model cannot serve it). (2026-10-12/13)
- **Selection:** every request fits 128Ki (input + output); the source records timing (timestamps or tool/idle
  gaps; generator-made gaps do not count); long inputs preferred (Mooncake about 10K is the floor, 30-40K the
  target). (2026-10-12/13)
- **One file serves the simulator and real vLLM** (`bench`): real in-vocabulary prompt token ids, equal blocks map
  to equal token sequences, output pinned with `max_tokens = output_toks` and `ignore_eos`. (2026-10-12/13)
- **Compact files** (`blk_codec: b16k100000`, `input_blk`): the run tree's router must have `feat/wl-codec`'s
  `serving/core/wl_codec.py` (on `feat/wl-codec`) and decoder, or prefix caching silently sees no reuse. (2026-10-12/13)
- Read `agents/RESEARCH.md` II.1 before selecting arrival process, session order or gaps. (2026-10-12/13)
- After regenerating a file, delete `R/meta/<wl>.json` and `<wl>_H.json`, or the harness keeps the old session list. (2026-10-12/13)
- Never commit workload data (`workloads/tracelab/`, `workloads/raw/`, the jsonl files). (2026-10-12/13)

Current set: **FreeInference swe-bench** (`workloads/freeinference-swebench-128K.jsonl`, 1,033 sessions, 60,773
requests, input mean 26.5K) is the FI grid's workload; lmcache-agentic, mooncake-conversation-12031 and
mooncake-toolagent-23608 pass the selection rules. Statistics, exclusions, generator commands and the codec:
`AN/WORKLOADS-DETAIL.md`.

## II.7 Env-gated hacks (2026-10-14)

Retired: TraceLab-era env-gated hacks (user, 2026-10-14); facts kept in `knowledge/experiments/env-gated-hacks.md`.

- The variables the current run line still sets (`KV_DIV`, the `RATE_*` of the arms in II.1) are described in the
  same entry; read it before setting one (2026-10-14).

## II.8 Research pitfalls (2026-10-15)

Approval: user, 2026-10-15: "좋아. 그렇게 바꿔줘."

Each item is a rule; the facts behind it are in the pitfall entry named.

- Export `KV_DIV=1` for reference checks: it defaults to 10 on research branches and `validate-par` does not set
  it (the harnesses do) (`knowledge/pitfalls/research-kv-div-default.md`). (2026-10-14)
- Read `agents/RESEARCH.md` II.4 before linking a research ASTRA-Sim build. (2026-10-14)
- Use only the documented `RATE_POLICY` values (`knowledge/pitfalls/research-rate-policy-silent.md`). (2026-10-14)
- Don't treat the `rate` protection as absolute: it is finite (`knowledge/pitfalls/research-rate-protection-finite.md`). (2026-10-14)
- Don't use `bwrap_sess.py` under `LT_CHUNK_TOKENS=128`; the lower tier evicts 256-token chunks and the NPU block is
  16 tokens (`knowledge/pitfalls/research-chunk-sizes.md`). (2026-10-14)
- Size decode so it never overflows: an overflow kills the run (`knowledge/pitfalls/research-decode-overflow.md`). (2026-10-14)
- Don't trust sub-batch interleaving timings for requests with holes (`knowledge/pitfalls/research-sub-batch-holes.md`). (2026-10-14)
- Report per-arm request counts with any time-window metric in closed loop
  (`knowledge/pitfalls/research-closed-loop-windows.md`). (2026-10-14)

## II.9 Notes to read, in order

1. `R/NEXT-AGENT.md` (the manual) and `R/HANDOFF.md` section 10 (newest first).
2. `R/results/<grid>/README.md` for the grid you work on.
3. `EX/PAPER-ALGORITHM.md` (the algorithm and the user's decisions), `EX/SETUP.md`.
4. `research/docs/AGENT-MANUAL.md`, `research/QUICKSTART.md`.
5. `AN/` for the detail moved out of this file (`AGENT-RULES-OLD.md` keeps the pre-2026-10-14 rule text).

