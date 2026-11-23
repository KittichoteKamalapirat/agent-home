# Shared working preferences

These apply to every project and to both Claude Code and Codex. A project's own
AGENTS.md or CLAUDE.md takes precedence where they differ.

## Default working style

- Use Poteto Mode for any task that changes code or needs rigor. In Claude Code it
  is the `pstack:poteto-mode` skill; in Codex it is
  `~/.agents/skills/poteto-mode/SKILL.md`. Skip it for quick questions and
  one-line edits.
- Use the `codebase-design` skill when designing or restructuring code.

## TypeScript linting

- TypeScript projects use oxlint, with type-aware rules on, next to strict
  `tsc`. The type checker stays the main net; oxlint catches what it allows,
  such as floating promises, unused code and leftover `debugger` or
  `console.log`.
- Before finishing a change in a TypeScript project, run its lint script and
  fix every oxlint finding. Suppress one only with an inline
  `oxlint-disable-next-line <rule> -- <reason>` when the code is intentional.
- If a TypeScript project has no oxlint yet, suggest adding it instead of
  adding it unasked.

## Skills

- Shared skills are installed from the agent-home repo
  (github.com/KittichoteKamalapirat/agent-home). Do not copy shared skills into a
  project.
- Project-specific skills live in the project's own `.agents/skills`.

### Creating or editing a skill

Whichever skill-writing skill you use, decide where the skill belongs before
writing any files:

- If it only makes sense for one project, create it in that project's
  `.agents/skills/<name>` and deliver it the way that repo delivers changes.
- Otherwise it is a shared skill and belongs in agent-home. Do not create it
  directly in `~/.claude/skills`, `~/.agents/skills` or `~/.codex/skills`; a
  skill created there exists on one machine only.

For a shared skill:

1. Find the local agent-home checkout with `readlink ~/.claude/CLAUDE.md` (or
   `~/.codex/AGENTS.md`); the repo root is two folders above that file. Run
   `git pull` there first.
2. A skill of my own goes in `skills/<name>/SKILL.md` in that checkout. A public
   skill from someone else's repo goes in `skills.txt` as a line with the repo
   and a pinned revision.
3. Run `./install.sh` so both agents on this machine get it.
4. The repo is public. Before committing, check the skill for secrets, tokens,
   private paths and details of unreleased work, and stop to ask me if you find
   any.
5. Commit and push to `master` in the same task. The skill is not finished until
   it is on GitHub, because the cloud and my other machines install from there.

If the agent-home checkout cannot be pushed from the current session, say so and
give me the files to add; do not leave a local-only copy as the result.

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
