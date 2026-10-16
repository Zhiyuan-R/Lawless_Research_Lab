# Failure attribution from traces (post-hoc analysis of Harvey LAB session runs)

You are analysing why a Claude-based legal agent failed specific rubric criteria. The runs are
finished and scored; isolation no longer matters, so you may read anything below. Be
evidence-driven and skeptical: every classification needs a concrete trace or document citation.

## Inputs, per task (task id T, slug = T with "/" replaced by "__")
- Digest: `harvey_lab/analysis/traces/<slug>.json` with the ordered tool steps (command, output size,
  error/spill flags, first 240 chars of output), the documents list, `run_dir`, `transcript`, the agent's
  final message, and `failed` = the failed criteria (id, title, judge reasoning).
- Full rubric and assignment: `harvey_lab/vendor/harvey-labs/tasks/<T>/task.json` (instructions, criteria).
- Source documents as text: run `harvey_lab/analysis/doctext.sh <T> /tmp/attr/<slug>` once (fixed: it now passes the file type to the parser), then grep the .txt files.
- The agent's deliverables as the judge saw them: `<run_dir>/judge/bundle.md`; the files are in `<run_dir>/output/`.
- What the agent actually SAW: `python3 harvey_lab/analysis/seen.py <transcript> '<regex>'` lists the tool calls
  whose output contained the regex (add `--cmd` to also search the commands). Use distinctive strings from the
  source (a defined term, a dollar figure, a section number, a date).
All paths are relative to /home/user/Lawless_Research_Lab.

## For each failed criterion, decide
1. Where the needed information lives (document + section/sheet + a short quote), or "general legal knowledge / judgment".
2. Did the agent see it? (seen.py hit -> step index; no hit -> check whether the read that should have shown it was
   truncated with head/sed/[:N], spilled to a file it never opened, skipped, or never issued).
3. Is it in the deliverable? (grep bundle.md: absent / present-but-wrong / present-and-right).
4. Was the judge right? Re-read the criterion literally against the deliverable. If the deliverable actually
   satisfies it, or the criterion contradicts the documents/instructions, say so.

Then assign exactly one `cause`:
- `not_retrieved`   needed content never reached the agent's tool output (say why: truncated read, doc skipped, section never opened)
- `seen_not_used`   content was in the agent's tool output, but the deliverable omits the point
- `misread_or_miscalc` the deliverable addresses it but gets a fact, number, date, party or computation wrong
- `judgment`        facts handled correctly, but the legal conclusion / severity / position / recommendation differs from the expert's
- `instruction_miss` an explicit instruction in the assignment (scope, format, audience, required element) was not followed
- `format_structure` substance there, but missing required structure/format (table, section, tracked changes, filename)
- `rubric_or_judge_issue` the deliverable satisfies the criterion as written, or the criterion is wrong/ambiguous given the documents

and one `capability` (the underlying skill that failed):
`reading_recall` (finding/remembering a stated fact in a long input), `cross_doc_reconciliation` (comparing or
reconciling two+ sources), `quantitative` (arithmetic, dates, deadlines), `legal_knowledge` (doctrine, statutes,
market practice not in the docs), `risk_calibration` (severity, priority, what matters), `exhaustiveness` (enumerating
every instance), `instruction_following`, `drafting_craft` (how a provision/document is written), `verification`
(failing to check its own output), `none` (for rubric_or_judge_issue).

## Also record per task (`process`)
2-5 short, concrete observations of agent behaviour from the step list that plausibly mattered: e.g. read docs with
`| head -n 200` and never saw the rest; converted all docs to text up front; wrote the deliverable at step N of M and
never re-checked against the instructions; rewrote the file K times; errors it hit; time/effort spent.
Mark each as `helpful` or `harmful`.

## Output
Write `harvey_lab/analysis/attribution/<GROUP>.json`:
```json
{"tasks": [{"task": "...", "n_failed": 0,
  "process": [{"obs": "...", "effect": "harmful|helpful"}],
  "failures": [{"id": "C-012", "title": "...", "cause": "...", "capability": "...",
    "source": "doc.docx §4.2: \"short quote\"" , "seen_step": 7, "deliverable": "absent | quote of what it wrote",
    "judge_correct": true, "explanation": "1-3 sentences: what went wrong, mechanically"}]}]}
```
Validate the file parses and has one entry per failed criterion (the digest's `failed` list). Reply with counts per
cause and the 3 most striking examples (one line each).
Do not modify anything outside `harvey_lab/analysis/attribution/` and `/tmp/attr/`.
