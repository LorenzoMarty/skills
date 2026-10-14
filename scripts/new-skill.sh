#!/usr/bin/env bash
# Cria uma skill nova a partir de templates/skill.
#
# Uso: scripts/new-skill.sh <nome-da-skill> <plugin>
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
name="${1:-}"
plugin="${2:-}"

if [[ ! "$name" =~ ^[a-z0-9]+(-[a-z0-9]+)*$ || -z "$plugin" ]]; then
  echo "uso: scripts/new-skill.sh <nome-em-kebab-case> <plugin>" >&2
  exit 1
fi
dest="$ROOT/plugins/$plugin/skills/$name"
if [[ ! -d "$ROOT/plugins/$plugin" ]]; then
  echo "plugin '$plugin' não existe; crie com scripts/new-plugin.sh $plugin \"descrição\"" >&2
  exit 1
fi
if [[ -e "$dest" ]]; then
  echo "$dest já existe" >&2
  exit 1
fi

cp -R "$ROOT/templates/skill" "$dest"
sed -i.bak "s/^name: nome-da-skill$/name: $name/" "$dest/SKILL.md" && rm "$dest/SKILL.md.bak"
echo "Criada: plugins/$plugin/skills/$name/SKILL.md — edite a description antes do commit."
