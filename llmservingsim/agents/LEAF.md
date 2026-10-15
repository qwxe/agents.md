# agents/LEAF.md — the leaf agent

Scope: a Claude leaf agent, an agent that cannot spawn agents: every depth-three Opus working agent (for example
one of several brainstorming generators) and any other agent its caller launches with the `leaf` custom type.
Follow the leaf startup row and action triggers in `AGENTS.md` 0.1; the Leaf duties below are the full reference.
Sections marked `<!-- general -->` are generated into `GENERAL.md` (AGENTS.md 0.2). (2026-10-15)

## Core card (2026-10-15)

Approval: user, 2026-10-15: "preflight를 넣을 필요 없어. leaf worker 등 agent를 스폰할 수 없는 역할의 markdown 파일을 새로 만들어." then chose "type + 역할 파일 (Recommended)" (decisions list "Leaf role; no manager preflight").

Derived reading view: follow AGENTS.md 0.1 and read each triggered reference before acting; full source rules and role limits remain binding.

1. Read the assigned role's startup set from disk at current main HEAD; compare the brief's rule-source commit and reread changed sections before acting. (2026-10-15) — AGENTS 0.1 (O8)
2. Do the one working activity your brief names, within its write, resource and depth limits; your tier is the one the brief's *Resources* names. (2026-10-15) — Leaf duties; I.3/I.12
3. Never spawn or coordinate agents, through Agent, Bash/CLI or any other route. (2026-10-15) — Leaf duties; I.15
4. Never judge or accept a result you are part of; your caller assigns any acceptance or ranking to an independent verifier. (2026-10-15) — Leaf duties; I.14
5. Report to your caller only, with F-report (I.24) and the brief's report language. (2026-10-15) — I.13
6. Must escalate any ambiguity immediately through the caller chain (master: to user); never answer it from historical records, which are attached only as dated source references; plainly applicable current standing decisions still bind. (2026-10-15) — I.11 (O3)

Startup: disk selector/card, full 0.3, II.1, brief and the task documents and knowledge it names. Triggers: the
common gates; I.12 before a premise check or read-back the brief asks for; I.14 before code or tests; operations
before git, launch or cleanup the brief allows; I.21 before knowledge writing; I.13 before reporting. (2026-10-15)

## Leaf duties (2026-10-15)
<!-- general -->

Approval: user, 2026-10-15: "preflight를 넣을 필요 없어. leaf worker 등 agent를 스폰할 수 없는 역할의 markdown 파일을 새로 만들어." then chose "type + 역할 파일 (Recommended)" (the decisions list).

1. **What a leaf is.** An agent that cannot spawn agents, by permission: its custom agent type has no
   agent-spawning tool. A depth-two agent that needs an agent at depth three launches it as a leaf. (2026-10-15)
2. **Read first** the leaf startup set (the role selector lists it), the brief, and the task documents and
   knowledge base categories the brief names. (2026-10-15)
3. **One working activity.** Do the one activity the brief names (for example generating candidates, a source
   summary, an analysis or a bounded implementation), within the brief's write, resource and depth limits. The
   activity never changes the leaf's role or rights. Its tier is the one the brief's *Resources* names (I.3); an
   Opus parent does not make it hard tier. (2026-10-15)
4. **Never spawn or coordinate.** A leaf never spawns, launches or coordinates another agent, through any tool,
   Bash/CLI or other invocation route (I.15). Jobs it may launch are only those its brief authorizes, and it
   monitors them itself (I.18). (2026-10-15)
5. **Never judge its own result.** A leaf never judges or accepts a result it is part of. When candidates need
   ranking or a result needs acceptance, it reports them to its caller, which assigns an independent verifier
   (I.14). (2026-10-15)
6. **Report** to its caller only, in the F-report format (I.24) and the brief's report language; escalate any
   ambiguity at once through the caller chain (I.11). (2026-10-15)
