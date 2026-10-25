"""Codex plugin packaging must remain installable alongside Claude Code."""

import json
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]


def test_portable_manifest_matches_claude_plugin():
    codex = json.loads((ROOT / "plugin.json").read_text())
    claude = json.loads((ROOT / ".claude-plugin/plugin.json").read_text())
    assert codex["$schema"] == "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
    assert codex["name"] == claude["name"]
    assert codex["version"] == claude["version"]
    assert codex["description"]
    assert codex["skills"] == "./skills/"


def test_codex_marketplace_resolves_the_plugin_root():
    marketplace = json.loads((ROOT / ".agents/plugins/marketplace.json").read_text())
    assert marketplace["name"]
    assert len(marketplace["plugins"]) == 1
    entry = marketplace["plugins"][0]
    assert entry["name"] == "harbor"
    assert entry["source"]["source"] == "local"
    assert (ROOT / entry["source"]["path"]).resolve() == ROOT
    assert entry["policy"]["installation"] == "AVAILABLE"


def test_codex_skill_has_valid_frontmatter_and_existing_references():
    skill = ROOT / "skills/harbor/SKILL.md"
    source = skill.read_text()
    parts = source.split("---", 2)
    assert parts[0] == ""
    metadata = yaml.safe_load(parts[1])
    assert metadata["name"] == "harbor"
    assert len(metadata["description"]) > 30
    for reference in (
        "commands/env-install-uv.md",
        "commands/probe-benchmark.md",
        "commands/task-create.md",
        "commands/reward-tune.md",
        "commands/rl-run.md",
        "commands/rl-tune.md",
        "commands/rl-eval.md",
        "commands/rl-sweep.md",
        "commands/plot.md",
        "agents/benchmark-generator.md",
        "agents/rl-integration-generator.md",
        "agents/rl-tuning-agent.md",
        "knowledge/references/rl-tuning-agent/tuning-instruction.md",
        "docs/guide/end-to-end.md",
        "scripts/common/resolve_suite.py",
    ):
        assert reference in source, reference
        assert (ROOT / reference).is_file(), reference


def test_existing_claude_marketplace_is_preserved():
    marketplace = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text())
    assert marketplace["plugins"][0]["name"] == "harbor"


def test_every_claude_command_has_an_individual_codex_skill():
    commands = {p.stem for p in (ROOT / "commands").glob("*.md")}
    skills = {p.parent.name for p in (ROOT / "skills").glob("*/SKILL.md")}
    assert skills == {"harbor"} | {f"harbor-{name}" for name in commands}

    for name in sorted(commands):
        skill = ROOT / "skills" / f"harbor-{name}" / "SKILL.md"
        content = skill.read_text()
        parts = content.split("---", 2)
        assert parts[0] == "", skill
        metadata = yaml.safe_load(parts[1])
        assert metadata["name"] == f"harbor-{name}"
        assert len(metadata["description"]) > 30
        assert f"commands/{name}.md" in content
        assert "skills/harbor/SKILL.md" in content
        assert "run each required executable gate" in content


def test_destructive_codex_skill_requires_confirmation():
    content = (ROOT / "skills/harbor-reset-workspace/SKILL.md").read_text()
    assert "dry-run deletion plan" in content
    assert "explicit user confirmation" in content
    assert "If confirmation is unavailable, stop" in content
