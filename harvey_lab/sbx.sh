#!/usr/bin/env bash
# Run one command inside a session run's sandbox and log it to <run_dir>/commands.jsonl.
# Usage: harvey_lab/sbx.sh <run_dir> '<bash command>'
set -uo pipefail
RUN_DIR="$1"; CMD="$2"
CONTAINER="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["container"])' "$RUN_DIR/session.json")"
python3 -c 'import json,sys,datetime; print(json.dumps({"ts": datetime.datetime.now(datetime.UTC).isoformat(), "command": sys.argv[1]}))' \
    "$CMD" >> "$RUN_DIR/commands.jsonl"
exec timeout 300 podman exec -w /workspace "$CONTAINER" bash -lc "$CMD"
