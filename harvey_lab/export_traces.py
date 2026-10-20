"""Copy every scored session-mode run (traces + scores) into harvey_lab/harvey_sampled_traces/.

One folder per task (task id with "/" -> "__"):
  solver_transcript.jsonl   full Claude Code transcript of the solver subagent
  judge_transcript.jsonl    full transcript of the independent judge subagent
  AGENT_BRIEF.md            the brief the solver was given (official system prompt + task)
  commands.jsonl            every sandbox command the solver ran, with timestamps
  output/                   the deliverables
  judge_bundle.md           what the judge was given (official prompt, outputs, criteria)
  judge_responses.json      the judge's per-criterion verdicts and reasoning
  scores.json               official evaluate_run() result (per-criterion pass/fail)
  metrics.json, config.json, session.json, report.html, audit_agent.json, audit_judge.json
plus index.json with one row per task. The agent's scratch workspace is not copied.

Usage: python3 harvey_lab/export_traces.py
"""

import json
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "harvey_sampled_traces"
RESULTS = HERE / "vendor" / "harvey-labs" / "results"
SUBAGENTS = Path("/root/.claude/projects/-home-user-Lawless-Research-Lab/e6ee0c2f-0792-5702-ab58-265c3898fc2d/subagents")
# The first task was run by hand before the batch state existed.
PILOT = {"task": "corporate-ma/review-data-room-red-flag-review",
         "run_dir": str(RESULTS / "corporate-ma/review-data-room-red-flag-review/claude-code-session/20261015-065804"),
         "agent_transcript": str(SUBAGENTS / "agent-a52772d92329f3a70.jsonl"),
         "judge_transcript": str(SUBAGENTS / "agent-a362b9a50cb6cd4d5.jsonl")}
RUN_FILES = ("AGENT_BRIEF.md", "commands.jsonl", "scores.json", "metrics.json", "config.json",
             "session.json", "report.html", "audit_agent.json", "audit_judge.json")


def export(task: str, s: dict) -> dict:
    run_dir = Path(s["run_dir"])
    dst = OUT / task.replace("/", "__")
    dst.mkdir(parents=True, exist_ok=True)
    for name in RUN_FILES:
        if (run_dir / name).exists():
            shutil.copy(run_dir / name, dst / name)
    if (run_dir / "output").exists():
        shutil.copytree(run_dir / "output", dst / "output", dirs_exist_ok=True)
    judge_dir = Path(json.loads((run_dir / "judge" / "location.json").read_text())["judge_dir"])
    for src, name in ((judge_dir / "bundle.md", "judge_bundle.md"), (run_dir / "judge" / "bundle.md", "judge_bundle.md"),
                      (run_dir / "judge" / "responses.json", "judge_responses.json"),
                      (judge_dir / "responses.json", "judge_responses.json")):
        if src.exists() and not (dst / name).exists():
            shutil.copy(src, dst / name)
    for key, name in (("agent_transcript", "solver_transcript.jsonl"), ("judge_transcript", "judge_transcript.jsonl")):
        if s.get(key) and Path(s[key]).exists():
            shutil.copy(Path(s[key]).resolve(), dst / name)
    scores = json.loads((dst / "scores.json").read_text())
    audits = {r: json.loads((dst / f"audit_{r}.json").read_text())["clean"] for r in ("agent", "judge")
              if (dst / f"audit_{r}.json").exists()}
    return {"task": task, "folder": dst.name, "run_id": scores["run_id"], "n_criteria": scores["n_criteria"],
            "n_passed": scores["n_passed"], "all_pass": scores["all_pass"], "judge_model": scores["judge_model"],
            "agent_audit_clean": audits.get("agent"), "judge_audit_clean": audits.get("judge"),
            "files": sorted(p.name for p in dst.iterdir())}


def main() -> None:
    state = json.loads((HERE / "batch_state.json").read_text())
    rows = [export(PILOT["task"], PILOT)]
    rows += [export(task, s) for task, s in state.items() if s["status"] == "done"]
    (OUT / "index.json").write_text(json.dumps(rows, indent=1))
    missing = [(r["task"], f) for r in rows for f in ("solver_transcript.jsonl", "judge_transcript.jsonl",
               "scores.json", "judge_responses.json", "judge_bundle.md") if f not in r["files"]]
    print(f"{len(rows)} tasks exported to {OUT}; missing files: {missing or 'none'}")


if __name__ == "__main__":
    main()
