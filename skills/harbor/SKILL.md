---
name: harbor
description: Use HARBOR to set up Isaac Lab, ManiSkill, Genesis, or another Python robot simulator; create and validate reinforcement-learning tasks; design and tune rewards; or train, evaluate, render, sweep, and tune RL policies. Use this skill when working on an existing simulation repository with HARBOR's tools and validation gates.
---

# HARBOR for Codex

Run HARBOR workflows in the **target simulator repository**, using the existing
HARBOR scripts, templates, and executable checks. The HARBOR plugin repository
contains the tools; the simulator repository contains the generated project.

For a single named command, prefer its matching `$harbor-<command>` skill
(for example, `$harbor-task-create` or `$harbor-rl-eval`). This general skill
remains available for selecting a workflow or coordinating multiple stages.

## Paths and runtime

- Locate this `SKILL.md` on disk. The HARBOR plugin root is two directories
  above it. Use that absolute path for `scripts/`, `agents/`, `commands/`,
  and `knowledge/` references. Do not assume the plugin and target repository
  are the same directory.
- Run project commands with the target repository as the working directory.
  Generated code, configs, logs, and checkpoints belong under
  `<target>/harbor/`, following the existing HARBOR layout.
- Read the relevant `commands/<operation>.md` and its referenced
  `agents/*.md` before starting a stage. Treat their task requirements, code
  examples, and gates as the source of truth. Load only references needed for
  the selected operation.
- Those files describe **Claude Code** entry points. In Codex, execute their
  workflow with the available file, shell, and optional subagent tools.
  `/harbor:...`, `Agent(...)`, `Skill(...)`, `AskUserQuestion`, and
  `SendMessage` are not shell commands or Codex APIs. Do not invoke them
  literally. Replace `${CLAUDE_PLUGIN_ROOT}` in documented shell examples
  with the resolved plugin root.
- Use the existing Python and shell scripts directly. Do not install Claude
  Code or generate a second RL training implementation to run this skill.

## Choose the HARBOR workflow

| Request | Read first | Goal |
| --- | --- | --- |
| Install simulator dependencies | `commands/env-install-uv.md`, `agents/dependency-generator.md` | Render and run isolated uv setup; pass import and device smoke tests |
| Discover a simulator's tasks | `agents/benchmark-generator.md`, `commands/probe-benchmark.md` | Verify rollout and rendering; write `benchmark-spec.json` and a task implementation guide |
| Integrate a training stack | `agents/rl-integration-generator.md` | Write the train/eval/render entry points; pass each algorithm's smoke tests |
| Create or clone a task | `commands/task-create.md` or `commands/task-clone.md` | Create scene, actions, reset, termination, observations, and reward with section gates |
| Optimize a reward | `commands/reward-tune.md`, `agents/reward-tuning-agent.md` | Iterate candidate rewards against real training and fixed success criteria |
| Train, evaluate, or render | `commands/rl-run.md`, `commands/rl-eval.md`, `commands/rl-render.md` | Execute the target's trainer and preserve checkpoints, metrics, and video |
| Tune or sweep RL parameters | `commands/rl-tune.md` or `commands/rl-sweep.md` | Compare recorded experiments under a controlled task and budget |
| Inspect results | `commands/plot.md`, `commands/rl-visualize.md` | Produce existing HARBOR plots and trajectory artifacts |

To create a new task from a description, follow the order in
`docs/guide/end-to-end.md`: dependency setup, benchmark probe, RL
integration, task creation, reward validation, then training. Reuse completed
stage artifacts. Start at the requested stage for an existing task.

## Execute each stage

1. Check the target repository, its existing `harbor/` artifacts, the selected
   simulator, and the available Python environment. Do not overwrite existing
   task implementations or local configurations.
2. Read the command/agent instructions for the selected stage and the
   referenced `knowledge/` material. Carry out the agent's concrete code
   editing and script invocations using Codex tools, rather than its
   Claude-specific dispatch syntax.
3. Run the corresponding **executable gate** described in the command. An
   import, finite reward, valid action, successful reset, render, or training
   checkpoint must come from an actual run, not from an agent's description.
4. On failure, inspect the generated artifacts and the gate's verdict or log;
   make a focused repair and rerun that gate. Stop the pipeline at any gate
   that cannot pass. Do not mark the stage complete.
5. Preserve the stage's standard paths and append results to its history.
   Report the exact command, evidence location, and any unverified stage.

For RL training, use the suite already recorded in
`harbor/rl-integration-generator/rl-suite-spec.json`. The existing
`scripts/common/resolve_suite.py --algo <name>` resolves its implementation,
config name, and training path. If the requested RL algorithm is not in the
suite, integrate it with `local_implementation` or the corresponding
generator workflow before attempting to train it.

## Experiment loops

Reward and algorithm tuning use recorded results to choose the **next**
candidate. Retain the existing target task's success criterion and evaluation
definition.

- For reward tuning, follow `commands/reward-tune.md`. Write each candidate
  into its isolated experiment directory. Implement the task/reward change,
  run its gates, train, evaluate, and decide whether it improved the fixed
  task success measure. Promote a candidate only after its source-task smoke
  checks pass.
- For RL tuning, follow `agents/rl-tuning-agent.md` and
  `knowledge/references/rl-tuning-agent/tuning-instruction.md`. Begin with
  the default-config baseline, test one change at a time, compare fixed
  metrics and runtime, then accept or revert. Honor the configured
  `stuck_threshold` and `max_iterations`.
- For a predeclared grid, follow `commands/rl-sweep.md`; do not present a
  sweep as a hypothesis-driven tuning loop.
- Use local execution unless the user requests cluster execution. Cluster
  examples use SLURM and require an available `sbatch`; never silently
  substitute a scheduler.

The upstream Claude workflow can delegate to specialized agents. Codex may
delegate a bounded stage if supported by its runtime, but it must keep stage
artifacts and gate results on disk. A sequential single-agent implementation
is valid. Do not claim concurrent candidate execution unless it happened.

## Completion

Give the target repository path, the command(s) executed, gate results, and
links or paths to the resulting specs, metrics, checkpoints, and renders. When
an experiment does not converge, report its actual metrics and final stop
reason. Never promote a failed smoke or an unverified policy.
