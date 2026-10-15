# agents.md

Rules for coding agents (Claude Code, Codex and others), kept in two parts.

## Part 1: general files (repository root)

These are repository-independent and reusable as they are:

- `GENERAL.md`: roles and spawning, delegation, decision rights and escalation, briefs and reports, tests and
  review, handover between sessions, safe git and process habits, and the general skills.
- `USER.md`: the contract between the user and the agents (the user's part and the options).
- `skills/<name>/SKILL.md`: the general skills (procedures an agent loads when a task matches).

## Part 2: `llmservingsim/`

The rule set of one concrete repository (LLMServingSim), as a worked example of how the general files are
adopted: its `AGENTS.md` entry file, the role files under `agents/`, the agent definitions and hooks under
`.claude/`, and the generator and publishing scripts.

## Adopting the general files in another repository

1. Copy `GENERAL.md` and `USER.md` into the repository, and the skills into `.claude/skills/`.
2. Write the repository's own `AGENTS.md`, with a term map in the style of section 0.4 of
   `llmservingsim/AGENTS.md` that maps the general terms (handoff file, decisions list, task trail, ...) to the
   repository's own files.
3. Mark the sections that are not tied to the repository with `<!-- general -->` on the line after their heading,
   and write them in general terms.
4. Run a generator like `llmservingsim/agents/gen_general.py` to rebuild `GENERAL.md` from the marked sections,
   and a publisher like `llmservingsim/agents/publish_agentsmd.py` to sync this layout.

## Provenance

The root files are generated from LLMServingSim and are edited there, never in this repository: change the
marked section in the source repository, regenerate, and run `python3 agents/publish_agentsmd.py`.

Source commit of the last sync: e4504406
