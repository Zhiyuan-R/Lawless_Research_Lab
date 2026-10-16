"""Was a fact visible to the solver? Lists tool calls whose OUTPUT matches a regex.

Usage: python3 harvey_lab/analysis/seen.py <transcript.jsonl> '<regex>' [--cmd]
  --cmd   also search the commands the agent ran (e.g. which file it opened)
Prints: step index, tool, matched snippet, and the command that produced it.
"""
import json, re, sys
path, pat = sys.argv[1], re.compile(sys.argv[2], re.I)
search_cmd = "--cmd" in sys.argv
steps, pending = [], {}
for line in open(path, errors="replace"):
    try:
        e = json.loads(line)
    except json.JSONDecodeError:
        continue
    content = (e.get("message") or {}).get("content")
    if not isinstance(content, list):
        continue
    for b in content:
        if b.get("type") == "tool_use":
            inp = b.get("input", {})
            s = {"i": len(steps), "tool": b["name"], "cmd": inp.get("command") or inp.get("file_path") or json.dumps(inp)}
            steps.append(s); pending[b["id"]] = s
        elif b.get("type") == "tool_result" and b.get("tool_use_id") in pending:
            c = b.get("content")
            pending[b["tool_use_id"]]["out"] = c if isinstance(c, str) else "".join(x.get("text", "") for x in c or [] if isinstance(x, dict))
hits = 0
for s in steps:
    for where in (["out", "cmd"] if search_cmd else ["out"]):
        m = pat.search(s.get(where, "") or "")
        if m:
            hits += 1
            t = s[where]; a = max(0, m.start() - 120)
            print(f"[step {s['i']} {s['tool']} in {where}] ...{t[a:m.end()+120]!r}...\n    cmd: {s['cmd'][:200]!r}")
print(f"{hits} hit(s) in {len(steps)} steps")
