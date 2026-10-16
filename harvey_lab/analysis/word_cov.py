"""Word-level reading coverage, robust to parser/markup differences (pandoc versions, openpyxl dumps).
Share of distinct words (>= 6 letters) in each document that appear in the solver's tool output.
Run: cd harvey_lab/vendor/harvey-labs && uv run python ../../analysis/xlsx_cov.py"""
import json, re, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.argv = ["coverage.py", "0"]
import coverage as C  # noqa: E402  (reuses text_of / outputs; its main loop runs 0 tasks)
words = lambda s: set(re.findall(r"[a-z]{6,}", s.lower()))  # noqa: E731
cov = json.load(open(HERE / "coverage.json"))
rows = {r["task"]: r for r in json.load(open(HERE / "trace_stats.json"))}
for t, x in cov.items():
    xl = list(x["docs"])
    if not xl: continue
    seen = words(C.outputs(rows[t]["transcript"]))
    for d in xl:
        w = words(C.text_of(C.TASKS / t / "documents" / d))
        x["docs"][d]["word_cov"] = round(len(w & seen) / len(w), 3) if w else None
json.dump(cov, open(HERE / "coverage.json", "w"), indent=1)
v = [dd["word_cov"] for x in cov.values() for dd in x["docs"].values() if dd.get("word_cov") is not None]
print(len(v), "mean", round(sum(v) / len(v), 3), "<0.5:", sum(a < 0.5 for a in v))
