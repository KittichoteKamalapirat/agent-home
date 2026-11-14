# agent-home

One source for my coding-agent setup, shared by Claude Code and Codex, on my own machines and in cloud sessions.

## What is here

| File | Purpose |
|---|---|
| `skills/` | Skills I wrote myself, one folder per skill |
| `skills.txt` | Third-party skills to pull, pinned to a revision |
| `claude-plugins.txt` | Claude Code plugins to install |
| `instructions/AGENTS.md` | Working preferences shared by every project |
| `install.sh` | Installs all of the above |

## Install or update

```bash
git clone https://github.com/KittichoteKamalapirat/agent-home ~/agent-home
```

```bash
~/agent-home/install.sh
```

To update later, `git pull` in `~/agent-home` and run `install.sh` again.

The installer links skills into `~/.claude/skills` (Claude Code) and `~/.agents/skills` (Codex). It never replaces a file or folder it did not create, and it exits with an error if anything failed.

## Cloud sessions

Paste this as the setup script of a Claude Code or Codex cloud environment:

```bash
#!/bin/bash
rm -rf /opt/agent-home
git clone -q --depth 1 https://github.com/KittichoteKamalapirat/agent-home /opt/agent-home \
  && bash /opt/agent-home/install.sh || echo "agent-home install had failures"
```

## Changing what is installed

- Add or remove a third-party skill: edit `skills.txt`.
- Add my own skill: create `skills/<name>/SKILL.md`.
- Pick up a newer upstream version: change the revision in `skills.txt`.

No secrets belong in this repo. It is public.
