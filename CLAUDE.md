# LorenzoMarty/skills

Marketplace de plugins do Claude Code (`lorenzo-skills`). Cada pasta em
`plugins/` é um plugin; cada `plugins/<plugin>/skills/<skill>/SKILL.md` é uma
skill.

## Comandos

```bash
python3 scripts/validate.py          # estrutura + frontmatter (rode antes de todo commit)
python3 scripts/audit.py             # falhas de qualidade do catálogo (avisos)
claude plugin validate .             # manifestos
scripts/new-skill.sh <nome> <plugin>
scripts/new-plugin.sh <nome> "<descrição>"
scripts/import.sh <pasta> <plugin>   # trazer skills de ~/.claude/skills ou de um projeto
scripts/sync-upstream.sh             # mudanças no fork original
```

## Como escrever uma skill

1. **description** decide o acionamento: diga o que faz **e quando usar**,
   com as frases que o usuário diria. Máx. 1024 caracteres.
2. Corpo nesta ordem: **quem você é → objetivo → processo em alto nível →
   exemplo curto**; só depois regras e detalhes.
3. Termine com **Próximo passo**: qual skill vem depois (`plugin:skill`).
   Não copie instruções de outra skill; aponte para ela.
4. Curto. Detalhe longo vai para `references/` e é lido sob demanda.
5. Scripts da própria skill: `${CLAUDE_SKILL_DIR}/scripts/...`. De outra skill
   do mesmo plugin: `${CLAUDE_SKILL_DIR}/../<skill>/...`.
6. `disable-model-invocation: true` só em skills que gastam dinheiro (APIs
   pagas) ou são destrutivas: elas deixam de poder ser encadeadas.
7. Mudou nome de skill ou plugin → atualize `README.md` e
   `plugins/workflow/skills/start/SKILL.md` (o roteador).
8. Suba `version` no `plugin.json` do plugin alterado.

`agents/openai.yaml` existe nas skills vindas do upstream para compatibilidade
com Codex; mantenha se editar a skill.

## Contexto no Obsidian

Hub: `02 - Projetos/Lorenzo Skills/Lorenzo Skills.md` (Arquitetura, Decisões e Registros na mesma pasta).
