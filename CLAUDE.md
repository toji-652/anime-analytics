# CLAUDE.md

This project's rules, stack, conventions, and current state live in **AGENTS.md** at the project root — that file is the shared source of truth read by both Claude Code and Antigravity.

**Read AGENTS.md first, at the start of every session, before doing anything else.**

## Claude-Code-specific notes

(Anything that only applies to Claude Code — not Antigravity — goes here. e.g. allowed-tools permissions, hook behavior, MCP servers you use in this project.)

## Session handoff

Before ending a session or when usage limits are close, update `PROGRESS.md` with:
- What was just done
- What's next
- Anything the next agent (whether that's Claude again, or Antigravity) needs to know that isn't obvious from git history

Commit progress notes along with code changes so they survive tool switches.
