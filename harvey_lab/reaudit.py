"""Re-run both isolation audits for every scored task against the right transcripts.

The transcript for a role is the one carrying that task's marker AND this run's directory
(agent) or judge directory (judge); earlier lookups by size could pick a transcript from a
run that was killed and restarted. Updates batch_state.json and prints a summary.
Usage: python3 harvey_lab/reaudit.py
"""
import json
from pathlib import Path
import wf_step as W

with W.locked_state() as state:
    summary = {"agent": [0, 0, []], "judge": [0, 0, []]}
    for task, s in state.items():
        if s["status"] != "done" or not s.get("run_dir"):
            continue
        run_dir = Path(s["run_dir"])
        legacy = not (s.get("agent_transcript") or "").find("/workflows/") >= 0  # batch.py-era runs: paths given explicitly
        for role, marker, home in (("agent", "SOLVER", str(run_dir)), ("judge", "JUDGE", str(Path(s["judge_bundle"]).parent))):
            t = s.get(f"{role}_transcript") if legacy else W.find_transcript("LABRUN-" + marker + "::" + task, must_contain=home)
            a = W.audit(role, t, run_dir)
            s[f"{role}_transcript"], s[f"{role}_audit_clean"] = t, a["clean"]
            summary[role][0] += 1
            summary[role][1] += a["clean"]
            if not a["clean"]:
                summary[role][2].append((task, a["violations"][:2]))
for role, (n, ok, bad) in summary.items():
    print(f"{role}: {ok}/{n} clean")
    for b in bad:
        print("   ", b)
