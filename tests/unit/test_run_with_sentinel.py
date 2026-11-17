"""Unit: scripts/common/run_with_sentinel.sh — completion is the artifact, not the exit code.

The three behaviors every caller depends on, and the reason each exists:

  - a job that produces its sentinel and then HANGS is a success (the GPU-sim teardown
    hang this script exists for) — and the hung process must not survive;
  - a job that dies without ever producing a sentinel is a failure, even if it exits 0;
  - a sentinel that lands in the same tick the process exits still counts.
"""
import os
import subprocess
import sys
import time

import pytest

from _pluginmeta import ROOT

SCRIPT = ROOT / "scripts" / "common" / "run_with_sentinel.sh"
FAST = ["--poll", "1", "--grace", "2", "--kill-after", "2"]


def _run(*args, timeout=60):
    return subprocess.run(["bash", str(SCRIPT), *args],
                          capture_output=True, text=True, timeout=timeout)


def test_sentinel_then_hang_is_success_and_the_process_is_reaped(tmp_path):
    sentinel = tmp_path / "checkpoint.pth"
    # The failure mode this script exists for: real work finishes, then teardown hangs.
    marker = tmp_path / "still_alive"
    cmd = (f"touch {sentinel}; "
           f"for i in $(seq 1 60); do touch {marker}; sleep 1; done")

    start = time.time()
    r = _run("--cmd", cmd, "--sentinel-file", str(sentinel), *FAST,
             "--log", str(tmp_path / "run.log"))
    took = time.time() - start

    assert r.returncode == 0, r.stderr
    assert took < 30, f"waited {took:.0f}s — it waited for the hang instead of the sentinel"

    marker.unlink(missing_ok=True)
    time.sleep(3)
    assert not marker.exists(), "the hung process group survived teardown"


def test_teardown_never_signals_the_callers_process_group(tmp_path):
    # Simulate ps observing the old parent group before setsid takes effect.
    # Isolate the launcher so the broken implementation cannot kill pytest.
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    fake_ps = fake_bin / "ps"
    fake_ps.write_text('#!/bin/sh\nprintf "%s\\n" "$TEST_CALLER_PGID"\n')
    fake_ps.chmod(0o755)

    sentinel = tmp_path / "done"
    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}:{env['PATH']}"
    env["HARBOR_SENTINEL_SCRIPT"] = str(SCRIPT)
    env["HARBOR_SENTINEL_FILE"] = str(sentinel)
    launcher = """
TEST_CALLER_PGID=$(/usr/bin/ps -o pgid= -p $$ | tr -d ' ')
export TEST_CALLER_PGID
exec bash "$HARBOR_SENTINEL_SCRIPT" \\
  --cmd 'touch "$HARBOR_SENTINEL_FILE"; sleep 10' \\
  --sentinel-file "$HARBOR_SENTINEL_FILE" \\
  --poll 1 --grace 0 --kill-after 1
"""
    r = subprocess.run(
        ["bash", "-c", launcher], start_new_session=True,
        capture_output=True, text=True, env=env, timeout=20,
    )
    assert r.returncode == 0, r.stderr
    assert sentinel.exists()


def test_exit_without_sentinel_is_failure(tmp_path):
    r = _run("--cmd", "exit 0", "--sentinel-file", str(tmp_path / "never"), *FAST)
    assert r.returncode == 1, "a clean exit with no artifact must not read as success"
    assert "no sentinel" in r.stderr


def test_log_substring_sentinel(tmp_path):
    r = _run("--cmd", "echo 'saved checkpoint to /tmp/x'; sleep 30",
             "--sentinel-log", "saved checkpoint to", *FAST,
             "--log", str(tmp_path / "run.log"))
    assert r.returncode == 0, r.stderr


def test_sentinel_landing_at_exit_is_not_missed(tmp_path):
    """Sentinel written immediately before exit — the poll may only see it post-mortem."""
    sentinel = tmp_path / "done"
    r = _run("--cmd", f"sleep 2; touch {sentinel}; exit 0",
             "--sentinel-file", str(sentinel), *FAST)
    assert r.returncode == 0, r.stderr


def test_timeout_without_sentinel(tmp_path):
    r = _run("--cmd", "sleep 60", "--sentinel-file", str(tmp_path / "never"),
             *FAST, "--timeout", "3")
    assert r.returncode == 3
    assert "timeout" in r.stderr


@pytest.mark.parametrize("args,reason", [
    ([], "no --cmd"),
    (["--cmd", "true"], "no sentinel of either kind"),
])
def test_usage_errors_exit_2(args, reason):
    assert _run(*args).returncode == 2, reason


def test_help_works():
    r = _run("--help")
    assert r.returncode == 0 and "sentinel" in r.stdout.lower()
