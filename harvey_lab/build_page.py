"""Render session_results/overview.html from summary.json (run build_summary.py first)."""

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
summary = json.loads((HERE / "session_results" / "summary.json").read_text())
zh = json.loads((HERE / "zh_names.json").read_text())
cats = json.loads((HERE / "failure_categories.json").read_text())

tasks = []
for t in summary["tasks"]:
    area_zh, name_zh = zh[t["task"]]
    tasks.append({
        "task": t["task"], "area": area_zh, "name": name_zh, "title": t["title"],
        "work_type": t["work_type"], "n": t["n_criteria"], "p": t["n_passed"], "all_pass": t["all_pass"],
        "docs": t["n_docs"], "docs_read": t["docs_read"], "minutes": t["minutes"], "pilot": t["pilot"],
        "deliverables": t["deliverables"],
        "failed": [{"id": f["id"], "title": f["title"], "cat": cats["assign"].get(f"{t['task']}|{f['id']}", "other"),
                    "reason": f["reasoning"]} for f in t["failed"]],
    })

data = {"tasks": tasks, "totals": summary["totals"], "agreement": summary["judge_agreement"],
        "categories": cats["labels"], "notes": cats["notes"]}
template = (HERE / "overview_template.html").read_text()
out = template.replace("__DATA__", json.dumps(data, ensure_ascii=False).replace("</", "<\\/"))
(HERE / "session_results" / "overview.html").write_text(out)
print("wrote overview.html", len(out))
