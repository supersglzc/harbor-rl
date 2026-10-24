# Use HARBOR with Codex

HARBOR is available as a Codex plugin alongside its Claude Code plugin. The
Codex package exposes a `$harbor` skill. It uses the same task specifications,
training scripts, evaluation gates, and experiment artifacts as Claude Code.

## Install

With a current Codex CLI, register the HARBOR repository as a marketplace:

```bash
codex plugin marketplace add supersglzc/harbor-rl
codex plugin add harbor@harbor-codex
codex
```

Alternatively, open `/plugins`, select **HARBOR for Codex**, and install
**harbor**. Start a new Codex session before using the skill.

For development from a local checkout, use
`codex plugin marketplace add /path/to/harbor-rl` instead.

In your **simulator repository**, ask Codex:

> $harbor Inspect this Isaac Lab checkout, validate the existing RL training
> setup, and create a task that pushes a cube to a goal.

Or for an existing task:

> $harbor Tune PPO for my existing task and compare candidates against its
> fixed evaluation.

## How it works

The skill reads HARBOR's existing `commands/`, `agents/`, and `knowledge/`
files, then executes the relevant `scripts/` and stage gates using Codex's
tools. It interprets Claude Code dispatch instructions as workflow guidance;
it does not run Claude-only slash commands or depend on Claude's agent API.

The plugin root is separate from the target simulator checkout. HARBOR outputs
remain under the target's `harbor/` directory. No additional MCP server is
required.

The packaged Codex skill supports sequential execution of the setup,
task-authoring, reward-tuning, and RL experiment workflows. Claude-specific
parallel agent dispatch and the Claude lifecycle hooks are not installed in
Codex. Cluster training continues to require the target's configured
SLURM tools.

Refer to [the end-to-end workflow](end-to-end.md) for the individual stages
and their validation gates.
