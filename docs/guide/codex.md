# Use HARBOR with Codex

HARBOR is available as a Codex plugin alongside its Claude Code plugin. The
Codex package exposes a general `$harbor` skill and a separate skill for each
of the 23 Claude Code commands. They use the same task specifications,
training scripts, evaluation gates, and experiment artifacts.

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

Or select the task-creation workflow directly:

> $harbor-task-create name=Isaac-Push-Block-v0 description="Push a block to a target"

Or for an existing task:

> $harbor-rl-tune Tune PPO for my existing task and compare candidates against its
> fixed evaluation.

Each `commands/<name>.md` has a matching `$harbor-<name>` skill. Common examples:

| Claude Code command | Codex skill |
| --- | --- |
| `/harbor:task-create` | `$harbor-task-create` |
| `/harbor:task-clone` | `$harbor-task-clone` |
| `/harbor:probe-task` | `$harbor-probe-task` |
| `/harbor:reward-tune` | `$harbor-reward-tune` |
| `/harbor:rl-run` | `$harbor-rl-run` |
| `/harbor:rl-eval` | `$harbor-rl-eval` |
| `/harbor:rl-render` | `$harbor-rl-render` |
| `/harbor:rl-tune` | `$harbor-rl-tune` |
| `/harbor:rl-sweep` | `$harbor-rl-sweep` |
| `/harbor:help` | `$harbor-help` |

Use the skill picker or type `$harbor-` to find the available entries. Codex
uses `$skill-name` invocation; Claude Code's `/harbor:...` syntax does not run
in Codex. The destructive `$harbor-reset-workspace` skill requires an explicit
request and confirmation after the dry run.

## How it works

Each skill reads HARBOR's shared Codex rules and its corresponding file in
`commands/`, then executes the relevant `agents/`, `knowledge/`, `scripts/`,
and stage gates using Codex's tools. It interprets Claude Code dispatch
instructions as workflow guidance; it does not run Claude-only slash commands
or depend on Claude's agent API.

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
