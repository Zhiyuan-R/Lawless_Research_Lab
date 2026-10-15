#!/usr/bin/env bash
# Run one Harvey LAB task end to end: agent run -> rubric grading -> HTML report.
#
# Usage: harvey_lab/run_task.sh <model> <task-id> [extra harness flags...]
#   harvey_lab/run_task.sh anthropic/claude-sonnet-4-6 corporate-ma/review-data-room-red-flag-review
#   harvey_lab/run_task.sh google/gemini-3.1-pro-preview tax/draft-cross-border-acquisition-tax-memo --reasoning-effort high
#
# Keys go in harvey_lab/vendor/harvey-labs/.env (ANTHROPIC_API_KEY, OPENAI_API_KEY, GOOGLE_API_KEY).
# Grading uses the standard Sonnet 4.6 + GPT-5.5 judge pair; set JUDGES to override,
# e.g. JUDGES="claude-sonnet-4-6" for a single judge (results are then not leaderboard-comparable).
set -euo pipefail
[[ $# -ge 2 ]] || { sed -n '2,11p' "$0"; exit 2; }
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENDOR="$HERE/vendor/harvey-labs"
export LAB_ROOT="$VENDOR"
MODEL="$1"; TASK="$2"; shift 2

lab() { uv run --project "$VENDOR" python -m "$@"; }

log="$(mktemp)"
trap 'rm -f "$log"' EXIT
lab lab_core.harness.run --model "$MODEL" --task "$TASK" "$@" | tee "$log"
RUN_ID="$(sed -n 's/^Run complete: //p' "$log" | tail -1)"
[[ -n "$RUN_ID" ]] || { echo "could not determine run id" >&2; exit 1; }

judge_args=()
[[ -n "${JUDGES:-}" ]] && read -r -a judge_args <<< "--judges $JUDGES"
lab lab_core.evaluation.run_eval --run-id "$RUN_ID" --task "$TASK" "${judge_args[@]}"
lab lab_core.evaluation.report --run-id "$RUN_ID"
echo "Report: $VENDOR/results/$RUN_ID/report.html"
