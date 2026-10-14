# Skills

Skills do Lorenzo para o [Claude Code](https://claude.com/claude-code),
distribuídas como **marketplace de plugins** (`lorenzo-skills`). Valem para
todos os projetos, local e na nuvem. Este README é a referência do que existe
e de como as peças se encaixam; as convenções para escrever skills ficam em
[CLAUDE.md](CLAUDE.md).

As skills aparecem com o prefixo do plugin: `/workflow:implement #42`.

## Plugins

| Plugin | Conteúdo |
|---|---|
| `workflow` | Fluxo da ideia ao PR verificado: roteador, entrevista, spec, tickets, implementação, verificação, handoff |
| `personal` | Especificação por entrevista, memória e Obsidian, marketing, front-end/3D, observabilidade, segurança |
| `design` | Telas, wireframes, design systems, imagem e mídia (algumas skills usam APIs pagas) |
| `dev` | Documentação atual de bibliotecas (exige o MCP do Context7) |

Parte das skills é fork de [rtadewald/skills](https://github.com/rtadewald/skills),
veja [UPSTREAM.md](UPSTREAM.md).

## O fluxo de trabalho

`workflow:start` é o roteador: classifica o pedido e escolhe a cadeia. Um hook
de `SessionStart` lembra o Claude de usá-lo em toda sessão.

```
ideia vaga ─► grill-me ─► write-spec ─► to-tickets ─► implement ─► verify ─► PR
                                                          │            │
                                                          └─ handoff ◄─┘ (contexto cheio)
```

- **Modo autônomo por padrão:** decisões reversíveis são tomadas e registradas
  como `Assumido:`; só para quando a decisão é irreversível ou muda escopo.
- **Você revisa o relatório do `verify`**, não o diff linha a linha.
- **Economia de contexto:** exploração vai para subagentes, a spec guarda as
  decisões, um ticket por sessão, `handoff` antes de estourar.

### Duas cadeias de spec

| Cadeia | Para quê | Passos |
|---|---|---|
| `workflow` | **Validar a ideia** e executar por ticket/PR | `grill-me` (rodadas sobre a árvore de decisões) → `write-spec` → `to-tickets` → `implement` → `verify` |
| `personal` | **Especificar o que será feito** | `spec-interview` (uma pergunta por vez) → `spec-router` → `implement-spec` → `review-spec` → `ship-spec` |

As duas gravam `.claude/specs/<slug>/spec.md` com requisitos `REQ-N` e
`status: draft | ready | in-progress | needs-changes | done`.
`implement` e `verify` também consomem o `skills-plan.yaml` do `spec-router`
e chamam `quality-gate` em diff grande.

### Ligação com as skills pessoais

| Momento | Skill |
|---|---|
| Antes de explorar código | `personal:knowledge-manager` |
| Spec salva | `personal:spec-router` |
| Diff grande ou área sensível | `personal:quality-gate` |
| Spec `done`: PR e issues | `personal:ship-spec` (só com pedido explícito de push) |
| Tarefa concluída, não trivial | `personal:claude-obsidian` |
| Specs paradas em qualquer projeto | `personal:specs-status` |

## Catálogo de skills

### `workflow`

| Skill | Faz |
|---|---|
| `start` | Roteador: classifica o pedido, escolhe cadeia e modo |
| `grill-me` | Entrevista em rodadas até não sobrar decisão implícita |
| `write-spec` | Escreve a spec com `REQ-N` testáveis |
| `to-tickets` | Quebra a spec em tickets com dependências declaradas e publica no tracker |
| `implement` | Teste que falha → código → verify → commit e PR |
| `verify` | Checks, evidência por REQ, leitura adversarial do diff, relatório |
| `handoff` | Compacta a conversa num documento para outra sessão continuar |

### `personal`

| Grupo | Skills |
|---|---|
| Especificação e entrega | `spec-interview`, `spec-router`, `implement-spec`, `review-spec`, `ship-spec`, `specs-status`, `quality-gate` |
| Memória e Obsidian | `knowledge-manager`, `claude-obsidian`, `organizar-vault`, `diluir-vault`, `token-trace` |
| Qualidade e segurança | `find-bugs`, `skill-scanner`, `agentic-actions-auditor` |
| Marketing e conteúdo | `ad-creative`, `ai-seo`, `brand`, `content-strategy`, `copy-editing`, `copywriting`, `cro`, `launch`, `marketing-psychology`, `seo-audit`, `social`, `humanizer`, `mkt-image`, `mkt-video`, `brag` |
| Front-end e design | `design-dna`, `motion-design`, `react-best-practices`, `ui-styling`, `ui-ux-pro-max`, `web-design-guidelines` |
| Three.js | `threejs-fundamentals`, `-geometry`, `-materials`, `-textures`, `-lighting`, `-shaders`, `-animation`, `-interaction`, `-loaders`, `-postprocessing` |
| Dados e observabilidade | `supabase-postgres-best-practices`, `opentelemetry`, `promql`, `dashboarding` |
| Descoberta | `find-skills` |

`token-trace` tem `disable-model-invocation`: só roda quando você a chama.

### `design`

| Skill | Faz |
|---|---|
| `plan-screen` | Compara três propostas de tela com wireframes e gera os mocks em paralelo (só por chamada explícita) |
| `to-wireframe` | Cria wireframe tipado (ASCII ou SVG) a partir de imagem ou brief |
| `img-to-html` | Recria um mock de UI como HTML/CSS/JS estático, em etapas com aprovação (só por chamada explícita) |
| `extract-ds` | Monta um design system a partir de um site local pronto, preservando as animações |
| `to-img` | Gera imagens em paralelo via OpenRouter |
| `openrouter-img` | Gera/edita imagem via OpenRouter com vários modelos (API paga; só por chamada explícita) |
| `nano-banana-pro` | Gera/edita imagem com a API Nano Banana Pro do Google (API paga) |
| `fal-ai` | Chama as APIs do fal.ai, p. ex. detecção de caixas de texto/UI para `img-to-html` (API paga; só por chamada explícita) |
| `mediabunny` | Manipulação de mídia com a biblioteca Mediabunny |

### `dev`

| Skill | Faz |
|---|---|
| `context7-mcp` | Consulta a documentação atual de bibliotecas via Context7 |

## Instalação

### Em todos os projetos na nuvem (claude.ai/code)

No ambiente da nuvem: menu do ambiente → **Edit** → **Setup script**, adicione:

```bash
curl -fsSL https://raw.githubusercontent.com/LorenzoMarty/skills/main/scripts/cloud-setup.sh | bash
```

Toda sessão nova nesse ambiente já começa com os plugins instalados e
atualizados. Para escolher plugins: `SKILLS_PLUGINS="workflow dev" bash`.

### Na sua máquina

```bash
git clone https://github.com/LorenzoMarty/skills.git && cd skills
bash scripts/cloud-setup.sh
```

Ou pelo próprio Claude Code: `/plugin marketplace add LorenzoMarty/skills` e
`/plugin install workflow@lorenzo-skills`. Atualizar:
`/plugin marketplace update lorenzo-skills`.

### Em um projeto (vale para quem clonar e para a GitHub Action)

```bash
scripts/install-in-project.sh ~/projetos/Estoque-NY
```

Mescla o marketplace e uma lista de permissões em `.claude/settings.json`,
cria o `CLAUDE.md` a partir do modelo e adiciona
`.github/workflows/claude.yml` (se o projeto já tiver um, mantém o dele; copie
de lá só `label_trigger`, `plugin_marketplaces` e `plugins`). Preencha os
comandos no `CLAUDE.md`: são eles que o `verify` roda.

> O `.claude/settings.json` do projeto **oferece** instalar o marketplace na
> primeira vez que você abre o projeto no Claude Code interativo; ele não
> instala sozinho em modo não interativo. Na nuvem, quem garante os plugins é
> o setup script acima; na GitHub Action, os campos `plugins` do `claude.yml`.

## Automação: o agente trabalhando sozinho

Com o `claude.yml` do modelo no projeto (requer o
[Claude GitHub App](https://github.com/apps/claude) e o secret
`CLAUDE_CODE_OAUTH_TOKEN`, gerado com `claude setup-token`):

1. Você escreve ou pede a spec (`workflow:write-spec`) e os tickets
   (`workflow:to-tickets`) → issues com a label `ready-for-agent`.
2. Cada issue com essa label dispara o agente, que roda `workflow:implement`,
   sobe a branch e comenta o link do PR já preenchido (a Action não abre o PR
   sozinha: o clique final é seu).
3. Você revisa o relatório e aprova; pede ajustes comentando `@claude` no PR.
4. Ticket que precisa de decisão sua volta com a label `needs-human`.

Numa sessão interativa, `workflow:implement backlog` faz o mesmo em sequência.

## Manutenção

| Comando | Faz |
|---|---|
| `python3 scripts/validate.py` | Estrutura e frontmatter (o CI roda o mesmo + `claude plugin validate`) |
| `scripts/new-plugin.sh <nome> "<descrição>"` | Cria plugin |
| `scripts/new-skill.sh <nome> <plugin>` | Cria skill a partir do modelo |
| `scripts/import.sh <pasta> <plugin>` (Windows: `scripts\import.ps1`) | Traz skills de outra pasta para um plugin |
| `claude --plugin-dir ./plugins/workflow` | Testa um plugin sem publicar |
| `scripts/sync-upstream.sh` | Traz novidades do fork original |

O `import` barra a cópia se achar algo com cara de segredo (o repositório é
público) e manda skills com nome já existente para `imports/conflicts/<nome>/`.
`import.ps1` aceita `-Exclude nome1,nome2` e `-Force`; chame-o direto
(`& .\scripts\import.ps1 -Exclude a,b`), pois `powershell -File` entrega a
lista como uma string só. No Windows, os `.sh` exigem Git Bash ou WSL.

Ao mudar nome de skill ou plugin, atualize este README e
`plugins/workflow/skills/start/SKILL.md`; ao alterar um plugin, suba a
`version` no `plugin.json`.
