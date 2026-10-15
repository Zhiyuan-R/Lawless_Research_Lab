"""Run Harvey LAB tasks with Claude Code session agents instead of API keys.

The official harness calls a provider API for the agent and for the judges.
This runner keeps everything else official and swaps those two roles for
Claude Code subagents working through files:

  prepare-agent  Start the official podman sandbox (network off, documents
                 mounted read-only, no task.json inside) and write the brief:
                 LAB system prompt + skill manuals + task instructions.
  finish-agent   Stop the sandbox; write config.json / metrics.json, with
                 document coverage measured from the sbx.sh command log.
  prepare-judge  Run the official score_rubric() with a recording judge, so
                 each criterion gets exactly the deliverable text the official
                 grader would send. Writes judge/bundle.md for a judge agent.
  finalize       Run the official evaluate_run() with a judge that reads the
                 judge agent's judge/responses.json, then build report.html.

Scores are written in the official scores.json format and tagged with the
session judge label, so they are NOT comparable to the standard
Sonnet 4.6 + GPT-5.5 dual-judge results.
"""

import argparse
import hashlib
import json
import shutil
import sys
from datetime import UTC, datetime
from pathlib import Path

from lab_core import paths
from lab_core.evaluation import report as lab_report
from lab_core.evaluation.judge import PROMPTS_DIR, Judge
from lab_core.evaluation.run_eval import evaluate_run
from lab_core.evaluation.scoring import score_rubric
from lab_core.harness import run as harness_run
from lab_core.sandbox.sandbox import Sandbox

HERE = Path(__file__).resolve().parent
SBX = HERE / "sbx.sh"
DEFAULT_AGENT_LABEL = "claude-code-session"
DEFAULT_JUDGE_LABEL = "claude-code-session-judge"


def _run_dir(run_id: str) -> Path:
    return paths.results_dir() / run_id


def _criteria(task: str) -> list[dict]:
    return harness_run.load_task(task)["config"]["criteria"]


# ── Agent phase ───────────────────────────────────────────────────────

def prepare_agent(task_id: str, label: str) -> None:
    task = harness_run.load_task(task_id)
    ts = datetime.now().astimezone().strftime("%Y%m%d-%H%M%S")
    run_id = f"{task_id}/{label}/{ts}"
    run_dir = _run_dir(run_id)
    output_dir, workspace_dir = run_dir / "output", run_dir / "workspace"
    output_dir.mkdir(parents=True)
    workspace_dir.mkdir(parents=True)

    skills = harness_run.DEFAULT_SKILLS
    harness_run.setup_skill_scripts(skills, workspace_dir)
    system_prompt = harness_run.build_system_preamble(enable_finish=False) + harness_run.load_skills(skills)

    sandbox = Sandbox(documents_dir=Path(task["docs_dir"]), output_dir=output_dir, workspace_dir=workspace_dir)
    sandbox.start()
    # The atexit backstop would tear the container down when this process
    # exits; the agent needs it alive until finish-agent.
    sandbox._started = False
    container = sandbox.container_name
    sandbox.container_name = None

    session = {
        "run_id": run_id,
        "task": task_id,
        "container": container,
        "sandbox_image": sandbox.image,
        "started_at": datetime.now(UTC).isoformat(),
    }
    (run_dir / "session.json").write_text(json.dumps(session, indent=2))

    brief = f"""# Harvey LAB agent brief

You are the agent under evaluation in the Harvey Legal Agent Benchmark.

## How to act

Your only workspace is a sandbox container. Run every command through:

    {SBX} {run_dir} '<bash command>'

It runs the command inside the container (cwd /workspace, no network) and logs it.
Do not touch any host path other than this brief — in particular never read task.json,
anything under tasks/ or results/ on the host, or other runs: the rubric lives there
and reading it disqualifies the run. Read documents with `parse-doc <file>` or the
Python libraries inside the container. Write deliverables to /workspace/output/.
There is no `finish` tool: when every deliverable is written, stop and reply with a
short summary and the list of files you produced.

Tool mapping from the system prompt below: `bash` = sbx.sh; `read` = `parse-doc`
(or `cat`) inside the sandbox; `write`/`edit` = write files under /workspace/output
from a sbx.sh command (heredoc or a Python script); `glob`/`grep` = `find`/`rg`.

---

# System prompt (official LAB harness)

{system_prompt}

---

# Assignment

{task["instructions"]}
"""
    (run_dir / "AGENT_BRIEF.md").write_text(brief)
    print(json.dumps({"run_id": run_id, "run_dir": str(run_dir), "brief": str(run_dir / "AGENT_BRIEF.md"),
                      "container": container}, indent=2))


def finish_agent(run_id: str, model: str) -> None:
    run_dir = _run_dir(run_id)
    session = json.loads((run_dir / "session.json").read_text())
    task = harness_run.load_task(session["task"])
    sandbox = Sandbox(documents_dir=Path(task["docs_dir"]), output_dir=run_dir / "output",
                      workspace_dir=run_dir / "workspace")
    sandbox.container_name = session["container"]
    sandbox.stop()

    log_path = run_dir / "commands.jsonl"
    commands = [json.loads(line) for line in log_path.read_text().splitlines()] if log_path.exists() else []
    command_text = "\n".join(c["command"] for c in commands)
    docs_dir = Path(task["docs_dir"])
    documents = sorted(str(p.relative_to(docs_dir)) for p in docs_dir.rglob("*") if p.is_file())
    # A document counts as read when a sandbox command named it, or read the
    # whole directory with a glob/loop over documents/.
    bulk = any(tok in command_text for tok in ("documents/*", "documents/**", "os.listdir", "iterdir", "glob("))
    read = [d for d in documents if bulk or Path(d).name in command_text]
    started = datetime.fromisoformat(session["started_at"])
    ended = datetime.now(UTC)
    outputs = sorted(str(p.relative_to(run_dir / "output")) for p in (run_dir / "output").rglob("*") if p.is_file())

    config = {
        "model": model, "task": session["task"], "run_id": run_id,
        "harness": "claude-code-session (sbx.sh over the official podman sandbox)",
        "skills": harness_run.DEFAULT_SKILLS, "sandbox_image": session["sandbox_image"],
        "started_at": session["started_at"],
    }
    metrics = {
        "model": model, "task": session["task"], "run_id": run_id,
        "turn_count": len(commands), "input_tokens": 0, "output_tokens": 0, "total_tokens": 0,
        "wall_clock_seconds": round((ended - started).total_seconds(), 1),
        "finished_cleanly": bool(outputs), "finish_reason": "session_agent_stop",
        "finish_summary": None, "completed_at": ended.isoformat(),
        "documents_read": len(read), "documents_read_list": read,
        "total_documents": len(documents),
        "documents_skipped": len(documents) - len(read),
        "documents_skipped_list": [d for d in documents if d not in read],
        "tool_calls": {"bash": len(commands)}, "output_files": outputs,
        "note": "Token counts are not observable from a session agent and are reported as 0.",
    }
    (run_dir / "config.json").write_text(json.dumps(config, indent=2))
    (run_dir / "metrics.json").write_text(json.dumps(metrics, indent=2))
    print(json.dumps({k: metrics[k] for k in ("turn_count", "wall_clock_seconds", "documents_read",
                                              "total_documents", "output_files")}, indent=2))


# ── Judge phase ───────────────────────────────────────────────────────

class _LookupMixin:
    def __init__(self, criteria: list[dict], model: str):
        self.model = model
        self._by_text = {(c["title"], c["match_criteria"]): c["id"] for c in criteria}

    def _criterion_id(self, variables: dict) -> str:
        return self._by_text[(variables["criterion_title"], variables["match_criteria"])]


class RecordingJudge(_LookupMixin):
    """Captures what the official grader would send for each criterion."""

    def __init__(self, criteria, model):
        super().__init__(criteria, model)
        self.records: dict[str, dict] = {}

    def evaluate_from_file(self, prompt_name: str, variables: dict) -> dict:
        self.records[self._criterion_id(variables)] = dict(variables)
        return {"verdict": "fail", "reasoning": "recording only"}


class FileJudge(_LookupMixin):
    """Returns verdicts the judge agent wrote to judge/responses.json."""

    def __init__(self, criteria, model, responses: dict):
        super().__init__(criteria, model)
        self.responses = responses

    def evaluate_from_file(self, prompt_name: str, variables: dict) -> dict:
        cid = self._criterion_id(variables)
        if cid not in self.responses:
            raise KeyError(f"no judge response for {cid}")
        resp = self.responses[cid]
        return Judge._parse_json(resp) if isinstance(resp, str) else resp


def prepare_judge(run_id: str, task_id: str) -> None:
    run_dir = _run_dir(run_id)
    criteria = _criteria(task_id)
    recorder = RecordingJudge(criteria, "recording")
    score_rubric(criteria=criteria, run_dir=run_dir, judge=recorder,
                 task_desc=harness_run.load_task(task_id)["config"]["title"], parallel=1)

    # The same deliverable text is sent with many criteria; list each distinct
    # output once and point criteria at it, to keep the judge's context small.
    outputs: dict[str, str] = {}
    lines = []
    for c in criteria:
        rec = recorder.records[c["id"]]
        key = "OUT-" + hashlib.sha256(rec["agent_output"].encode()).hexdigest()[:8]
        outputs.setdefault(key, rec["agent_output"])
        lines.append(f"### {c['id']}  (Agent's Output: {key})\n**{rec['criterion_title']}**\n\n{rec['match_criteria']}\n")

    template = (PROMPTS_DIR / "rubric_criterion.txt").read_text()
    task_desc = recorder.records[criteria[0]["id"]]["task_description"]
    judge_dir = run_dir / "judge"
    judge_dir.mkdir(exist_ok=True)
    bundle = f"""# Harvey LAB judge bundle — {run_id}

You are the judge. For EACH criterion below, apply the official LAB per-criterion
prompt independently, as if it were the only criterion: the agent output is the
block it points to, the criterion is its title + text. Do not let one criterion's
verdict influence another, and do not reward effort — judge only what the output says.

Write `{judge_dir / 'responses.json'}` as a JSON object mapping every criterion id
to {{"reasoning": "...", "verdict": "pass" | "fail"}}. All {len(criteria)} ids must be present.

## Official per-criterion prompt (for reference)

````
{template}
````

## Task
{task_desc}

## Agent outputs

""" + "\n\n".join(f"<<<{k}>>>\n{v}\n<<<END {k}>>>" for k, v in outputs.items()) + \
        "\n\n## Criteria\n\n" + "\n".join(lines)
    (judge_dir / "bundle.md").write_text(bundle)
    print(json.dumps({"bundle": str(judge_dir / "bundle.md"), "responses": str(judge_dir / "responses.json"),
                      "criteria": len(criteria), "distinct_outputs": len(outputs),
                      "bundle_chars": len(bundle)}, indent=2))


def finalize(run_id: str, task_id: str, judge_label: str) -> None:
    run_dir = _run_dir(run_id)
    responses = json.loads((run_dir / "judge" / "responses.json").read_text())
    judge = FileJudge(_criteria(task_id), judge_label, responses)
    scores = evaluate_run(run_id=run_id, task=task_id, judge=judge, parallel=1)
    report_path = lab_report.generate_report(run_id)
    print(scores["summary"])
    print(f"scores: {run_dir / 'scores.json'}\nreport: {report_path}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("prepare-agent"); p.add_argument("task"); p.add_argument("--label", default=DEFAULT_AGENT_LABEL)
    p = sub.add_parser("finish-agent"); p.add_argument("run_id"); p.add_argument("--model", default=DEFAULT_AGENT_LABEL)
    p = sub.add_parser("prepare-judge"); p.add_argument("run_id"); p.add_argument("task")
    p = sub.add_parser("finalize"); p.add_argument("run_id"); p.add_argument("task")
    p.add_argument("--judge-label", default=DEFAULT_JUDGE_LABEL)
    a = parser.parse_args()
    if a.cmd == "prepare-agent":
        prepare_agent(a.task, a.label)
    elif a.cmd == "finish-agent":
        finish_agent(a.run_id, a.model)
    elif a.cmd == "prepare-judge":
        prepare_judge(a.run_id, a.task)
    else:
        finalize(a.run_id, a.task, a.judge_label)
    return 0


if __name__ == "__main__":
    shutil.which("podman") or sys.exit("podman is required; run harvey_lab/setup.sh")
    sys.exit(main())
