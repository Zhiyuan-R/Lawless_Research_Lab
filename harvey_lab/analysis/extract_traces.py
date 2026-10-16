"""Turn solver transcripts + scores into per-task trace digests and a stats table.

For every task whose solver finished (scored or not), writes
  analysis/traces/<slug>.json   ordered steps (command, output size, flags), thinking,
                                final message, and for scored tasks the failed criteria
  analysis/trace_stats.json     one row of behavioural metrics per task

Usage: python3 harvey_lab/analysis/extract_traces.py
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
LAB = HERE.parent
sys.path.insert(0, str(LAB))
from wf_step import find_transcript  # noqa: E402

STATE = LAB / "batch_state.json"
TASKS = LAB / "vendor" / "harvey-labs" / "tasks"
OUT = HERE / "traces"

LIMITERS = re.compile(r"\|\s*(head|tail)\b|\bsed -n\b|\[:\d+\]|\bhead -c\b|\bcut -c")
ERRORS = re.compile(r"Traceback \(most recent call last\)|\bError\b|No such file|command not found|"
                    r"SyntaxError|cannot access|Permission denied|timed out", re.I)
OUTPUT_TOUCH = re.compile(r"/workspace/output|\boutput/")
WRITES_DELIVERABLE = re.compile(r"\.save\(|docx\.Document\(|Workbook\(|> */workspace/output|pandoc .* -o ")
READBACK = re.compile(r"parse-doc[^|;&]*output/|Document\(['\"][^'\"]*output/|load_workbook\(['\"][^'\"]*output/")


def slug(task: str) -> str:
    return task.replace("/", "__")


def documents(task: str) -> list[str]:
    d = TASKS / task / "documents"
    return sorted(str(p.relative_to(d)) for p in d.rglob("*") if p.is_file()) if d.exists() else []


def parse_transcript(path: Path) -> dict:
    steps, pending, thinking, texts, times = [], {}, [], [], []
    for line in path.read_text(errors="replace").splitlines():
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue
        if e.get("timestamp"):
            times.append(e["timestamp"])
        content = (e.get("message") or {}).get("content")
        if not isinstance(content, list):
            continue
        for b in content:
            t = b.get("type")
            if t == "thinking":
                thinking.append(b.get("thinking", ""))
            elif t == "text" and e.get("type") == "assistant":
                texts.append(b.get("text", ""))
            elif t == "tool_use":
                inp = b.get("input", {})
                cmd = inp.get("command") or inp.get("file_path") or json.dumps(inp)[:300]
                step = {"i": len(steps), "tool": b["name"], "cmd": cmd, "thinking_before": len(thinking)}
                steps.append(step)
                pending[b["id"]] = step
            elif t == "tool_result":
                s = pending.get(b.get("tool_use_id"))
                if s is None:
                    continue
                c = b.get("content")
                text = c if isinstance(c, str) else "".join(x.get("text", "") for x in c or [] if isinstance(x, dict))
                s["out_chars"] = len(text)
                s["is_error"] = bool(b.get("is_error"))
                s["error_text"] = bool(ERRORS.search(text[:4000]))
                s["spilled"] = "/tool-results/" in text or "Output too large" in text
                s["out_head"] = text[:240]
    return {"steps": steps, "thinking": thinking, "texts": texts, "times": times}


def minutes(times: list[str]) -> float | None:
    if len(times) < 2:
        return None
    f = lambda s: datetime.fromisoformat(s.replace("Z", "+00:00"))  # noqa: E731
    return round((f(times[-1]) - f(times[0])).total_seconds() / 60, 1)


def main() -> None:
    state = json.loads(STATE.read_text())
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for task, s in state.items():
        if s["status"] not in ("done", "judge_running", "agent_running") or not s.get("run_dir"):
            continue
        run_dir = Path(s["run_dir"])
        tpath = s.get("agent_transcript") or find_transcript("LABRUN-" + "SOLVER::" + task)
        if not tpath or not Path(tpath).exists():
            continue
        tr = parse_transcript(Path(tpath))
        bash = [x for x in tr["steps"] if x["tool"] == "Bash"]
        cmds = " \n".join(x["cmd"] for x in bash)
        docs = documents(task)
        bulk = bool(re.search(r"for \w+ in [^;]*documents/\*|find [^|;]*documents|documents/\*\*?", cmds))
        named = [d for d in docs if Path(d).name in cmds]
        outs = sorted(p.name for p in (run_dir / "output").glob("*") if p.is_file()) if (run_dir / "output").exists() else []
        out_bytes = sum(p.stat().st_size for p in (run_dir / "output").glob("*") if p.is_file()) if outs else 0
        last_write = max((x["i"] for x in bash if WRITES_DELIVERABLE.search(x["cmd"])), default=-1)
        readback_after = any(READBACK.search(x["cmd"]) for x in bash if x["i"] > last_write - 1) if last_write >= 0 else False
        row = {
            "task": task, "area": task.split("/")[0],
            "work_type": task.split("/")[-1].split("-")[0] if not task.startswith(("contracts/", "firm-knowledge/", "diligence/")) else task.split("/")[0],
            "status": s["status"],
            "n_criteria": s.get("n_criteria"), "n_passed": s.get("n_passed") if s["status"] == "done" else None,
            "all_pass": s.get("all_pass") if s["status"] == "done" else None,
            "n_docs": len(docs), "docs_named": len(named), "bulk_read": bulk,
            "n_tool_calls": len(tr["steps"]), "n_bash": len(bash),
            "n_reads_host": sum(x["tool"] == "Read" for x in tr["steps"]),
            "n_limited_reads": sum(bool(LIMITERS.search(x["cmd"])) for x in bash),
            "n_errors": sum(x.get("is_error", False) or x.get("error_text", False) for x in bash),
            "n_spilled": sum(x.get("spilled", False) for x in tr["steps"]),
            "doc_chars_seen": sum(x.get("out_chars", 0) for x in bash if not OUTPUT_TOUCH.search(x["cmd"])),
            "thinking_chars": sum(len(t) for t in tr["thinking"]), "n_thinking": len(tr["thinking"]),
            "minutes": minutes(tr["times"]),
            "first_write_step": next((x["i"] for x in bash if WRITES_DELIVERABLE.search(x["cmd"])), None),
            "n_rewrites": sum(bool(WRITES_DELIVERABLE.search(x["cmd"])) for x in bash),
            "readback_after_write": readback_after,
            "outputs": outs, "output_bytes": out_bytes,
            "transcript": tpath,
        }
        rows.append(row)
        digest = {**{k: row[k] for k in ("task", "status", "n_criteria", "n_passed", "outputs", "transcript")},
                  "run_dir": str(run_dir), "documents": docs,
                  "steps": [{k: x.get(k) for k in ("i", "tool", "out_chars", "is_error", "error_text", "spilled", "out_head")}
                            | {"cmd": x["cmd"][:600]} for x in tr["steps"]],
                  "final_message": (tr["texts"][-1] if tr["texts"] else "")[:3000]}
        if s["status"] == "done":
            scores = json.loads((run_dir / "scores.json").read_text())
            digest["failed"] = [c for c in scores["criteria_results"] if c["verdict"] != "pass"]
        (OUT / f"{slug(task)}.json").write_text(json.dumps(digest, indent=1))
    (HERE / "trace_stats.json").write_text(json.dumps(rows, indent=1))
    print(f"{len(rows)} tasks; scored {sum(r['status'] == 'done' for r in rows)}")


if __name__ == "__main__":
    main()
