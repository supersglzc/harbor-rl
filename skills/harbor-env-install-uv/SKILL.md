---
name: harbor-env-install-uv
description: Set up an isolated uv Python environment for an RL simulator repository and validate its dependencies.
---

# HARBOR: env-install-uv

Use this skill for the `env-install-uv` workflow in a robot RL repository.

1. Locate this `SKILL.md`. The HARBOR plugin root is two directories above its parent directory (`skills/harbor-env-install-uv/../..`). The target repository is the user's project, not the plugin checkout.
2. Read `<plugin-root>/skills/harbor/SKILL.md` for the common Codex execution rules. Read `<plugin-root>/commands/env-install-uv.md` for this workflow's inputs, procedure, and validation gates. Load referenced `agents/`, `knowledge/`, and `scripts/` files as needed.
3. Execute the command's workflow with Codex file, shell, and optional subagent tools. Treat Claude Code-specific `/harbor:...` and `Agent(...)` syntax as workflow references, not runnable Codex commands. Do not create a second implementation of the same command.
4. Use the target repository's existing HARBOR artifacts, run each required executable gate, stop on a failed gate, and report the actual results and artifact paths.