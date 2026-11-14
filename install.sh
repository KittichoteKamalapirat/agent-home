#!/usr/bin/env bash
# Install this repo's skills, plugins and instructions for Claude Code and Codex.
# Safe to re-run. Never overwrites a file or folder it did not create.
set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENDOR="${AGENT_HOME_VENDOR:-$HOME/.agent-home/vendor}"
CLAUDE_SKILLS="$HOME/.claude/skills"
CODEX_SKILLS="$HOME/.agents/skills"
linked=0; skipped=0; failed=0

# Link one skill folder into one skills directory.
link_skill() { # <skill dir> <target skills dir>
  local src="$1" dest="$2/$(basename "$1")"
  mkdir -p "$2"
  if [ -L "$dest" ]; then
    rm "$dest"
  elif [ -e "$dest" ]; then
    echo "  skip (already exists, not ours): $dest"; skipped=$((skipped+1)); return
  fi
  ln -s "$src" "$dest" && linked=$((linked+1))
}

# Link a skill folder, or every skill folder inside it, for the chosen agents.
link_path() { # <path> <claude|codex|both>
  local path="$1" agents="$2" dirs=() d t
  if [ -f "$path/SKILL.md" ]; then dirs=("$path")
  else for d in "$path"/*/; do [ -f "${d}SKILL.md" ] && dirs+=("${d%/}"); done; fi
  if [ ${#dirs[@]} -eq 0 ]; then echo "  FAILED: no SKILL.md under $path"; failed=$((failed+1)); return; fi
  for d in "${dirs[@]}"; do
    [ "$agents" != codex ] && link_skill "$d" "$CLAUDE_SKILLS"
    [ "$agents" != claude ] && link_skill "$d" "$CODEX_SKILLS"
  done
}

# Download one repo at one revision, once.
fetch() { # <owner/repo> <ref>  -> prints the checkout path
  local dir="$VENDOR/${1//\//__}@$2"
  if [ ! -d "$dir/.git" ]; then
    rm -rf "$dir"; mkdir -p "$dir"
    ( cd "$dir" && git init -q && git remote add origin "https://github.com/$1" \
      && git fetch -q --depth 1 origin "$2" && git checkout -q FETCH_HEAD ) >&2 \
      || { rm -rf "$dir"; return 1; }
  fi
  echo "$dir"
}

echo "== Skills =="
link_path_if_any() { ls "$1"/*/SKILL.md >/dev/null 2>&1 && link_path "$1" both; }
link_path_if_any "$REPO/skills"
while read -r repo ref path agents; do
  case "$repo" in ''|'#'*) continue;; esac
  if dir="$(fetch "$repo" "$ref")"; then link_path "$dir/$path" "${agents:-both}"
  else echo "  FAILED: could not download $repo@$ref"; failed=$((failed+1)); fi
done < "$REPO/skills.txt"

echo "== Claude plugins =="
if command -v claude >/dev/null 2>&1; then
  while read -r source plugin; do
    case "$source" in ''|'#'*) continue;; esac
    market="${plugin#*@}"
    claude plugin marketplace add "$source" >/dev/null 2>&1 \
      || claude plugin marketplace update "$market" >/dev/null 2>&1
    if claude plugin install "$plugin" >/dev/null 2>&1 \
       || claude plugin list 2>/dev/null | grep -q "$plugin"; then echo "  ok: $plugin"
    else echo "  FAILED: $plugin"; failed=$((failed+1)); fi
  done < "$REPO/claude-plugins.txt"
else
  echo "  claude not installed here, skipping"
fi

echo "== Shared instructions =="
for dest in "$HOME/.claude/CLAUDE.md" "$HOME/.codex/AGENTS.md"; do
  if [ -L "$dest" ] || [ ! -e "$dest" ]; then
    mkdir -p "$(dirname "$dest")" && ln -sfn "$REPO/instructions/AGENTS.md" "$dest" && echo "  linked: $dest"
  else
    echo "  skip (you already have one): $dest"
  fi
done

echo
echo "Done: $linked skill links, $skipped skipped, $failed failed."
[ "$failed" -eq 0 ]
