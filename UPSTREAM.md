# Origem das skills

Parte das skills deste repositório é um fork de
[rtadewald/skills](https://github.com/rtadewald/skills) (commit registrado em
`.upstream-sha`). O repositório original não declara licença; o crédito
pertence ao autor original. `grill-me`, `to-tickets` e `handoff` por sua vez
derivam de [mattpocock/skills](https://github.com/mattpocock/skills).

| Skill | Plugin | Mudanças aqui |
|---|---|---|
| grill-me | workflow | descrição para acionamento automático, modo autônomo, encadeia em write-spec |
| to-tickets | workflow | tracker padrão GitHub Issues sem setup externo, modo autônomo, link para spec, encadeia em implement |
| handoff | workflow | reescrita: destino que sobrevive a sessões na nuvem (PR/issue/spec) |
| context7-mcp | dev | — |
| plan-screen, to-wireframe, img-to-html, extract-ds, to-img | design | referências `$skill` → `design:skill`; caminhos via `${CLAUDE_SKILL_DIR}`; links para o fluxo |
| openrouter-img, nano-banana-pro, fal-ai, mediabunny | design | caminhos via `${CLAUDE_SKILL_DIR}` |
| motion-lab | design (`references/`) | catálogo de referência, não é skill |

Não vieram (citadas no README original, mas ausentes no repositório):
`ds-from-*`, `ds-cards-*`, `img-to-html2`, `img-to-html3`, `animate`,
`find-font`.

Para ver o que mudou no original desde a última sincronização:
`scripts/sync-upstream.sh` (ou `--patch` para o diff completo).
