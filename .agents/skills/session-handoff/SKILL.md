---
name: session-handoff
description: Use this skill at the end of a coding session, when usage limits are close, when the user says "wrap up", "save progress", "switching tools", "handoff", or before any long break in work. Also use at the START of a session to check for existing handoff notes before doing anything else.
---

# Session Handoff

This project is worked on across two tools (Claude Code and Antigravity) that may run different models depending on usage limits. Continuity depends on this skill, not on any single tool's memory.

## At the start of a session

1. Read `AGENTS.md` for project rules and current state.
2. Read the top entry of `PROGRESS.md` for what happened last session and what's next.
3. If `PROGRESS.md` mentions unfinished work, confirm with the user before assuming it's still relevant (things may have changed).
4. If a `tickets/` directory exists, check `tickets/README.md` (regenerate it first via `tickets/_generate_index.sh` if it looks stale) for tickets in in-progress/blocked/in-review status assigned to a role relevant to this session; surface these before starting new work.

## At the end of a session (or when asked to hand off)

1. Prepend a new entry to `PROGRESS.md` using the template format already in the file:
   - What was done
   - What's next
   - Anything non-obvious the next session needs to know
   - Files touched
2. Update the "Current state" section of `AGENTS.md` if the project's overall status changed (not just this session's details — that's what PROGRESS.md is for).
3. If a ticket was advanced this session, update its `status` field in `tickets/<id>-*.md` and re-run `tickets/_generate_index.sh` before the PROGRESS.md/commit step below.
4. If there are uncommitted changes, suggest a commit with a clear message before ending the session — git history is a second continuity layer alongside PROGRESS.md.
5. Keep the handoff note factual and short. This is for an agent to read, not a changelog for humans — skip pleasantries.
