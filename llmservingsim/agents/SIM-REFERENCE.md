# agents/SIM-REFERENCE.md — stock simulator reference

Scope: everyone working on `serving/`, `profiler/` or `bench/` (Claude agents whose brief touches them, Cursor, Copilot and other tools). Formerly AGENTS.md Part III (moved 2026-10-14). Since 2026-10-14 this file keeps the rules; the facts (architecture, formats, data flow, configs) are knowledge entries in `knowledge/simulator/` (catalog `knowledge/KNOWLEDGE.md`).

This file documents `main`; research branches add to it (`agents/RESEARCH.md`) but do not change these rules. (2026-10-14)

## Simulator knowledge (2026-10-14)

Read before changing the simulator: the entries of category `simulator` whose `read_when` matches your change
(`python3 agents/gen_knowledge.py --category simulator` prints the table). Start with
`knowledge/simulator/overview.md` (what LLMServingSim is, repository layout) and `knowledge/simulator/simulation-flow.md`. (2026-10-14)
The container images are `knowledge/environment/docker-images.md`.

## Code Style & Formatting (2026-10-15)

Approval: user, 2026-10-15: "좋아. 그렇게 바꿔줘."

- **Python**: 4-space indentation, snake_case for functions/variables, PascalCase for classes (2026-04-26)
- **No enforced formatter** — match surrounding code style in the file you're editing (2026-04-26)
- **CLI flags**: use hyphens (`--cluster-config`, `--max-num-seqs`) (2026-04-26)
- **Internal Python**: use underscores (`max_num_seqs`, `enable_chunked_prefill`) (2026-04-26)
- **JSON config filenames**: descriptive snake_case (`single_node_pim_instance.json`) (2026-04-26)
- **Imports**: keep minimal and consistent; `serving/` modules use relative imports (2026-04-26)
- Read `AGENTS.md` 0.3 rule 11 before writing comments, docstrings or logs. (2026-04-26)

## Rules from the reference sections (2026-10-15)

Approval: user, 2026-10-15: "좋아. 그렇게 바꿔줘."

Rules that were embedded in the architecture description; the facts behind each are in the entry named.

- **R1.** `_axis_bracket` blends on a linear scale. Don't "restore" log space because the sweep is geometric
  (see `knowledge/simulator/perf-db-lookup.md`). (2026-08-20)
- **R2.** Keep the anti-thrash rule: phase B of `schedule()` never preempts and is skipped entirely on any step
  that preempted; it is load-bearing (see `knowledge/simulator/scheduler.md`). (2026-08-19)
- **R3.** There is one `schedule()` for prefix caching on and off; do not reintroduce a second scheduler (see
  `knowledge/simulator/scheduler.md`). (2026-08-19)
- **R4.** For a run that saturates the KV cache, calibrate `mem_util` so the block count matches
  `kv_cache.num_gpu_blocks` in the bench run's `meta.json` before comparing latency at all; do not treat
  `mem_util` as a general explanation for validation error (see `knowledge/simulator/memory-model.md`). (2026-08-21)
- **R5.** If a runtime workload needs mixed-regime data at `n = X`, profile with `MAX_NUM_SEQS ≥ X + 1` (see
  `knowledge/simulator/feasibility-bounds.md`). (2026-04-26)
- **R6.** Pass ASTRA-Sim the **total** data size of a collective, not per-NPU: the full output tensor for the
  ALLREDUCE on `o_proj` and `down_proj`, the full activation tensor for the MoE ALLTOALL (see
  `knowledge/simulator/collective-sizes.md`). (2026-04-26)
- **R7.** EP collectives never mark the PP dimension in `involved_dim` (see `knowledge/simulator/involved-dim.md`). (2026-08-21)
- **R8.** The memory location type values (`LOCAL` = 1, `REMOTE` = 2, `CXL` = 3, `STORAGE` = 4) must match the
  C++ enum in `astra-sim/astra-sim/system/AstraMemoryAPI.hh` (see `knowledge/simulator/chakra-converter.md`). (2026-04-26)
- **R9.** Head dimension: some models (e.g., Qwen3) have `head_dim != hidden_size // num_attention_heads`.
  Always use (2026-04-26):
  ```python
  head_dim = config.get('head_dim', n_embd // n_head)
  q_dim = n_head * head_dim        # NOT n_embd
  kv_dim = kv_head * head_dim      # NOT n_embd // group
  ```
  Read `knowledge/pitfalls/sim-hidden-size-head-dim.md` before changing these dimensions. (2026-04-26) (2026-10-15)
- **R10.** Every trace field except the last carries an explicit trailing space in `_FMT`, and `header()` goes
  through `_FMT` too, so the file has one layout (see `knowledge/simulator/trace-format.md`). (2026-08-23)
- **R11.** Dynamically released sub-requests enter the waiting queue with `bisect.insort`, not `append` (see
  `knowledge/simulator/agentic-sessions.md`). (2026-04-26)
- **R12.** Advance `num_computed_tokens` at schedule time, as vLLM's `_update_after_schedule` does, not at
  completion (see `knowledge/simulator/scheduler.md`). (2026-08-19)
- **R13.** Gate the DP dummy batch on `len(inflight) < pp_size`, not `== 0`, and land a DP batch's dispatch before
  the next `schedule()` for that NPU (`dp_ready_workloads` served ahead of `schedule()`) (see
  `knowledge/simulator/dp-wave-sync.md`). (2026-08-24)
- **R14.** The simulator runs with cwd `astra-sim/`: paths to `configs/`, `workloads/`, `profiler/` are relative
  to the repo root and prefixed with `../` in code (see `knowledge/simulator/working-directory.md`). (2026-04-26)

## README and docs split (2026-10-14)

The repo has two documentation surfaces with deliberate scope:

- **`README.md`** — minimal front door. About / Getting Started / Publications /
  Citation only. Logo + link bar (Website / Documentation / Contribute /
  Contact / Changelog) point everything else out to the website. **Do not
  re-add detailed content (CLI flag tables, dataset schema, profiler
  walkthroughs, validation plots, etc.) to the README** — it lives on the
  website now. (2026-05-04)
- **`docs/`** — the public docs site (Docusaurus 3, deployed at
  `https://llmservingsim.ai`). All long-form content lives here. See
  `docs/AGENTS.md` for site-specific conventions. (2026-05-04)

When you add a new feature with user-visible behavior, document it on the
website (not the README). (2026-05-04)

## Commit & Pull Request Guidelines (2026-10-15)

Approval: user, 2026-10-15: "좋아. 그렇게 바꿔줘."

- Short imperative commit messages: `Fix incorrect evict_size accumulation`,
  `Add Qwen3 model support` (2026-04-26)
- Read `agents/OPERATIONS.md` I.16 before staging or committing. (2026-04-26)
- Include the exact command used for validation and note any output CSV path in PRs (2026-04-26)
- Describe which simulation mode is affected and the config/dataset used (2026-04-26)

## Testing & Validation (2026-10-14)

No unit-test suite on `main` (the default test suite lives on `feat/tests`, `agents/OPERATIONS.md` I.5). The simulator is deterministic, so validation is exact
equality against recorded results:

1. **`./serving/validate.sh`** — the whole check, ~8 min. Stage 1 compares every
   scenario against the `Total clocks (ns)` recorded in
   `serving/validate-baselines.txt`; stage 2 regenerates each `bench/examples`
   entry's `outputs/sim.csv` and `validation/summary.txt` and checks both md5s.
   Anything that moved is printed as a markdown table for the PR.
   `--clocks-only` skips stage 2, `--list` names the scenarios, `--update`
   rewrites the baselines, `--help` prints the rest.
   **Run it after every commit that touches `serving/`** — it is cheap enough,
   and it is how the 8-of-19 regression on the perf branch was caught. (2026-08-24)
2. For the *size* of an accuracy change, not just its presence:
   `./bench/examples/validate.sh` regenerates `validation/summary.txt` and the
   three plots. A changed `sim.csv` makes those stale, so regenerate and commit
   them in the same commit. (2026-08-24)
3. For profiler changes: edit `MODEL` / `HARDWARE` in `profiler/profile.sh`
   and run `./profiler/profile.sh` from the repo root inside the vLLM container. (2026-04-26)

Before adding or choosing a scenario, read `knowledge/simulator/validation-scenarios.md` (what the scenarios
exercise). (2026-10-14)

## Common Pitfalls (2026-10-15)

Approval: user, 2026-10-15: "좋아. 그렇게 바꿔줘."

Each item is a rule; its explanation and history are in the pitfall entry named.

- **Don't edit `astra-sim/`** unless the change targets simulator integration; after editing `llm_converter.py` reinstall Chakra in the container (see `knowledge/pitfalls/sim-edit-astra-sim.md`). (2026-08-20)
- **Don't commit large files** (generated traces, `.et` files, scratch run output); `--keep-inputs` and `--save-trace-text` can leave gigabytes in `astra-sim/inputs/runs/` (see `knowledge/pitfalls/sim-large-files.md`). (2026-08-23)
- **Don't use machine-specific absolute paths** in configs or code — use relative paths rooted at the repo (see `knowledge/pitfalls/sim-absolute-paths.md`). (2026-04-26)
- **Don't add `getattr` fallbacks** for Request attributes — initialize all attributes in `Request.__init__` and access directly (see `knowledge/pitfalls/sim-getattr-fallbacks.md`). (2026-04-26)
- **Don't reintroduce `is_prefill()` or a prefill/decode branch in the scheduler**; classify for the trace by scheduled token count (see `knowledge/pitfalls/sim-is-prefill.md`). (2026-08-19)
- **Don't add a "preserve the decode state on preemption" special case** (see `knowledge/pitfalls/sim-preserve-decode-state.md`). (2026-08-19)
- **Don't derive sequence length from `num_computed_tokens`** — use `num_tokens_reached` (see `knowledge/pitfalls/sim-seq-len-from-computed.md`). (2026-08-19)
- **Don't split pipeline stages by trace-line count**; cut only on transformer-block boundaries (`pp_stage_boundaries`) (see `knowledge/pitfalls/sim-pp-split-by-lines.md`). (2026-08-20)
- **Don't gate a DP batch on which NPU is asking** (route on `len(batch.fired) == 1`), and never hand an NPU a DP batch whose `workload_name` is still `None` (see `knowledge/pitfalls/sim-dp-gate-on-npu.md`). (2026-08-21)
- **Don't give a DP group one slot per member anywhere**: `dp_pending[dg][inst]` and `dp_ready_workloads[npu]` are FIFOs (see `knowledge/pitfalls/sim-dp-single-slot.md`). (2026-08-24)
- **Don't let the start NPU's join depend on the pipeline being full**: `schedule()` tries `_schedule_existing` before the `len(inflight) >= pp_size` cap (see `knowledge/pitfalls/sim-start-npu-join.md`). (2026-08-24)
- Read `agents/SIM-REFERENCE.md` "Rules from the reference sections" before calculating model head dimensions. (2026-04-26)
- **Use canonical vLLM layer names**; every name the simulator emits must also appear in the architecture yaml's catalog (see `knowledge/pitfalls/sim-layer-names.md`). (2026-04-26)
- **Profiler CSVs store microseconds** (`time_us`); the simulator converts to nanoseconds at load time (see `knowledge/pitfalls/sim-profiler-microseconds.md`). (2026-04-26)
- **First and last trace layers must use REMOTE** (see `knowledge/pitfalls/sim-first-last-remote.md`). (2026-04-26)
- **memory_expansion.json only has remote_mem by default**: local_mem exists only with `--enable-local-offloading` (see `knowledge/pitfalls/sim-local-mem-default.md`). (2026-04-26)
- **Don't edit `astra-sim/inputs/` files by hand**: `config_builder.py` regenerates them on every run (see `knowledge/pitfalls/sim-inputs-regenerated.md`). (2026-04-26)
