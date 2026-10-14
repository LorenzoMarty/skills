#!/usr/bin/env python3
"""token-trace: per-task / per-agent token breakdown from Claude Code transcripts.

Source: ~/.claude/projects/<proj>/<session>.jsonl (+ <session>/subagents/agent-*.jsonl).
Store:  SQLite (~/.claude/token-trace/trace.db, override with TOKEN_TRACE_DB).
Usage:  token_trace.py [session|today|expensive|project|ingest] [args]
"""
import glob, json, os, re, sqlite3, sys
from datetime import datetime, timezone

HOME = os.path.expanduser("~")
PROJECTS = os.environ.get("TOKEN_TRACE_PROJECTS", os.path.join(HOME, ".claude", "projects"))
DB = os.environ.get("TOKEN_TRACE_DB", os.path.join(HOME, ".claude", "token-trace", "trace.db"))

SCHEMA = """
CREATE TABLE IF NOT EXISTS calls(   -- one row per API message (deduped by msg_id)
  msg_id TEXT PRIMARY KEY, session_id TEXT, agent_id TEXT, task_id TEXT, project TEXT,
  ts TEXT, model TEXT, input INT, cache_read INT, cache_create INT, output INT,
  thinking INT);                     -- thinking NULL = API gave no split (UNKNOWN)
CREATE TABLE IF NOT EXISTS tasks(task_id TEXT PRIMARY KEY, session_id TEXT, title TEXT, start_ts TEXT);
CREATE TABLE IF NOT EXISTS agents(session_id TEXT, agent_id TEXT, parent_agent TEXT, type TEXT, descr TEXT,
  PRIMARY KEY(session_id, agent_id));
CREATE TABLE IF NOT EXISTS tools(tool_use_id TEXT PRIMARY KEY, msg_id TEXT, session_id TEXT, task_id TEXT, name TEXT);
CREATE INDEX IF NOT EXISTS calls_task ON calls(task_id);
CREATE INDEX IF NOT EXISTS calls_ts ON calls(ts);
"""


# ---------- parsing ----------
def _text(msg):
    c = msg.get("content")
    if isinstance(c, str):
        return c
    if isinstance(c, list):
        return " ".join(b.get("text", "") for b in c if isinstance(b, dict) and b.get("type") == "text")
    return ""


def _title(text):
    """Task label from a real user prompt; None if it is not one."""
    t = re.sub(r"<(system-reminder|local-command-\w+)>.*?</\1>", "", text, flags=re.S)
    t = re.sub(r"</?pasted_content[^>]*>", "", t).strip()
    if t.startswith("<command-name>"):  # slash command
        name = t.split("</command-name>")[0].replace("<command-name>", "").strip()
        args = t.split("<command-args>")[-1].split("</command-args>")[0].strip() if "<command-args>" in t else ""
        t = f"{name} {args}".strip()
    if not t or t.startswith("<"):
        return None
    return " ".join(t.split())[:80]


def parse_file(path, session_id, agent_id=""):
    """Returns (calls, tasks, tools). calls merged per msg_id (max of each usage field)."""
    calls, tasks, tools = {}, {}, {}
    cur = f"{session_id}/-"
    for line in open(path, encoding="utf-8", errors="replace"):
        try:
            d = json.loads(line)
        except ValueError:
            continue
        m = d.get("message")
        if not isinstance(m, dict):
            continue
        if d.get("type") == "user" and not agent_id and not d.get("isMeta") and not d.get("toolUseResult"):
            title = _title(_text(m))
            if title:
                cur = d.get("promptId") or d.get("uuid")
                tasks[cur] = (session_id, title, d.get("timestamp"))
        elif d.get("type") == "assistant" and m.get("usage") and m.get("id"):
            u = m["usage"]
            th = (u.get("output_tokens_details") or {}).get("thinking_tokens")
            new = dict(session_id=session_id, agent_id=agent_id, task_id=cur, project=d.get("cwd"),
                       ts=d.get("timestamp"), model=m.get("model"),
                       input=u.get("input_tokens", 0), cache_read=u.get("cache_read_input_tokens", 0),
                       cache_create=u.get("cache_creation_input_tokens", 0),
                       output=u.get("output_tokens", 0), thinking=th)
            old = calls.get(m["id"])
            if old:  # same API message repeated per content block: keep the max, never sum
                for k in ("input", "cache_read", "cache_create", "output"):
                    new[k] = max(new[k], old[k])
                new["thinking"] = max(x for x in (th, old["thinking"], -1) if x is not None)
                new["thinking"] = None if new["thinking"] < 0 else new["thinking"]
                new["ts"] = old["ts"]
            calls[m["id"]] = new
            for b in m.get("content") or []:
                if isinstance(b, dict) and b.get("type") == "tool_use":
                    tools[b["id"]] = (m["id"], session_id, cur, b.get("name"))
    return calls, tasks, tools


def ingest_session(con, transcript):
    sid = os.path.basename(transcript)[:-6]
    calls, tasks, tools = parse_file(transcript, sid)
    owner = {t: (tl[2], "") for t, tl in tools.items()}  # tool_use_id -> (task_id, agent_id)
    agents = {}
    sub = glob.glob(os.path.join(transcript[:-6], "subagents", "agent-*.jsonl"))
    metas = {}
    for p in sub:
        aid = os.path.basename(p)[6:-6]
        try:
            metas[aid] = json.load(open(p[:-6] + ".meta.json", encoding="utf-8"))
        except (OSError, ValueError):
            metas[aid] = {}
    parsed = {os.path.basename(p)[6:-6]: parse_file(p, sid, os.path.basename(p)[6:-6]) for p in sub}
    for aid, (_, _, t) in parsed.items():
        for tid in t:
            owner.setdefault(tid, (f"{sid}/-", aid))
    for _ in range(5):  # resolve nested agents (agent spawned by agent) to the root task
        for aid, meta in metas.items():
            task, parent = owner.get(meta.get("toolUseId"), (f"{sid}/-", ""))
            agents[aid] = (parent, task)
            for tid in parsed[aid][2]:
                owner[tid] = (task, aid)
    for aid, (c, _, t) in parsed.items():
        task = agents[aid][1] if aid in agents else f"{sid}/-"
        for r in c.values():
            r["task_id"] = task
        calls.update(c)
        tools.update({k: (v[0], v[1], task, v[3]) for k, v in t.items()})
    with con:
        con.executemany("INSERT OR REPLACE INTO calls VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
                        [(k, r["session_id"], r["agent_id"], r["task_id"], r["project"], r["ts"], r["model"],
                          r["input"], r["cache_read"], r["cache_create"], r["output"], r["thinking"])
                         for k, r in calls.items()])
        con.executemany("INSERT OR REPLACE INTO tasks VALUES(?,?,?,?)", [(k, *v) for k, v in tasks.items()])
        if any(r["task_id"] == f"{sid}/-" for r in calls.values()):
            con.execute("INSERT OR IGNORE INTO tasks VALUES(?,?,?,?)",
                        (f"{sid}/-", sid, "(no prompt / unlinked agent)", None))
        con.executemany("INSERT OR REPLACE INTO agents VALUES(?,?,?,?,?)",
                        [(sid, a, agents[a][0], metas[a].get("agentType"), metas[a].get("description"))
                         for a in agents])
        con.executemany("INSERT OR REPLACE INTO tools VALUES(?,?,?,?,?)", [(k, *v) for k, v in tools.items()])
    return sid


def connect():
    os.makedirs(os.path.dirname(DB), exist_ok=True)
    con = sqlite3.connect(DB)
    con.executescript(SCHEMA)
    return con


def current_transcript():
    sid = os.environ.get("CLAUDE_CODE_SESSION_ID")
    if sid:
        hit = glob.glob(os.path.join(PROJECTS, "*", sid + ".jsonl"))
        if hit:
            return hit[0]
    files = glob.glob(os.path.join(PROJECTS, "*", "*.jsonl"))  # fallback: newest transcript
    return max(files, key=os.path.getmtime) if files else None


# ---------- aggregation / rendering ----------
def fmt(n):
    return f"{n/1e6:.3f}M" if n >= 1e6 else f"{n/1e3:.1f}k" if n >= 1e3 else str(int(n))


def split(rows):
    """rows: (input, cache_read, cache_create, output, thinking). read/think/write/unknown/total."""
    read = think = write = unk = 0
    for i, cr, cc, o, t in rows:
        read += i + cr + cc
        if t is None:
            unk += o
        else:
            think += t
            write += o - t
    return dict(read=read, think=think, write=write, unk=unk, total=read + think + write + unk)


def agg(con, where, args):
    rows = con.execute(f"SELECT input,cache_read,cache_create,output,thinking FROM calls WHERE {where}", args)
    return split(rows.fetchall())


def box(title, s, tools, dur, extra=()):
    w = 54
    lines = [f"Task: {title}"[:w - 1], ""]
    for k, tag in (("read", "MEASURED"), ("think", "MEASURED"), ("write", "DERIVED")):
        lines.append(f"{k:<8}{fmt(s[k]):>10}  {tag}")
    if s["unk"]:
        lines.append(f"{'no-split':<8}{fmt(s['unk']):>10}  UNKNOWN")
    lines += ["─" * (w - 1),f"{'total':<8}{fmt(s['total']):>10}  DERIVED", ""]
    lines += [f"{n} tools: {c}" for n, c in tools[:6]]
    if dur is not None:
        lines.append(f"Duration: {int(dur//60)}m {int(dur%60):02d}s  (wall clock)")
    lines += list(extra)
    out = ["╭─ Token Trace " + "─" * (w - 14) + "╮"]
    out += [f"│ {l:<{w-1}}│" for l in lines]
    return "\n".join(out + ["╰" + "─" * w + "╯"])


def _ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()


def task_info(con, task_id):
    title, start = con.execute("SELECT title,start_ts FROM tasks WHERE task_id=?", (task_id,)).fetchone()
    tools = con.execute("SELECT name,COUNT(*) c FROM tools WHERE task_id=? GROUP BY name ORDER BY c DESC",
                        (task_id,)).fetchall()
    end = con.execute("SELECT MAX(ts) FROM calls WHERE task_id=?", (task_id,)).fetchone()[0]
    dur = _ts(end) - _ts(start) if start and end else None
    return title, tools, dur


def task_rows(con, where="1", args=()):
    q = f"""SELECT t.task_id, t.title, t.start_ts, SUM(input+cache_read+cache_create+output) tot
            FROM tasks t JOIN calls c USING(task_id) WHERE {where} GROUP BY t.task_id ORDER BY tot DESC"""
    return con.execute(q, args).fetchall()


def table(rows, label="Task"):
    out = [f"{label:<44}{'Tokens':>10}"]
    out += [f"{r[0][:42]:<44}{fmt(r[1]):>10}" for r in rows]
    return "\n".join(out)


def agent_tree(con, sid):
    ag = {a: (p, t or "agent", d or "") for a, p, t, d in
          con.execute("SELECT agent_id,parent_agent,type,descr FROM agents WHERE session_id=?", (sid,))}
    tot = {a: s for a, s in con.execute(
        "SELECT agent_id,SUM(input+cache_read+cache_create+output) FROM calls WHERE session_id=? GROUP BY agent_id",
        (sid,))}
    # per-node numbers are the agent's own calls: nothing is counted in two nodes
    def node(a, depth):
        name = "Main session" if a == "" else f"{ag[a][1]}: {ag[a][2][:30]}"
        out = [f"{'  '*depth}{name:<46}{fmt(tot.get(a, 0)):>10}"]
        for k, (p, _, _) in sorted(ag.items()):
            if p == a and k != a:
                out += node(k, depth + 1)
        return out
    return "\n".join(node("", 0) + [f"{'─'*56}", f"{'Total':<46}{fmt(sum(tot.values())):>10}"])


def cmd_default(con):
    sid = os.environ.get("CLAUDE_CODE_SESSION_ID") or con.execute(
        "SELECT session_id FROM calls ORDER BY ts DESC LIMIT 1").fetchone()[0]
    r = con.execute("SELECT task_id FROM tasks WHERE session_id=? AND start_ts IS NOT NULL "
                    "AND EXISTS(SELECT 1 FROM calls WHERE calls.task_id=tasks.task_id) "
                    "ORDER BY start_ts DESC LIMIT 1", (sid,)).fetchone()
    if not r:
        return "No tasks recorded for this session."
    title, tools, dur = task_info(con, r[0])
    s = agg(con, "task_id=?", (r[0],))
    ss = agg(con, "session_id=?", (sid,))
    return box(title, s, tools, dur, ["", f"Session total: {fmt(ss['total'])}"])


def cmd_session(con, sid):
    ss = agg(con, "session_id=?", (sid,))
    tools = con.execute("SELECT name,COUNT(*) c FROM tools WHERE session_id=? GROUP BY name ORDER BY c DESC",
                        (sid,)).fetchall()
    return "\n\n".join([box(f"session {sid[:8]}", ss, tools, None),
                        table([(r[1], r[3]) for r in task_rows(con, "t.session_id=?", (sid,))]),
                        agent_tree(con, sid)])


def cmd_today(con):
    start = datetime.now().astimezone().replace(hour=0, minute=0, second=0, microsecond=0)
    iso = start.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
    s = agg(con, "ts>=?", (iso,))
    rows = task_rows(con, "t.start_ts>=?", (iso,))
    return box("today", s, [], None) + "\n\n" + table([(r[1], r[3]) for r in rows[:15]])


def cmd_expensive(con, n=10):
    return table([(r[1], r[3]) for r in task_rows(con)[:n]])


def cmd_project(con):
    rows = con.execute("SELECT project, SUM(input+cache_read+cache_create+output) t FROM calls "
                       "GROUP BY project ORDER BY t DESC").fetchall()
    return table([(os.path.basename(p or "?"), t) for p, t in rows], "Project")


def main(argv):
    sys.stdout.reconfigure(encoding="utf-8")
    cmd = argv[0] if argv else ""
    con = connect()
    if cmd == "ingest":
        if "--all" in argv:
            files = [f for f in glob.glob(os.path.join(PROJECTS, "*", "*.jsonl"))]
        else:  # hook mode: JSON on stdin with transcript_path
            try:
                files = [json.load(sys.stdin)["transcript_path"]]
            except (ValueError, KeyError):
                files = []
        for f in files:
            ingest_session(con, f)
        print(f"ingested {len(files)} session(s)")
        return
    cur = current_transcript()
    if cur:  # keep the current session fresh on every query
        ingest_session(con, cur)
    if cmd == "session":
        sid = argv[1] if len(argv) > 1 else os.path.basename(cur)[:-6]
        print(cmd_session(con, sid))
    elif cmd == "today":
        print(cmd_today(con))
    elif cmd == "expensive":
        print(cmd_expensive(con, int(argv[1]) if len(argv) > 1 else 10))
    elif cmd == "project":
        print(cmd_project(con))
    else:
        print(cmd_default(con))


if __name__ == "__main__":
    main(sys.argv[1:])
