#!/usr/bin/env bash
# Importa skills de uma pasta local para um plugin deste repositório.
#
# Uso:
#   scripts/import.sh <origem> [plugin] [--force]
#
# <origem> pode ser uma pasta de skills (ex.: ~/.claude/skills ou
# <projeto>/.claude/skills) ou uma única skill (pasta com SKILL.md).
# [plugin] é o plugin de destino em plugins/ (padrão: core).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
force=0
args=()
for arg in "$@"; do
  case "$arg" in
    --force) force=1 ;;
    *) args+=("$arg") ;;
  esac
done

src="${args[0]:-}"
plugin="${args[1]:-core}"
dest="$ROOT/plugins/$plugin/skills"

if [[ -z "$src" || ! -d "$src" ]]; then
  echo "uso: scripts/import.sh <origem> [plugin] [--force]" >&2
  exit 1
fi
if [[ ! -f "$ROOT/plugins/$plugin/.claude-plugin/plugin.json" ]]; then
  echo "plugin '$plugin' não existe; crie com scripts/new-plugin.sh $plugin \"descrição\"" >&2
  exit 1
fi

if [[ -f "$src/SKILL.md" ]]; then
  candidates=("$src")
else
  candidates=("$src"/*/)
fi

imported=0
for dir in "${candidates[@]}"; do
  dir="${dir%/}"
  [[ -f "$dir/SKILL.md" ]] || continue
  name="$(basename "$dir")"
  if [[ -e "$dest/$name" && $force -eq 0 ]]; then
    echo "• $name já existe em $plugin (use --force para sobrescrever)"
    continue
  fi
  rm -rf "${dest:?}/$name"
  # -L copia o conteúdo de symlinks em vez do link em si.
  cp -RL "$dir" "$dest/$name"
  echo "+ $name → plugins/$plugin/skills/$name"
  imported=$((imported + 1))
done

echo "$imported skill(s) importada(s)."
python3 "$ROOT/scripts/validate.py"
