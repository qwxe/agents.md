# agents/CODEX.md — Codex research worker

Scope: Codex, and any Claude agent that calls Codex. Codex reads only "Codex's own rules" and ignores the rest. Sections marked `<!-- general -->` are copied into `GENERAL.md` (AGENTS.md 0.2).

## I.4 Codex CLI (2026-10-14)
<!-- general -->

### Codex's own rules

Codex is a research worker. It works read-only; it never commits, pushes or launches runs or long jobs; it answers in
the language the brief asks for; it cites a source (URL, paper, file path) for each claim and marks what it could
not verify; it lists open points instead of deciding them; it never prints token or credential files. Its output is a second opinion that the caller verifies.

### Calling Codex (Claude agents)

Run it on the host, not inside a build or run container; it needs no job slot (the one exception to "no
CPU outside your slot"), but don't run many at once. `--search` enables live web search for literature work.

```
timeout 600 "$CODEX" [--search] exec --ephemeral -s read-only --color never -m <model> -c model_reasoning_effort="<level>" \
  -C <repo> -o "$SCRATCH/codex_last.txt" "<prompt>" </dev/null >"$SCRATCH/codex.out" 2>"$SCRATCH/codex.err"
```

- `$CODEX` is the installed codex binary; where it lives on this machine is in the repository's `AGENTS.md`.
- Always `</dev/null` (else it waits on stdin); for a long brief pass `-` and pipe it on stdin. The answer is in
  the `-o` file. Add `--skip-git-repo-check` outside a git repo. Never `--dangerously-bypass-approvals-and-sandbox`.
- Always pass the effort: unset, it runs at `low`.

| job | model | flags |
|---|---|---|
| find docs/papers/source, summarise with sources | Luna | `-m gpt-6-luna -c model_reasoning_effort="medium"` |
| judge assumptions, complexity, pros/cons; choose what to investigate; mixed jobs | Sol Light | `-m gpt-6.1-sol -c model_reasoning_effort="low"` |
| correctness checks, hard counterexamples, comparing designs | Sol Medium+ | `-m gpt-6.1-sol -c model_reasoning_effort="medium"` (or `high`/`xhigh`) |

## Codex in this repository (2026-10-14)

- Binary (not on PATH; the path changes with every VS Code extension update):
  `CODEX=$(ls -d ~/.vscode-server/extensions/openai.chatgpt-*/bin/linux-x86_64/codex | tail -1)`.
- `-C /home/asd/LLMServingSim`. Host only, never in `servingsim_docker`; no `slotrun` slot.
- Install details and more flags, if a flag above is missing: `AN/CODEX-DETAIL.md` (research branch, 0.4).

## Codex pitfalls (2026-10-14)
<!-- general -->

- Running without `</dev/null`: it waits on stdin forever.
- Omitting the reasoning effort: it runs at `low`.
- Relying on an answer without opening its sources: Codex output is a second opinion.
