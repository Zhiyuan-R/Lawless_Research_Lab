#!/usr/bin/env bash
# Dump the plain text of a task's documents (same parser the sandbox uses), for post-hoc analysis.
# Usage: harvey_lab/analysis/doctext.sh <task_id> <out_dir>
set -uo pipefail
LAB="$(cd "$(dirname "$0")/.." && pwd)/vendor/harvey-labs"
SRC="$LAB/tasks/$1/documents"; OUT="$2"; mkdir -p "$OUT"
cd "$LAB"
find "$SRC" -type f | while read -r f; do
  rel="${f#$SRC/}"; dst="$OUT/${rel//\//__}.txt"
  ext="${f##*.}"; ext="${ext,,}"
  uv run --quiet python lab_core/sandbox/parsers/parse_doc.py "$ext" "$f" > "$dst" 2>/dev/null \
    || uv run --quiet markitdown "$f" > "$dst" 2>/dev/null || cp "$f" "$dst"
done
wc -c "$OUT"/* | tail -n +1
