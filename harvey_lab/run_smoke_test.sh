#!/usr/bin/env bash
# Keyless pipeline check: scripted agent -> podman sandbox -> deliverables -> grader extraction.
# Usage: harvey_lab/run_smoke_test.sh [task-id]
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENDOR="$HERE/vendor/harvey-labs"
export LAB_ROOT="$VENDOR"
exec uv run --project "$VENDOR" python "$HERE/smoke_test.py" "$@"
