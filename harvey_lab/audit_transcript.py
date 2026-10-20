"""Audit a session subagent's transcript for isolation violations.

Violations (run is void): any network/external tool; any read of a file other than
the role's own input (agent: AGENT_BRIEF.md, judge: bundle.md) or files it wrote
itself; any reference to task.json, the tasks/ tree, another run, or (for the agent)
the judging area / (for the judge) the agent's run directory.
Warnings (reported, not voiding): other host activity, e.g. helper scripts written
outside the sandbox or the judge directory.

Writes the verdict to <run_dir>/audit_<role>.json and exits 1 on a violation.

Usage: python3 audit_transcript.py <agent|judge> <transcript.jsonl> <run_dir>
"""

import json
import re
import sys
from pathlib import Path

WEB_TOOLS = {"WebSearch", "WebFetch"}
HERE = Path(__file__).resolve().parent
SBX = str(HERE / "sbx.sh")


def tool_calls(transcript: Path, seen: set):
    """Yield tool calls in order; `seen` accumulates text of earlier tool results, so a
    read of a harness spill file is allowed only if the harness pointed this agent to it."""
    for line in transcript.read_text().splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        content = (event.get("message") or {}).get("content")
        if isinstance(content, list):
            for block in content:
                if block.get("type") == "tool_use":
                    yield block["name"], block.get("input", {})
                elif block.get("type") == "tool_result":
                    seen.add(json.dumps(block.get("content")))


FORBIDDEN_HINT = re.compile(r"task\.json|harvey-labs/tasks")


def expand(cmd: str) -> str:
    """Substitute simple VAR=value assignments so $VAR paths can be checked."""
    env = dict(re.findall(r"\b([A-Z_][A-Z0-9_]*)=([^\s;&|]+)", cmd))
    for k, v in sorted(env.items(), key=lambda kv: -len(kv[0])):
        cmd = cmd.replace("${" + k + "}", v).replace("$" + k, v)
    return cmd


def audit(role: str, transcript: Path, run_dir: Path) -> dict:
    """Violations: anything that could reach the rubric, another run, or the network.
    Warnings: other host activity (helper files written outside the sandbox / judge dir)."""
    violations, warnings, counts = [], [], {}
    results_root = next(p for p in run_dir.parents if p.name == "results")  # task ids nest 2-4 levels
    tasks_root = results_root.parent / "tasks"
    judge_root = Path("/tmp/lab-judging")
    if role == "agent":
        home = run_dir
        allowed_reads = {str(run_dir / "AGENT_BRIEF.md")}
    else:
        home = Path(json.loads((run_dir / "judge" / "location.json").read_text())["judge_dir"])
        allowed_reads = {str(home / "bundle.md"), str(home / "responses.json")}
    written: set[str] = set()

    def check_path(path: str, how: str):
        p = path.rstrip("/.,:")
        if p.startswith(str(tasks_root)):
            violations.append(f"{how}: rubric tree {p}")
        elif p.startswith(str(results_root)) and not p.startswith(str(run_dir)):
            violations.append(f"{how}: another run {p}")
        elif role == "agent" and p.startswith(str(judge_root)):
            violations.append(f"{how}: judging area {p}")
        elif role == "judge" and p.startswith(str(run_dir)) and not p.startswith(str(home)):
            violations.append(f"{how}: agent run dir {p}")
        elif role == "judge" and p.startswith(str(judge_root)) and not p.startswith(str(home)):
            violations.append(f"{how}: another judge dir {p}")

    seen: set[str] = set()
    for name, args in tool_calls(transcript, seen):
        counts[name] = counts.get(name, 0) + 1
        if name in WEB_TOOLS or name.startswith("mcp__"):
            violations.append(f"{name}: network/external tool used")
            continue
        if name == "SubagentHandback":
            continue
        if FORBIDDEN_HINT.search(json.dumps(args)):
            violations.append(f"{name} references rubric location: {json.dumps(args)[:160]}")
        if name in ("Read", "Grep", "Glob"):
            target = args.get("file_path") or args.get("path") or args.get("pattern", "")
            check_path(target, name)
            # Harness-owned output files (oversized tool output, background-command
            # logs) are fine when the harness handed this same agent that exact path.
            harness_file = (("/tool-results/" in target or ("/tmp/claude-0/" in target and "/tasks/b" in target))
                            and any(target in t for t in seen))
            # The judge's directory holds only its bundle, its verdicts and its own scratch files.
            own_judge_file = role == "judge" and target.startswith(str(home) + "/")
            if target not in allowed_reads and target not in written and not harness_file and not own_judge_file:
                violations.append(f"{name} outside allowed files: {target}")
        elif name in ("Write", "Edit", "NotebookEdit"):
            target = args.get("file_path", "")
            check_path(target, name)
            written.add(target)
            if not target.startswith(str(home)):
                warnings.append(f"{name} on host outside {home.name}: {target}")
        elif name == "Bash":
            cmd = expand(args.get("command", ""))
            for path in set(re.findall(r"(/(?:home|tmp|root|etc|usr|var|opt)[^\s'\";|&>)]*)", cmd)):
                check_path(path, "Bash")
            if role == "agent" and SBX not in cmd:
                warnings.append(f"host Bash without sbx.sh: {cmd[:120]}")
        elif name not in ("TodoWrite", "TaskCreate", "TaskUpdate", "TaskList", "StructuredOutput"):
            warnings.append(f"unexpected tool: {name}")

    result = {"role": role, "clean": not violations, "violations": violations,
              "warnings": warnings, "tool_counts": counts}
    (run_dir / f"audit_{role}.json").write_text(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    role, transcript, run_dir = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
    r = audit(role, transcript, run_dir)
    print(json.dumps({k: r[k] for k in ("role", "clean", "tool_counts")}),
          *(["VIOLATIONS:"] + r["violations"] if r["violations"] else []),
          *(["warnings:"] + r["warnings"][:5] if r["warnings"] else []), sep="\n")
    sys.exit(0 if r["clean"] else 1)
