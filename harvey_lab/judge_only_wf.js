export const meta = {
  name: 'lab-judge-backlog',
  description: 'Judge already-solved Harvey LAB runs: independent judge, then official scoring and audits',
  phases: [{ title: 'Judge' }, { title: 'Score' }],
}

// Judge-only pass over runs whose solver already finished; no new tasks are solved.
const H = '/home/user/Lawless_Research_Lab/harvey_lab'
const tasks = args.tasks

function judgePrompt(task) {
  return `LABRUN-JUDGE::${task}

You are the LLM judge for one Harvey Legal Agent Benchmark (LAB) run. You did not produce the work; grade it strictly and impartially.

Step 1. Run exactly this host command (it closes the agent's sandbox and builds your grading bundle):
  python3 ${H}/wf_step.py post-agent '${task}'
It prints one JSON line. If it contains "error", reply with exactly "SKIPPED: <that JSON>" and stop.
Otherwise it gives "bundle" (path to bundle.md) and "responses" (where to write verdicts). Your working directory is the folder containing bundle.md.

Step 2. Read ALL of bundle.md with the Read tool in chunks (offset/limit): the official per-criterion prompt, the task, the agent output blocks (<<<OUT-xxxx>>> ... <<<END OUT-xxxx>>>), and every criterion. Each criterion names the output block it is judged against. Redline output may show tracked insertions/deletions inline; treat them as the agent's proposed changes.

For each criterion apply the official prompt independently: PASS only if that output block satisfies the criterion as written, including any specific numbers, parties, documents or recommendations it requires; otherwise FAIL. No credit for effort or near-misses; one verdict must not influence another. Before passing, confirm the required facts are actually present (e.g. Grep the bundle).

Isolation rules (checked automatically from your tool log; a violation voids the grading): besides the Step 1 command, read and search only bundle.md; create files only inside the bundle's folder; do not access any other path (no harvey_lab results or tasks, no other judging folders, no scratch directories); no web or MCP tools; do not spawn agents.

Step 3. Write the "responses" file: a JSON object mapping every criterion id in the bundle to {"reasoning": "<1-3 sentences>", "verdict": "pass" | "fail"}. Validate it parses and contains every id.

Reply with the pass count and the failed ids with one-line reasons.`
}

const SCORE = { type: 'object', properties: { output: { type: 'string' } }, required: ['output'] }

async function judgeOne(task) {
  const judged = await agent(judgePrompt(task), { label: `judge ${task}`, phase: 'Judge' })
  if (typeof judged === 'string' && judged.startsWith('SKIPPED')) { log(`skipped ${task}: ${judged}`); return { task, skipped: judged } }
  const r = await agent(`Run exactly this command and return its stdout verbatim in "output":\n  python3 ${H}/wf_step.py post-judge '${task}'`,
    { label: `score ${task}`, phase: 'Score', schema: SCORE, model: 'haiku', effort: 'low' })
  log(`${task}: ${r ? r.output : 'score step failed'}`)
  return { task, score: r ? r.output : null }
}

const results = []
let next = 0
await parallel([0, 1].map(() => async () => {
  while (next < tasks.length) results.push(await judgeOne(tasks[next++]))
}))
return { n: results.length, scored: results.filter(r => r.score).length }
