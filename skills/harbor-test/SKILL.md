---
name: harbor-test
description: Run HARBOR plugin contract, unit, and optional end-to-end validation suites.
---

# HARBOR: test

Use this skill for the `test` workflow in a robot RL repository.

1. Locate this `SKILL.md`. The HARBOR plugin root is two directories above its parent directory (`skills/harbor-test/../..`). The target repository is the user's project, not the plugin checkout.
2. Read `<plugin-root>/skills/harbor/SKILL.md` for the common Codex execution rules. Read `<plugin-root>/commands/test.md` for this workflow's inputs, procedure, and validation gates. Load referenced `agents/`, `knowledge/`, and `scripts/` files as needed.
3. Execute the command's workflow with Codex file, shell, and optional subagent tools. Treat Claude Code-specific `/harbor:...` and `Agent(...)` syntax as workflow references, not runnable Codex commands. Do not create a second implementation of the same command.
4. Use the target repository's existing HARBOR artifacts, run each required executable gate, stop on a failed gate, and report the actual results and artifact paths.