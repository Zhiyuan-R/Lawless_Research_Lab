"""Collect every finished session-mode run into session_results/ and summary.json.

For each done task: copies the deliverables, scores, metrics, audits and judge
verdicts into session_results/<run_id>/, and writes session_results/summary.json
with per-task scores, failed criteria, judge-agreement data and batch totals.
"""

import json
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
STATE = HERE / "batch_state.json"
OUT = HERE / "session_results"
PILOT = "corporate-ma/review-data-room-red-flag-review/claude-code-session/20261015-065804"
RESULTS = HERE / "vendor" / "harvey-labs" / "results"


def collect(run_dir: Path, run_id: str) -> None:
    dst = OUT / run_id
    dst.mkdir(parents=True, exist_ok=True)
    if (run_dir / "output").exists():
        shutil.copytree(run_dir / "output", dst / "output", dirs_exist_ok=True)
    for name in ("scores.json", "metrics.json", "config.json", "report.html", "commands.jsonl",
                 "audit_agent.json", "audit_judge.json"):
        if (run_dir / name).exists():
            shutil.copy(run_dir / name, dst / name)
    if (run_dir / "judge" / "responses.json").exists():
        shutil.copy(run_dir / "judge" / "responses.json", dst / "responses.json")


def task_row(task: str, run_dir: Path, run_id: str, extra: dict) -> dict:
    scores = json.loads((run_dir / "scores.json").read_text())
    metrics = json.loads((run_dir / "metrics.json").read_text())
    config = json.loads((HERE / "vendor/harvey-labs/tasks" / task / "task.json").read_text())
    audits = {r: json.loads((run_dir / f"audit_{r}.json").read_text())["clean"]
              for r in ("agent", "judge") if (run_dir / f"audit_{r}.json").exists()}
    return {
        "task": task, "area": task.split("/")[0], "title": config.get("title", ""),
        "work_type": config.get("work_type") or "contract", "run_id": run_id,
        "n_criteria": scores["n_criteria"], "n_passed": scores["n_passed"], "all_pass": scores["all_pass"],
        "failed": [{"id": c["id"], "title": c["title"], "reasoning": c["reasoning"]}
                   for c in scores["criteria_results"] if c["verdict"] != "pass"],
        "n_docs": metrics.get("total_documents"), "docs_read": metrics.get("documents_read"),
        "commands": metrics.get("turn_count"), "minutes": round(metrics.get("wall_clock_seconds", 0) / 60, 1),
        "deliverables": metrics.get("output_files", []),
        "audit_agent_clean": audits.get("agent", True), "audit_judge_clean": audits.get("judge", True),
        **extra,
    }


def main() -> None:
    state = json.loads(STATE.read_text())
    rows = []
    pilot_dir = RESULTS / PILOT
    collect(pilot_dir, PILOT)
    rows.append(task_row(PILOT.split("/claude-code-session")[0], pilot_dir, PILOT, {"pilot": True}))
    for task, s in state.items():
        if s["status"] != "done":
            continue
        run_dir = Path(s["run_dir"])
        collect(run_dir, s["run_id"])
        rows.append(task_row(task, run_dir, s["run_id"], {"pilot": False}))
    agreement = json.loads((HERE / "judge_agreement.json").read_text()) if (HERE / "judge_agreement.json").exists() else None
    tot_c = sum(r["n_criteria"] for r in rows)
    tot_p = sum(r["n_passed"] for r in rows)
    summary = {
        "tasks": rows,
        "skipped": [{"area": "diligence", "reason": "every task has 2,600-4,000 documents and 400-1,100 criteria"}]
        + [{"task": t, "reason": s.get("reason", s["status"])} for t, s in state.items() if s["status"] not in ("done",)],
        "totals": {"n_tasks": len(rows), "all_pass": sum(r["all_pass"] for r in rows),
                   "criteria": tot_c, "criteria_passed": tot_p,
                   "pooled_pass_rate": round(tot_p / tot_c, 4) if tot_c else None,
                   "mean_task_pass_rate": round(sum(r["n_passed"] / r["n_criteria"] for r in rows) / len(rows), 4),
                   "audits_clean": sum(r["audit_agent_clean"] and r["audit_judge_clean"] for r in rows)},
        "judge_agreement": agreement,
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=1, ensure_ascii=False))
    print(json.dumps(summary["totals"], indent=1))


if __name__ == "__main__":
    main()
