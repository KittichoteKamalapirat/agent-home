---
name: agent-friendly-audit
description: Audits the current repository for the mistakes coding agents keep making in it, using its git history and past Claude Code and Codex sessions, then proposes a plan to restructure it so agents work well there, and carries the plan out after approval. Runs in poteto-mode with the /correct, /architect and /recall skills. Use when the user asks to audit a repo, find agent pitfalls, make a repo more agent friendly, or run poteto's audit prompt, including a rerun to see what has improved since the last audit.
---

# Agent-friendly audit

Work in poteto-mode for the whole task. In Claude Code, load it through the `use-poteto-mode` skill. In Codex, read `~/.agents/skills/poteto-mode/SKILL.md`.

## The task

Audit this repo. Refactor and rearchitect it so that its architecture is more agent friendly.

1. Use both the /correct and /architect skills to look through past commits and past sessions in Claude Code and Codex for this project. Find the most common pitfalls agents fall into, whether in code quality, performance or bugs.
2. Where it helps, use the /recall skill to find past conversations for context.
3. Make a high-level plan for the user to review, backed by real data: counts, commits and session quotes, not impressions.
4. Answer your own open questions by prototyping instead of deferring them to the user.
5. Once the user approves the plan, ask whether they want the stack playbook or the full autopilot playbook, then execute with the one they pick.

If /correct, /architect or /recall is not installed, say which one is missing and do the same analysis by hand from git history and the session logs.

## Finding the sessions

- Claude Code: `~/.claude/projects/` folders whose name contains the repo's folder name, including its worktrees. Skip `subagents/` transcripts.
- Codex: `~/.codex/sessions/` and `~/.codex/archived_sessions/`. Match on the `cwd` in each file's `session_meta`, case-insensitively. Also follow symlinked project folders. A file's modification time is not proof of activity; use the timestamps of its turns.
- Report how many sessions you scanned per source.

## What to look for

- The user correcting the agent ("no", "wrong", "still broken", "you didn't", "revert") or asking for the same thing more than once.
- The agent saying something was done when it was later shown not to be.
- Build and test failures, and how often each one recurred.
- Files edited over and over.
- Time lost on the environment: Docker, Xcode, simulators, disk space, locks, sessions that died mid-run.
- Actions blocked by permission checks. They often show an agent trying to bypass a gate.

Group findings into mistake classes. A class counts once it has happened twice. For each class, give the count and two or three concrete examples with the session file and a short quote.

## Reruns

If an earlier audit exists (look in the project's agent memory, its docs and past sessions), scope the mining to what happened since that audit. Compare against the earlier classes: which recurred, which stopped, and which are new.

Never print secrets or tokens found in transcripts.
