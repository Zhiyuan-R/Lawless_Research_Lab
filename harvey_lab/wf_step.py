"""Glue steps for running LAB session-mode tasks from a Workflow, one command per step.

  wf_step.py prepare <task>      start the sandbox + brief (run by the solver agent itself)
  wf_step.py post-agent <task>   stop sandbox, audit solver transcript, build judge bundle
                                  (run by the judge agent before it grades)
  wf_step.py post-judge <task>   audit judge transcript, write official scores, clean up

All state writes go through batch_state.json under an exclusive file lock, so several
workflows can run in parallel. Each step prints one JSON line.

Transcripts are found by a marker in the agent's first prompt: the solver prompt carries
"LABRUN-SOLVER::<task>", the judge prompt "LABRUN-JUDGE::<task>". Steps only receive the
task id and build the marker internally, so no other agent's transcript contains it.
"""

import fcntl
import json
import shutil
import subprocess
import sys
from contextlib import contextmanager
from pathlib import Path

HERE = Path(__file__).resolve().parent
STATE = HERE / "batch_state.json"
LOCK = HERE / ".batch_state.lock"
SESSION_DIRS = [Path("/root/.claude/projects"), Path("/tmp/claude-0")]


@contextmanager
def locked_state():
    with open(LOCK, "w") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        state = json.loads(STATE.read_text())
        yield state
        tmp = STATE.with_suffix(".tmp")
        tmp.write_text(json.dumps(state, indent=1))
        tmp.replace(STATE)


def read_state() -> dict:
    with open(LOCK, "w") as lk:
        fcntl.flock(lk, fcntl.LOCK_SH)
        return json.loads(STATE.read_text())


def session(*args: str) -> str:
    out = subprocess.run([str(HERE / "session.sh"), *args], capture_output=True, text=True)
    if out.returncode != 0:
        raise RuntimeError(f"session.sh {args[0]} failed: {out.stderr[-1500:]}")
    return out.stdout


def find_transcript(marker: str) -> str | None:
    """The agent transcript whose opening prompt contains the marker (largest if several)."""
    hits = []
    for root in SESSION_DIRS:
        for p in root.rglob("*.jsonl"):
            try:
                with open(p, errors="replace") as f:
                    head = "".join(f.readline() for _ in range(4))
            except OSError:
                continue
            if marker in head:
                hits.append(p)
    for root in SESSION_DIRS:
        for p in root.rglob("*.output"):
            try:
                with open(p, errors="replace") as f:
                    head = "".join(f.readline() for _ in range(4))
            except OSError:
                continue
            if marker in head:
                hits.append(p)
    return str(max(hits, key=lambda p: p.stat().st_size)) if hits else None


def audit(role: str, transcript: str | None, run_dir: Path) -> dict:
    if transcript is None:
        result = {"role": role, "clean": False, "violations": ["transcript not found"], "warnings": []}
        (run_dir / f"audit_{role}.json").write_text(json.dumps(result, indent=2))
        return result
    subprocess.run([sys.executable, str(HERE / "audit_transcript.py"), role, transcript, str(run_dir)],
                   capture_output=True, text=True)
    return json.loads((run_dir / f"audit_{role}.json").read_text())


def prepare(task: str) -> dict:
    with locked_state() as state:
        s = state[task]
        if s["status"] == "done":
            return {"skip": True, "reason": "already done"}
        if s["status"] in ("agent_running", "judge_running", "scoring") and s.get("run_dir"):
            return {"skip": True, "reason": f"already {s['status']}"}
        s["status"] = "preparing"
    try:
        info = json.loads(session("prepare-agent", task))
    except Exception as e:  # noqa: BLE001
        with locked_state() as state:
            state[task].update(status="failed", reason=f"prepare: {e}"[:500])
        return {"error": str(e)[:500]}
    with locked_state() as state:
        state[task].update(status="agent_running", run_id=info["run_id"], run_dir=info["run_dir"])
    return {"run_dir": info["run_dir"], "brief": info["brief"], "sbx": str(HERE / "sbx.sh")}


def post_agent(task: str) -> dict:
    s = read_state()[task]
    if s["status"] != "agent_running":
        return {"error": f"task status is {s['status']}, expected agent_running"}
    run_dir = Path(s["run_dir"])
    transcript = find_transcript("LABRUN-" + "SOLVER::" + task)
    session("finish-agent", s["run_id"])
    a = audit("agent", transcript, run_dir)
    try:
        info = json.loads(session("prepare-judge", s["run_id"], task))
    except Exception as e:  # noqa: BLE001
        with locked_state() as state:
            state[task].update(status="failed", reason=f"prepare-judge: {e}"[:500], agent_audit_clean=a["clean"])
        return {"error": str(e)[:300]}
    with locked_state() as state:
        state[task].update(status="judge_running", agent_audit_clean=a["clean"], agent_transcript=transcript,
                           judge_bundle=info["bundle"], judge_responses=info["responses"],
                           n_criteria=info["criteria"], bundle_chars=info["bundle_chars"])
    return {"bundle": info["bundle"], "responses": info["responses"], "criteria": info["criteria"],
            "bundle_chars": info["bundle_chars"]}


def post_judge(task: str) -> dict:
    s = read_state()[task]
    if s["status"] != "judge_running":
        return {"error": f"task status is {s['status']}, expected judge_running"}
    run_dir = Path(s["run_dir"])
    transcript = find_transcript("LABRUN-" + "JUDGE::" + task)
    a = audit("judge", transcript, run_dir)
    try:
        session("finalize", s["run_id"], task)
    except Exception as e:  # noqa: BLE001
        with locked_state() as state:
            state[task].update(status="failed", reason=f"finalize: {e}"[:500], judge_audit_clean=a["clean"])
        return {"error": str(e)[:300]}
    scores = json.loads((run_dir / "scores.json").read_text())
    shutil.rmtree(run_dir / "workspace", ignore_errors=True)
    with locked_state() as state:
        state[task].update(status="done", judge_audit_clean=a["clean"], judge_transcript=transcript,
                           n_passed=scores["n_passed"], n_criteria=scores["n_criteria"],
                           all_pass=scores["all_pass"], n_grading_errors=scores["n_grading_errors"])
    return {"task": task, "passed": scores["n_passed"], "criteria": scores["n_criteria"],
            "all_pass": scores["all_pass"], "agent_audit_clean": s.get("agent_audit_clean"),
            "judge_audit_clean": a["clean"]}


if __name__ == "__main__":
    cmd, task = sys.argv[1], sys.argv[2]
    try:
        out = {"prepare": prepare, "post-agent": post_agent, "post-judge": post_judge}[cmd](task)
    except Exception as e:  # noqa: BLE001
        out = {"error": f"{type(e).__name__}: {e}"[:500]}
    print(json.dumps(out))
