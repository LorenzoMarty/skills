#!/usr/bin/env bash
# Instala o marketplace lorenzo-skills no escopo do usuário, para valer em
# todos os projetos da máquina ou do ambiente na nuvem.
#
# Ambiente na nuvem (claude.ai/code): cole no "Setup script" do ambiente:
#   curl -fsSL https://raw.githubusercontent.com/LorenzoMarty/skills/main/scripts/cloud-setup.sh | bash
#
# Local: bash scripts/cloud-setup.sh
#
# Plugins instalados: variável SKILLS_PLUGINS (padrão: "workflow knowledge dev design").
set -euo pipefail

MARKETPLACE="${SKILLS_MARKETPLACE:-LorenzoMarty/skills}"
PLUGINS="${SKILLS_PLUGINS:-workflow knowledge dev design}"

if ! command -v claude >/dev/null 2>&1; then
  echo "claude CLI não encontrado; nada a instalar." >&2
  exit 0
fi

# "add" falha se o marketplace já existir; nesse caso só atualiza.
claude plugin marketplace add "$MARKETPLACE" >/dev/null 2>&1 \
  || claude plugin marketplace update lorenzo-skills >/dev/null 2>&1 || true

for plugin in $PLUGINS; do
  claude plugin install "$plugin@lorenzo-skills" >/dev/null 2>&1 \
    && echo "✓ $plugin@lorenzo-skills" \
    || echo "✗ falhou: $plugin@lorenzo-skills" >&2
done
