#!/usr/bin/env bash
# Prepara um projeto para usar as skills:
#   - mescla marketplace, plugins e permissões em .claude/settings.json
#   - cria CLAUDE.md a partir do modelo (se não existir)
#   - adiciona a GitHub Action do agente autônomo (se não existir)
#
# Uso: scripts/install-in-project.sh <pasta-do-projeto> [--no-action]
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TPL="$ROOT/templates/project"
project="${1:-}"
with_action=1
[[ "${2:-}" == "--no-action" ]] && with_action=0

if [[ -z "$project" || ! -d "$project" ]]; then
  echo "uso: scripts/install-in-project.sh <pasta-do-projeto> [--no-action]" >&2
  exit 1
fi

mkdir -p "$project/.claude"
python3 - "$TPL/.claude/settings.json" "$project/.claude/settings.json" <<'PY'
import json
import sys
from pathlib import Path

template = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
target = Path(sys.argv[2])
current = json.loads(target.read_text(encoding="utf-8")) if target.exists() else {}

for key in ("extraKnownMarketplaces", "enabledPlugins"):
    current.setdefault(key, {}).update(template[key])
allow = current.setdefault("permissions", {}).setdefault("allow", [])
allow.extend(rule for rule in template["permissions"]["allow"] if rule not in allow)

target.write_text(json.dumps(current, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"✓ {target}")
PY

copy_if_missing() {
  local src="$1" dest="$2"
  if [[ -e "$dest" ]]; then
    echo "• $dest já existe (mantido)"
  else
    mkdir -p "$(dirname "$dest")"
    cp "$src" "$dest"
    echo "✓ $dest"
  fi
}

copy_if_missing "$TPL/CLAUDE.md" "$project/CLAUDE.md"
if [[ $with_action -eq 1 ]]; then
  copy_if_missing "$TPL/.github/workflows/claude.yml" "$project/.github/workflows/claude.yml"
fi

echo
echo "Próximos passos:"
echo "  1. Preencha os comandos em CLAUDE.md (o agente usa no workflow:verify)."
[[ $with_action -eq 1 ]] && echo "  2. Adicione o secret CLAUDE_CODE_OAUTH_TOKEN no repositório (claude setup-token)."
echo "  Commit: git add .claude CLAUDE.md .github && git commit -m 'Configura skills do Claude'"
