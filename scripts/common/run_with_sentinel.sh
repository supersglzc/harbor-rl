#!/usr/bin/env bash
# run_with_sentinel.sh — run a command whose completion is an ARTIFACT, not an exit code.
#
# GPU-sim trainers routinely finish their real work — checkpoint written, output
# flushed — and then hang forever in simulator teardown. Waiting for a natural
# exit deadlocks the caller; killing on a timer throws away finished work. The
# only reliable completion signal is the sentinel the job itself produces.
#
# So: launch, poll for the sentinel, and once it appears give the process a short
# grace period to exit on its own before taking it down. A process killed AFTER
# its sentinel is a SUCCESS.
#
# Usage:
#   run_with_sentinel.sh --cmd "<shell command>"
#                        [--sentinel-file <path>]     # exists  => done
#                        [--sentinel-log  <substr>]   # in log  => done
#                        [--log <file>] [--poll 15] [--grace 60]
#                        [--kill-after 30] [--timeout 0]
#
# At least one of --sentinel-file / --sentinel-log is required; if both are given,
# EITHER firing counts as done.
#
# Exit codes:
#   0  sentinel observed (success, whether or not the process exited on its own)
#   1  process exited and no sentinel ever appeared (real failure)
#   2  usage error
#   3  --timeout elapsed with no sentinel (treated as a failure by callers)
set -uo pipefail

CMD=""; SENTINEL_FILE=""; SENTINEL_LOG=""; LOG=""
POLL=15; GRACE=60; KILL_AFTER=30; TIMEOUT=0

while [ $# -gt 0 ]; do
    case "$1" in
        --cmd)           CMD="$2"; shift 2 ;;
        --sentinel-file) SENTINEL_FILE="$2"; shift 2 ;;
        --sentinel-log)  SENTINEL_LOG="$2"; shift 2 ;;
        --log)           LOG="$2"; shift 2 ;;
        --poll)          POLL="$2"; shift 2 ;;
        --grace)         GRACE="$2"; shift 2 ;;
        --kill-after)    KILL_AFTER="$2"; shift 2 ;;
        --timeout)       TIMEOUT="$2"; shift 2 ;;
        -h|--help)       sed -n '2,30p' "$0"; exit 0 ;;
        *) echo "unknown arg: $1" >&2; exit 2 ;;
    esac
done

[ -n "$CMD" ] || { echo "--cmd is required" >&2; exit 2; }
[ -n "$SENTINEL_FILE" ] || [ -n "$SENTINEL_LOG" ] || {
    echo "one of --sentinel-file / --sentinel-log is required" >&2; exit 2; }
[ -n "$LOG" ] || LOG="$(mktemp)"

sentinel_seen() {
    [ -n "$SENTINEL_FILE" ] && [ -e "$SENTINEL_FILE" ] && return 0
    [ -n "$SENTINEL_LOG" ] && [ -f "$LOG" ] && grep -qF -- "$SENTINEL_LOG" "$LOG" && return 0
    return 1
}

# Own process group, so teardown reaches the simulator's children too.
setsid bash -c "$CMD" >"$LOG" 2>&1 &
CHILD=$!
# setsid makes the child the group leader. Querying ps here can race with
# setsid and return the caller's group, which stop_group would then kill.
PGID="$CHILD"

stop_group() {
    kill -TERM "-$PGID" 2>/dev/null
    for _ in $(seq 1 "$KILL_AFTER"); do
        kill -0 "-$PGID" 2>/dev/null || return 0
        sleep 1
    done
    kill -KILL "-$PGID" 2>/dev/null
    pkill -P "$CHILD" 2>/dev/null
    return 0
}

elapsed=0
while true; do
    if sentinel_seen; then
        echo "[sentinel] observed after ${elapsed}s; grace ${GRACE}s then teardown"
        waited=0
        while [ "$waited" -lt "$GRACE" ] && kill -0 "$CHILD" 2>/dev/null; do
            sleep 1; waited=$((waited + 1))
        done
        kill -0 "$CHILD" 2>/dev/null && stop_group
        wait "$CHILD" 2>/dev/null
        echo "[sentinel] done (log: $LOG)"
        exit 0
    fi

    if ! kill -0 "$CHILD" 2>/dev/null; then
        # One last look: the sentinel may have landed in the same tick it exited.
        sentinel_seen && { echo "[sentinel] observed at exit"; exit 0; }
        echo "[sentinel] process exited with no sentinel — FAILURE (log: $LOG)" >&2
        exit 1
    fi

    if [ "$TIMEOUT" -gt 0 ] && [ "$elapsed" -ge "$TIMEOUT" ]; then
        echo "[sentinel] timeout ${TIMEOUT}s with no sentinel — tearing down" >&2
        stop_group
        exit 3
    fi

    sleep "$POLL"
    elapsed=$((elapsed + POLL))
done
