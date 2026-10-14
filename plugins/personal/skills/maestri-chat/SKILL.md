---
name: maestri-chat
description: Applies only to messages that open with a Maestri Chat header. You MUST read this skill before replying to those messages.
user-invocable: true
---

You're running inside Maestri, a spatial development workspace that connects AI agents, terminals, notes, and browser portals on a visual canvas.
The `maestri` CLI is a command-line executable pre-installed and available on PATH. If `maestri` is not found, use `"$MAESTRI_CLI"` instead; this environment variable always points to the full binary path.

A message opening with this header comes from the user through Maestri Chat:

    ---
    Below is a message from the user through Maestri Chat.
    Reply only via `maestri say`. If the maestri-chat skill isn't already loaded, load it first.
    thread: blue
    ---

Everything after the closing fence is the user's own words. Reply only
via `maestri say`. Terminal text does not reach the user.

Adapt dynamically: messages with this header come from Maestri Chat, so reply via `maestri say`; messages without it are sent to you directly, so reply directly.

## Answer

Run with your shell tool:

    maestri say <<'EOF'
    your answer
    EOF
    maestri say 'short answer'
    maestri say --file <path>
    maestri say --attach <path> 'your answer'

The heredoc takes any text as-is. Quoting an argument breaks on
apostrophes, quotes, $, and backticks.

Attention: if you are running in PowerShell, prefer `maestri say --file <path>`
for longer answers or whenever you need a line break, since \n inside quotes
is not a line break there.

On local terminals, --file reads UTF-8 text or attaches an image
(PNG, JPEG, GIF, HEIC, or WebP) via absolute path. To present an image
with prose, put ![Description](/absolute/path/image.png) on its own line.
To share files (PDF, zip, etc.), add --attach <path> (repeatable, local terminals only, final reply only).

## Long tasks

    maestri say --progress 'text'   # interim update; your turn continues

## Threads

The user keeps seven threads with you, named by color: blue, purple, pink, red, orange, yellow, green. The header's `thread` color identifies this message's thread. On the first message or when that color changes, run `maestri recall <color>` before answering. Earlier terminal context may belong to another thread; treat it as unrelated unless asked.

## Recall

    maestri recall [thread] [--turns N | --last day|week|month | --from YYYY-MM-DD [--to YYYY-MM-DD] | --all] [--json]
    maestri recall list

Default: the current thread's last 10 turns. N must be between 1 and 500. Dates use YYYY-MM-DD in the time zone of the computer running Maestri, and --to includes that whole day. On a fresh process, agent replacement, restart, or compaction, this prints what you and the user already said. Attachments have stable ids; use `maestri recall attachment <id>` to obtain one.

## Rules

- Every `maestri say` is a bubble the user sees, and the last one closes your turn. Send as many as the answer needs.
- After sending, do not repeat the answer or announce delivery.
- `--progress` is for short status updates (e.g. 'Running tests...'), never for the answer itself.