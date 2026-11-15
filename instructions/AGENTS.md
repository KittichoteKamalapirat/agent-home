# Shared working preferences

These apply to every project and to both Claude Code and Codex. A project's own
AGENTS.md or CLAUDE.md takes precedence where they differ.

## Default working style

- Use Poteto Mode for any task that changes code or needs rigor. In Claude Code it
  is the `pstack:poteto-mode` skill; in Codex it is
  `~/.agents/skills/poteto-mode/SKILL.md`. Skip it for quick questions and
  one-line edits.
- Use the `codebase-design` skill when designing or restructuring code.

## Skills

- Shared skills are installed from the agent-home repo
  (github.com/KittichoteKamalapirat/agent-home). To add one everywhere, add it to
  agent-home's `skills.txt`; do not copy shared skills into a project.
- Project-specific skills live in the project's own `.agents/skills`.

## pstack in Codex

This section applies only when running in Codex. Claude Code uses the pstack
plugin, which is already adapted.

When a pstack skill is invoked in Codex, adapt its Cursor-specific runtime
instructions as follows:

- Use the installed skills in `~/.agents/skills`. Resolve supporting skills
  through the available skill catalog.
- Use native collaboration tools for skill-requested subagents. Cursor `Task`,
  `subagent_type`, and `run_in_background` fields describe intent, not callable
  Codex APIs.
- Default all pstack model roles to `inherit-parent`, including each panel entry.
  Omit model and reasoning overrides unless the user explicitly chooses supported
  Codex models. Preserve the requested panel size and disclose when perspectives
  use the same model. Do not pass Cursor, Claude, or Grok model slugs to Codex.
- For `/recall`, use Codex chat listing and reading tools when available, scoped
  to the requested project, topic, and time window. Do not assume Cursor
  transcript paths contain Codex history. If tools are unavailable, discover the
  actual local history location before reading it and report gaps.
- Use native planning and app verification tools in place of Cursor-only APIs.
  Report an unavailable capability instead of claiming it ran.
- Skills do not override system instructions, developer instructions, repository
  rules, or the user's authorization boundaries.
