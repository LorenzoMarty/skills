#!/usr/bin/env bash
# Mostra o que mudou em rtadewald/skills desde a última sincronização, só
# para as skills que vieram de lá. Não altera nada: aplique à mão o que fizer
# sentido e depois grave o novo SHA em .upstream-sha.
#
# Uso: scripts/sync-upstream.sh [--patch]
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
UPSTREAM="https://github.com/rtadewald/skills.git"
base="$(cat "$ROOT/.upstream-sha")"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

git clone -q --filter=blob:none "$UPSTREAM" "$tmp/up"
head="$(git -C "$tmp/up" rev-parse --short HEAD)"
if [[ "$(git -C "$tmp/up" rev-parse "$base")" == "$(git -C "$tmp/up" rev-parse HEAD)" ]]; then
  echo "Sem mudanças desde $base."
  exit 0
fi

# Skills locais que existem no upstream.
paths=()
for dir in "$ROOT"/plugins/*/skills/*/; do
  name="$(basename "$dir")"
  [[ -d "$tmp/up/$name" ]] && paths+=("$name")
done
[[ -d "$tmp/up/motion-lab" ]] && paths+=("motion-lab")

echo "Upstream: $base → $head"
if [[ "${1:-}" == "--patch" ]]; then
  git -C "$tmp/up" diff "$base" HEAD -- "${paths[@]}"
else
  git -C "$tmp/up" diff --stat "$base" HEAD -- "${paths[@]}"
  echo
  echo "Skills novas no upstream:"
  git -C "$tmp/up" diff --name-only --diff-filter=A "$base" HEAD -- '*/SKILL.md' | sed 's#/SKILL.md##; s#^#  #'
fi
echo
echo "Depois de aplicar: echo $head > .upstream-sha"
