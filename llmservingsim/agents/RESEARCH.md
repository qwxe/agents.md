# agents/RESEARCH.md — research context: lower-tier partial eviction

Scope: agents on research branches. Section ids (II.x) are kept from the old single-file AGENTS.md, so references to "II.1" still work. Read II.1 always; other sections when the brief names them.


Applies to agents on research branches. Research code is **not on `main`**: it lives on `explore/pe-tracelab`
(TraceLab era) and `explore/rate-wl-phase3` plus feature branches (II.3).

## II.1 Decisions in force

Every standing user decision, newest wins. Source = where the reasoning (why) is recorded; a new row also
states its why in one clause. Superseded and ruled-out entries are reopened only when the user names them (I.10).

| area | decision | date | source |
|---|---|---|---|
| Paper themes | Three themes, all on the hole structure: (1) the `rate` cost, (2) CP-degree-aware eviction cost, (3) CP partition. The router is not a theme. | 10-13 | `EX/PAPER-ALGORITHM.md` |
| Framework principle | The paper's system is a real framework configuration **as shipped** plus our eviction policy only. Features no framework has are out of scope. "Minimal" is conceptual: the implementation may be large (e.g. patching Mooncake master's eviction order). | 10-14 | HANDOFF 10.13 |
| Hole lookup | The lookup that reuses blocks past a miss is part of our eviction and is **always** implemented (one lookup-function change), although SGLang/LMCache stop at the first miss. | 10-14 | — |
| Claim 1 | `rate` uses session behaviour only (tool gaps, decode, p_end), never router rules, move fractions or load; load/routing effects belong to claim 2. Every chunk is priced by its session's latest request (`RATE_SESS_STATE=1`). | 10-13 | `R/rsess/NOTES.md` |
| Claim 2 | Cost = expectation at eviction time from the instance's **own** queue with **windowed** W/lambda/rho (eviction != execution); the reader's group is fixed at eviction (an eviction that crosses a threshold re-homes the session). No part split, no burstiness test. | 10-13/14 | `R/qacf` |
| Hardware | H100 (`RWL_HW=H100`, H100NVL-long profiles). Decode instances `mem_size` 141 GB (H200-class) so decode capacity does not bind. | 10-12/13 | `R/fi/NOTES.md` |
| Model, layout | FI runs: Qwen/Qwen3-30B-A3B-Instruct-2507, tp1, **2P6D** (8 GPUs; 2P is the floor under "prefill takes as much load as possible, decode never saturates"). | 10-13 | `R/models/NOTES.md`, `R/fi/DECODE-NEED.md` |
| Configurations | Run **both**. **A:** prefill `consistent_hash` (vllm-router, session sticky) + private CPU tier 128 GiB per prefill instance. **B:** SGLang HiCache + Mooncake shared L3 (one pool, 2 x 128 GiB) + per-instance staging L2 = 2 x device KV pool (SGLang `--hicache-ratio 2`, LRU, L3 ⊇ L2) + Dynamo v1.5.1 KV router `--shared-cache-type hicache` (0.5). Our eviction acts on A's private tiers and on B's shared L3. | 10-14 | HANDOFF 10.13 |
| Decode routing | Least-load by **tokens** (`load_tokens`: booked unique prompt blocks, Dynamo-style), in A and B. No decode admission queue: an overflow still fails the run. | 10-14 | `R/results/fi-pd2/README.md` |
| Bandwidth | PCIe 50 GB/s per GPU; network 100 Gbps = 12.5 GB/s. B's remote-node reads: min(PCIe, net) + 10 us per remote chunk; same-node reads at PCIe. | 10-14 | — |
| Arms | LRU, Belady (TTL 0), ideal (infinite tier), AsymCache (plain CostAwarePool), **ours = `rate_sum`** (`RATE_POLICY=rate RATE_HOLE=after RATE_SEG=sum`, `RATE_SESS_STATE=1`). `rate_tail` is an ablation. Quick checks: LRU vs ours only. | 10-13 | `R/results/fi-pd/README.md` |
| Router overlap | `--router-overlap-past-holes` reports reusable tokens past holes to an unchanged router, identically for every arm; not claimed. | 10-13 | — |
| Arrivals, seeds | Sessions start by Poisson at a controlled rate and keep their recorded tool gaps; the session **order is random** (permuted). **One seed** (1); no seed mean +- sd. | 10-13/14 | `R/fi/mkds2.py` |
| Run length | Every run goes **to completion** (FI has no steady state). Headline = full-run TTFT; also report (A) TTFT of arrivals in [1800 s, t1] with per-arm counts and (D) all requests of sessions started in [1800 s, 0.75 t1]. | 10-14 | `R/fi/LOADTIME.md` |
| Load knob | Session arrival rate only. FI grid rates 0.1 / 0.15 / 0.2 (all arms) plus 0.05 and 0.25 (LRU, ours). | 10-13/14 | HANDOFF 10.12-10.13 |
| Workloads | II.6. | 10-12/13 | — |
| Scope | FCFS prefill only; inclusive lower tier only (an exclusive tier would need DRAM-bandwidth modelling). | 10-07 | `EX/SETUP.md` |

**Superseded** (do not reintroduce):
- "Every arm runs the stock Dynamo KV router" and "P and D both `consistent_hash`" (10-13) → configurations A/B
  and token least-load decode above.
- "Main configuration = one shared pool", "private tier only", "all shared, no private tier" (10-13) → A and B both.
- RTXPRO6000 / Llama-3.1-8B as the experiment setup, TraceLab regimes R1-R3/S → H100 / Qwen3-30B-A3B FI. The
  constants in II.2 are still the RTXPRO6000 fit.
- `RATE_POLICY=rate` alone as "ours", and the successor-prefilled -> 0 row → `rate_sum` + `RATE_SESS_STATE=1`.
- Claim 2 "each CP group shares one FCFS queue" with an open "instantaneous vs windowed W" → own queue, windowed.
- Seeds 1-3 with file-order arrivals; decode least-load by request count; the old `fi-pd` sweep (killed 10-14).
- "Research on Sonnet" → Codex. "Only the main session monitors" → I.5.

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
prefill under private tiers (chaotic). Under hit-aware SRPT `rate` loses to LRU, hence the FCFS scope.

Evidence tables (claim 1 ablations, M2, queueing models, CP profile limits): `AN/CLAIM-EVIDENCE.md`.

## II.3 Code and branches

| branch | what it is |
|---|---|
| `main` | Stock LLMServingSim (`agents/SIM-REFERENCE.md`). Upstream docs and validation. |
| `perf/fast-et-encoder` (`ea5b243`) | The fast simulator base research branches are cut from. |
| `feat/pe-srpt` | Reviewed research code: cost-aware pool, `--return-dist`, `--queue-cost`, hit-aware SRPT, `--pd-reserve`. |
| `explore/pe-tracelab` | fast-et + pe-srpt + every env-gated hack (II.7) + the TraceLab harness and notes (`EX`). |
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

## II.4 Research environment

- **Machine:** WSL2, 28 vCPUs (about 8 fast cores), about 11-12 GB RAM, no GPU: only the simulator runs here,
  never the profiler or bench.
- **Container:** `servingsim_docker` (`scripts/docker-sim.sh`) mounts only `/home/asd/LLMServingSim` at
  `/app/LLMServingSim`, so a worktree elsewhere is invisible to it. It exits on every host or Claude Code restart:
  `docker start servingsim_docker`.
- **`.wt/` layout** (restored 2026-10-12 from `archive-20261012/env-sim.tar.gz`): `.wt/bin` (slotrun, hangdump,
  validate-par), `.wt/perf-tools/slots`, `.wt/pypy/venv` (PyPy 3.10 v7.3.19; its `python` refuses runs outside a
  slot), `.wt/astra-build/build` (the research ASTRA-Sim build, perf pin `99a368d`), `.wt/p3/<id>` (code
  worktrees), `.wt/p2v/<id>` (measurement trees). `.wt/` is in `.git/info/exclude`.
- **The research build is `.wt/astra-build/build`, not `astra-sim/build`** (that is main's `d346994` build).
- **Code vs runs:** write code in a worktree `.wt/p3/<id>` on your own branch; never build or run inside a
  worktree, and never nest worktrees. Run from a measurement tree `.wt/p2v/<id>`: copy `serving/` (and `bench/`),
  symlink `configs`, `profiler`, `outputs`, `workloads`, `astra-sim/build -> ../../../astra-build/build`, and
  `astra-sim/inputs` from `git archive 99a368d inputs`. Pass it as `SIM_TREE=.wt/p2v/<id>` (relative). One tree
  per variant; delete it when done.
- **Stock simulator on main:** `git submodule update --init --recursive`, then
  `docker exec -w /app/LLMServingSim servingsim_docker bash scripts/compile.sh`, then `./serving/validate.sh`.
- **Reference checks** (exact): `SIM_TREE=<tree> KV_DIV=1 .wt/bin/validate-par` = 59/59 + 8/8. Stock TraceLab
  (codex n160 seed 1, 4P4D, CPU 112, LOAD, FCFS, LRU; pass env `{"KV_DIV": "1"}`): **2474048837763** (csv
  `99bc8243`) on any tree with fix/attention-per-segment (pe-tracelab, phase3 trees); 2520592369985 only on bare
  `perf/fast-et-encoder`. If a clock differs, check the dataset, the tree, the PyPy version, then the build.
- Data setup, TraceLab-era harness API and regimes: `AN/ENV-DETAIL.md`.

## II.5 Experiment run line

- **Current grids (10-14):** FI, seed 1, rates as in II.1, five arms, configurations A and B, from tree
  `.wt/p2v/ab`. Drivers `R/fi/drv_pd2.py` (A) and `R/fi/drv_shB.py` (B); dataset builder `R/fi/mkds2.py`
  (`fi/ds/fi_swe128K_pois_perm_r<rate>_s<seed>.jsonl`). Run ids `xFI_A_r<rate>_<arm>`, `xFI_B_r<rate>_<arm>`.
  Results `R/results/fi-A/`, `R/results/fi-B/`. Setup and state: `R/HANDOFF.md` 10.13.
- Per rate, the LRU run goes first: ours (params), Belady (T_res, oracle) and AsymCache derive inputs from the same
  configuration's LRU run.
- Older lines: `R/results/fi-pd/` (killed sweep, file-order arrivals, request-count decode load); the TraceLab
  harness `tracelab/r2/tl2_run.py::run` and `EX/infra/harness.py` (`AN/ENV-DETAIL.md`).
- Analyses: `R/fi/LOADTIME.md` (phases, no steady state, stop rules), `R/fi/DECODE-NEED.md` (decode sizing),
  `R/prof/PROFILE.md` (profiling).

## II.6 Workloads

Rules (user, 2026-10-12/13):
- **Use the whole source.** Never `--num-sessions`, never cut a session with `--max-context`, never drop single
  requests. A source whose requests exceed the served model's window is left out, except FreeInference, where a
  session with any over-length request is dropped **whole** (the simulated model cannot serve it).
- **Selection:** every request fits 128Ki (input + output); the source records timing (timestamps or tool/idle
  gaps; generator-made gaps do not count); long inputs preferred (Mooncake about 10K is the floor, 30-40K the
  target).
- **One file serves the simulator and real vLLM** (`bench`): real in-vocabulary prompt token ids, equal blocks map
  to equal token sequences, output pinned with `max_tokens = output_toks` and `ignore_eos`.
- **Compact files** (`blk_codec: b16k100000`, `input_blk`): the run tree's router must have `feat/wl-codec`'s
  `serving/core/wl_codec.py` (on `feat/wl-codec`) and decoder, or prefix caching silently sees no reuse.
- **Arrivals:** Poisson session starts at a controlled rate, random session order, recorded within-session gaps.
- After regenerating a file, delete `R/meta/<wl>.json` and `<wl>_H.json`, or the harness keeps the old session list.
- Never commit workload data (`workloads/tracelab/`, `workloads/raw/`, the jsonl files).

Current set: **FreeInference swe-bench** (`workloads/freeinference-swebench-128K.jsonl`, 1,033 sessions, 60,773
requests, input mean 26.5K) is the FI grid's workload; lmcache-agentic, mooncake-conversation-12031 and
mooncake-toolagent-23608 pass the selection rules. Statistics, exclusions, generator commands and the codec:
`AN/WORKLOADS-DETAIL.md`.

## II.7 Env-gated hacks

On `explore/pe-tracelab` and the trees derived from it:

| var | effect |
|---|---|
| `KV_DIV` | Divides every KV size. **Defaults to 10 when unset**, not 1. |
| `RATE_POLICY`, `RATE_PARAMS`, `RATE_HOLE`, `RATE_SEG`, `RATE_SESS_STATE`, `RATE_STATS`, `RATE_NEWTOK` | `SessRatePool` modes (`rate`, `rate_q`, `rate_req`, `uni`, ...); ours = `rate` + `RATE_HOLE=after RATE_SEG=sum` + `RATE_SESS_STATE=1`. |
| `UNI_COST`, `UNI_M`, `UNI_KRES`, `UNI_KEYC`, `UNI_SESS`, `UNI_SJ`, `UNI_MPRES` | `uni` ablations; `UNI_SJ=1` is M2. |
| `AFFINITY=hash\|sticky\|file\|balw`, `AFFINITY_FILE`, `ST_BAL_WIN`, `ST_TSCALE` | Session-affinity prefill routing (TraceLab era). |
| `XS_SEED`, `XS_JIT_S`, `XS_KEY=static\|hit\|hit0` | Start-time jitter; SRPT key (`hit` = hit-aware). |
| `PP_MODE`, `PP_HOLES`, `PP_PIN`, `PP_EXCL`, `PP_STATS`, `PP_PIN_FRAC/SIDE`, `PP_EVERY` | `ProbePool` arms, pinning, statistics. `PP_EXCL` (exclusive tier) is out of scope. |
| `PERTURB_FILE`, `WORK_PERTURB_FILE`, `DC_ATTN` | Probes that perturb hits, work or attention pricing. |

## II.8 Research pitfalls

- **`KV_DIV` defaults to 10** on research branches; `validate-par` and `EX/lz/stock.py` do not set it, so export
  `KV_DIV=1` for reference checks (the harnesses set it themselves).
- **The wrong ASTRA-Sim build:** research trees must link `.wt/astra-build/build`, not `astra-sim/build`.
- **Reference clock depends on the tree** (II.4): a mismatch against 2520592369985 is expected on fixed trees.
- **`RATE_POLICY=rate_unif` and `rate_p` silently run as plain `rate`;** `XS_QPROT`, `XS_QW`, `XS_HD` do not exist.
  "dist + queued protection" is `PP_MODE=dist` with `PP_PIN=1`.
- **The `rate` protection is finite** (1e6): protected chunks can still go after every other chunk.
- **Chunk sizes:** the lower tier evicts 256-token chunks (`memory_model.py`); the NPU block is 16 tokens.
  `bwrap_sess.py` hard-codes 256, so it is wrong under `LT_CHUNK_TOKENS=128` (`R/fish/bwrap_fi.py` is not).
- **Decode overflow kills the run** ("decode instance cannot admit request"): there is no admission queue.
- **`_make_sub_batch` drops hole segments,** so sub-batch interleaving with holes is timed wrong.
- **Closed loop:** a slower arm stretches the clock, so time windows favour it; report per-arm request counts.
- **Unreproducible references:** `fsrun` warm-up and conv10 need `outputs/mc/*` files no branch has.

## II.9 Notes to read, in order

1. `R/NEXT-AGENT.md` (the manual) and `R/HANDOFF.md` section 10 (newest first).
2. `R/results/<grid>/README.md` for the grid you work on.
3. `EX/PAPER-ALGORITHM.md` (the algorithm and the user's decisions), `EX/SETUP.md`, `EX/FINDINGS.md`.
4. `research/docs/AGENT-MANUAL.md`, `research/QUICKSTART.md`.
5. `AN/` for the detail moved out of this file (`AGENT-RULES-OLD.md` keeps the pre-2026-10-14 rule text).

