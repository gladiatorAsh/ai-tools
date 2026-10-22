#!/bin/bash
# Copy this pack's skills (and optionally agents) into Copilot's discovery folders.
#
#   scripts/install.sh                     # personal: ~/.copilot/skills  (all your projects)
#   scripts/install.sh --project <repo>    # project:  <repo>/.github/skills and <repo>/.github/agents
#   scripts/install.sh --skill llm-evals   # only one skill (repeatable)
#
# Existing skills with the same name are replaced; nothing else in the target is touched.
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
skills_dest="${HOME}/.copilot/skills"
agents_dest=""
selected=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --project)
      [[ -d "${2:-}" ]] || { echo "error: --project needs an existing directory" >&2; exit 2; }
      skills_dest="$(cd "$2" && pwd)/.github/skills"
      agents_dest="$(cd "$2" && pwd)/.github/agents"
      shift 2 ;;
    --skill)
      [[ -n "${2:-}" ]] || { echo "error: --skill needs a name" >&2; exit 2; }
      selected+=("$2"); shift 2 ;;
    -h|--help)
      sed -n '2,8p' "$0"; exit 0 ;;
    *)
      echo "error: unknown argument '$1'" >&2; exit 2 ;;
  esac
done

if [[ ${#selected[@]} -eq 0 ]]; then
  for d in "$here"/skills/*/; do selected+=("$(basename "$d")"); done
fi

mkdir -p "$skills_dest"
for name in "${selected[@]}"; do
  [[ "$name" =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]] || { echo "error: invalid skill name '$name'" >&2; exit 2; }
  src="$here/skills/$name"
  [[ -f "$src/SKILL.md" ]] || { echo "error: no skill named '$name'" >&2; exit 1; }
  rm -rf "${skills_dest:?}/$name"
  cp -R "$src" "$skills_dest/$name"
  echo "installed skill: $name -> $skills_dest/$name" >&2
done

if [[ -n "$agents_dest" ]]; then
  mkdir -p "$agents_dest"
  cp "$here"/agents/*.agent.md "$agents_dest/"
  echo "installed agents -> $agents_dest" >&2
fi

echo "done. In Copilot CLI run '/skills reload'; in VS Code start a new chat and type '/skills'." >&2
