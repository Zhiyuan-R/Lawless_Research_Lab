"""Reading coverage: what share of each task's document text reached the solver's eyes.

A document line (>= 40 chars after whitespace normalisation) counts as seen when it appears
in any tool output of the solver transcript. Run from the harvey-labs checkout with uv:
  cd harvey_lab/vendor/harvey-labs && uv run python ../../analysis/coverage.py
Adds per-document coverage to analysis/coverage.json.
"""
import json, re, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "vendor" / "harvey-labs" / "lab_core" / "sandbox" / "parsers"))
import parse_doc as P  # noqa: E402

TASKS = HERE.parent / "vendor" / "harvey-labs" / "tasks"
norm = lambda s: re.sub(r"[\s|*#_>\-]+", " ", s).strip().lower()  # noqa: E731

def text_of(p: Path) -> str:
    ext = p.suffix.lower()
    try:
        if ext == ".docx": return P.parse_docx(str(p))
        if ext == ".pdf": return P.parse_pdf(str(p))
        if ext == ".pptx": return P.parse_pptx(str(p))
        if ext in (".xlsx", ".xls"): return P.parse_xlsx(str(p))
        return p.read_text(errors="replace")
    except Exception:  # noqa: BLE001
        return ""

def outputs(transcript: str) -> str:
    chunks = []
    for line in open(transcript, errors="replace"):
        try: e = json.loads(line)
        except json.JSONDecodeError: continue
        c = (e.get("message") or {}).get("content")
        if isinstance(c, list):
            for b in c:
                if b.get("type") == "tool_result":
                    x = b.get("content")
                    chunks.append(x if isinstance(x, str) else "".join(y.get("text", "") for y in x or [] if isinstance(y, dict)))
    return norm("\n".join(chunks))

rows = json.load(open(HERE / "trace_stats.json"))
result = {}
for r in rows[:int(sys.argv[1]) if len(sys.argv)>1 else None]:
    if r["task"].startswith(("firm-knowledge/", "diligence/")): continue  # thousands of docs: retrieval, not reading
    seen = outputs(r["transcript"])
    docs = {}
    d = TASKS / r["task"] / "documents"
    for p in sorted(d.rglob("*")):
        if not p.is_file(): continue
        lines = [norm(l) for l in text_of(p).splitlines()]
        lines = [l for l in lines if len(l) >= 40]
        hit = sum(l[:200] in seen for l in lines)
        docs[str(p.relative_to(d))] = {"lines": len(lines), "seen": hit, "chars": sum(map(len, lines))}
    tot = sum(v["lines"] for v in docs.values()); hit = sum(v["seen"] for v in docs.values())
    result[r["task"]] = {"coverage": round(hit / tot, 3) if tot else None, "docs": docs}
    print(f"{result[r['task']]['coverage']}\t{r['task']}", flush=True)
(HERE / "coverage.json").write_text(json.dumps(result, indent=1))
