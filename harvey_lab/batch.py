"""Drive a batch of session-mode LAB runs, one step per command.

State lives in harvey_lab/batch_state.json so the batch survives restarts.

  batch.py next                         start the next pending task's sandbox; print its brief
  batch.py agent-done <task> <transcript>   finish agent, audit it, build the judge bundle
  batch.py judge-done <task> <transcript>   audit judge, finalize scores + report
  batch.py fail <task> <reason>         mark a task failed (kept in the summary)
  batch.py set <task> <key> <value>     record e.g. the agent_id / judge_id
  batch.py status                       one line per task
"""

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
STATE = HERE / "batch_state.json"
TASKS = HERE / "batch_tasks.json"
RESULTS = HERE / "vendor" / "harvey-labs" / "results"


def load() -> dict:
    if STATE.exists():
        return json.loads(STATE.read_text())
    state = {t["id"]: {"status": "pending", **t} for t in json.loads(TASKS.read_text())}
    save(state)
    return state


def save(state: dict) -> None:
    STATE.write_text(json.dumps(state, indent=1))


def session(*args: str) -> str:
    out = subprocess.run([str(HERE / "session.sh"), *args], capture_output=True, text=True)
    if out.returncode != 0:
        raise SystemExit(f"session.sh {args[0]} failed:\n{out.stderr[-2000:]}")
    return out.stdout


def audit(role: str, transcript: str, run_dir: Path) -> dict:
    subprocess.run([sys.executable, str(HERE / "audit_transcript.py"), role, transcript, str(run_dir)],
                   capture_output=True, text=True)
    return json.loads((run_dir / f"audit_{role}.json").read_text())


def main() -> None:
    cmd, *rest = sys.argv[1:]
    state = load()
    if cmd == "next":
        task = next((k for k, v in state.items() if v["status"] == "pending"), None)
        if task is None:
            print("NONE")
            return
        info = json.loads(session("prepare-agent", task))
        state[task].update(status="agent_running", run_id=info["run_id"], run_dir=info["run_dir"])
        save(state)
        print(json.dumps({"task": task, "run_dir": info["run_dir"], "brief": info["brief"]}))
    elif cmd == "agent-done":
        task, transcript = rest
        s = state[task]
        session("finish-agent", s["run_id"])
        a = audit("agent", transcript, Path(s["run_dir"]))
        info = json.loads(session("prepare-judge", s["run_id"], task))
        s.update(status="judge_running", agent_audit_clean=a["clean"], agent_transcript=transcript,
                 judge_bundle=info["bundle"], judge_responses=info["responses"], n_criteria=info["criteria"],
                 bundle_chars=info["bundle_chars"])
        save(state)
        print(json.dumps({"task": task, "agent_audit_clean": a["clean"], "violations": a["violations"][:5],
                          "bundle": info["bundle"], "responses": info["responses"],
                          "criteria": info["criteria"], "bundle_chars": info["bundle_chars"]}))
    elif cmd == "judge-done":
        task, transcript = rest
        s = state[task]
        a = audit("judge", transcript, Path(s["run_dir"]))
        out = session("finalize", s["run_id"], task)
        scores = json.loads((Path(s["run_dir"]) / "scores.json").read_text())
        s.update(status="done", judge_audit_clean=a["clean"], judge_transcript=transcript,
                 n_passed=scores["n_passed"], n_criteria=scores["n_criteria"], all_pass=scores["all_pass"],
                 n_grading_errors=scores["n_grading_errors"])
        save(state)
        print(out.strip().splitlines()[0], "| judge audit clean:", a["clean"], a["violations"][:3])
    elif cmd == "fail":
        task, reason = rest
        state[task].update(status="failed", reason=reason)
        save(state)
    elif cmd == "set":
        task, key, value = rest
        state[task][key] = value
        save(state)
    elif cmd == "status":
        for k, v in state.items():
            extra = f"{v.get('n_passed')}/{v.get('n_criteria')}" if v["status"] == "done" else ""
            print(f"{v['status']:14s} {extra:8s} {k}")
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
