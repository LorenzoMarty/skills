#!/usr/bin/env bash
# Cria um plugin (grupo de skills) e registra no marketplace.
#
# Uso: scripts/new-plugin.sh <nome-do-plugin> "<descrição>"
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
name="${1:-}"
description="${2:-}"

if [[ ! "$name" =~ ^[a-z0-9]+(-[a-z0-9]+)*$ || -z "$description" ]]; then
  echo "uso: scripts/new-plugin.sh <nome-em-kebab-case> \"<descrição>\"" >&2
  exit 1
fi
dir="$ROOT/plugins/$name"
if [[ -e "$dir" ]]; then
  echo "plugins/$name já existe" >&2
  exit 1
fi

mkdir -p "$dir/.claude-plugin" "$dir/skills"
touch "$dir/skills/.gitkeep"

python3 - "$ROOT" "$name" "$description" <<'PY'
import json
import sys
from pathlib import Path

root, name, description = Path(sys.argv[1]), sys.argv[2], sys.argv[3]
manifest = {
    "name": name,
    "version": "0.1.0",
    "description": description,
    "author": {"name": "Lorenzo Marty"},
}
(root / "plugins" / name / ".claude-plugin" / "plugin.json").write_text(
    json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
)
path = root / ".claude-plugin" / "marketplace.json"
marketplace = json.loads(path.read_text(encoding="utf-8"))
marketplace["plugins"].append(
    {"name": name, "source": f"./plugins/{name}", "description": description}
)
path.write_text(json.dumps(marketplace, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
PY

echo "Criado plugins/$name e registrado no marketplace."
