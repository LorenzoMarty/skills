---
name: token-trace
description: Show where Claude Code tokens went (read/think/write per task, per subagent, per tool count) from real API usage in the session transcripts. Use for /token-trace, "quanto de token gastei", "qual tarefa foi mais cara".
disable-model-invocation: true
allowed-tools: Bash(python *)
argument-hint: "[session|today|expensive|project]"
---

Run this and print the output verbatim in a code block, with no extra commentary:

```
python "${CLAUDE_SKILL_DIR}/token_trace.py" $ARGUMENTS
```

- no argument: last task of the current session + session total
- `session [id]`: session box, tokens per task, per-agent tree
- `today`: everything since local midnight
- `expensive [N]`: top N tasks across all history
- `project`: tokens per project dir

Tags: MEASURED = field returned by the API; DERIVED = arithmetic on measured fields.
Per-tool token attribution is UNKNOWN (not exposed by Claude Code); only tool call counts are shown.
