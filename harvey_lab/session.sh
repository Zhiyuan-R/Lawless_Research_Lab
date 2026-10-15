#!/usr/bin/env bash
# Wrapper for session_runner.py (Claude Code session as agent + judge, no API keys).
# Usage: harvey_lab/session.sh <prepare-agent|finish-agent|prepare-judge|finalize> ...
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export LAB_ROOT="$HERE/vendor/harvey-labs"
exec uv run --project "$LAB_ROOT" python "$HERE/session_runner.py" "$@" 2> >(grep -v UV_NATIVE_TLS >&2)
