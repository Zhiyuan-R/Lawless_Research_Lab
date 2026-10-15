"""Second-judge agreement check for session-mode LAB runs.

  rejudge.py prepare <task>...   copy each task's judge bundle to /tmp/lab-judging-b/<id>/
  rejudge.py agreement           compare judge B with judge A, per criterion and per task

Judge B sees the same bundle as judge A (and nothing of judge A's verdicts), in its
own directory, so the comparison measures how stable a single same-model judge is.
"""

import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
STATE = HERE / "batch_state.json"
ROOT_B = Path("/tmp/lab-judging-b")


def main() -> None:
    cmd, *tasks = sys.argv[1:]
    state = json.loads(STATE.read_text())
    if cmd == "prepare":
        for t in tasks:
            src = Path(state[t]["judge_bundle"])
            dst = ROOT_B / src.parent.name
            dst.mkdir(parents=True, exist_ok=True)
            shutil.copy(src, dst / "bundle.md")
            state[t]["judge_b_dir"] = str(dst)
            print(json.dumps({"task": t, "dir": str(dst)}))
        STATE.write_text(json.dumps(state, indent=1))
    elif cmd == "agreement":
        both = agree = a_only = b_only = 0
        rows = []
        for t, s in state.items():
            if "judge_b_dir" not in s or not (Path(s["judge_b_dir"]) / "responses.json").exists():
                continue
            a = json.loads((Path(s["run_dir"]) / "judge" / "responses.json").read_text())
            b = json.loads((Path(s["judge_b_dir"]) / "responses.json").read_text())
            va = {k: v["verdict"].lower() for k, v in a.items()}
            vb = {k: v["verdict"].lower() for k, v in b.items()}
            ids = sorted(set(va) & set(vb))
            same = sum(va[i] == vb[i] for i in ids)
            flips = [(i, va[i], vb[i]) for i in ids if va[i] != vb[i]]
            both += len(ids)
            agree += same
            a_only += sum(1 for i, x, y in flips if x == "pass")
            b_only += sum(1 for i, x, y in flips if y == "pass")
            pa = sum(v == "pass" for v in va.values())
            pb = sum(v == "pass" for v in vb.values())
            rows.append({"task": t, "n": len(ids), "a_pass": pa, "b_pass": pb, "agree": same,
                         "a_all_pass": pa == len(va), "b_all_pass": pb == len(vb),
                         "flips": [{"id": i, "a": x, "b": y, "a_reason": a[i]["reasoning"],
                                    "b_reason": b[i]["reasoning"]} for i, x, y in flips]})
        out = {"criteria_compared": both, "agreement": round(agree / both, 4) if both else None,
               "a_pass_b_fail": a_only, "a_fail_b_pass": b_only,
               "all_pass_agreement": sum(r["a_all_pass"] == r["b_all_pass"] for r in rows), "tasks": rows}
        (HERE / "judge_agreement.json").write_text(json.dumps(out, indent=1))
        print(json.dumps({k: v for k, v in out.items() if k != "tasks"}, indent=1))
        for r in rows:
            print(f"{r['task'][:60]:60s} A {r['a_pass']}/{r['n']}  B {r['b_pass']}/{r['n']}  agree {r['agree']}/{r['n']}")
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
