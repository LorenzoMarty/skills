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
| `workflow` | Fluxo da ideia ao PR verificado: roteador, entrevista, spec, tickets, implementação, verificação, revisão, entrega, handoff |
| `knowledge` | Memória entre sessões e vault Obsidian: cache por projeto, registros, decisões, manutenção do vault |
| `design` | Front-end e design: telas, wireframes, design systems, UI/UX, motion, Three.js, imagem e mídia (algumas skills usam APIs pagas) |
| `marketing` | Copy, SEO, CRO, lançamento, social, marca, imagem e vídeo de marketing |
| `ops` | Observabilidade e segurança: OpenTelemetry, PromQL, dashboards Grafana, auditoria de skills e GitHub Actions |
| `dev` | Documentação atual de bibliotecas (exige o MCP do Context7), boas práticas de Postgres, descoberta de skills |

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
| Validar a ideia | Decidir o que fazer e executar por ticket/PR | `grill-me` (rodadas sobre a árvore de decisões) → `write-spec` → `to-tickets` → `implement` → `verify` |
| Especificar o que será feito | Detalhar requisitos e critério de concluído | `spec-interview` (uma pergunta por vez) → `spec-router` → `implement-spec` → `review-spec` → `ship-spec` |

As duas gravam `.claude/specs/<slug>/spec.md` com requisitos `REQ-N` e
`status: draft | ready | in-progress | needs-changes | done`.
`implement` e `verify` também consomem o `skills-plan.yaml` do `spec-router`
e chamam `quality-gate` em diff grande.

### Skills de apoio ao fluxo

| Momento | Skill |
|---|---|
| Antes de explorar código | `knowledge:knowledge-manager` |
| Spec salva | `workflow:spec-router` |
| Diff grande ou área sensível | `workflow:quality-gate` |
| Spec `done`: PR e issues | `workflow:ship-spec` (só com pedido explícito de push) |
| Tarefa concluída, não trivial | `knowledge:claude-obsidian` |
| Specs paradas em qualquer projeto | `workflow:specs-status` |

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
| `spec-interview` | Entrevista (uma pergunta por vez) e salva a spec |
| `spec-router` | Escolhe as skills para a spec e grava o `skills-plan.yaml` |
| `implement-spec` | Implementa exatamente os `REQ-N` da spec, commit por REQ |
| `review-spec` | Compara o construído com a spec, em runtime; devolve correções |
| `ship-spec` | Prepara o PR da spec e cria issues (Jira na Qiron, GitHub nos pessoais) |
| `specs-status` | Lista specs pendentes em todos os projetos |
| `quality-gate` | `verify` + `code-review` + `simplify` sobre o diff |
| `find-bugs` | Procura bugs e falhas de segurança nas mudanças da branch |

### `knowledge`

| Skill | Faz |
|---|---|
| `knowledge-manager` | Cache semântico por projeto: reaproveita o que já se sabe antes de ler código |
| `claude-obsidian` | Grava registros, decisões e arquitetura no vault Obsidian ao concluir tarefa |
| `organizar-vault` | Corrige problemas estruturais do vault (órfãs, links quebrados, frontmatter) |
| `diluir-vault` | Condensa, padroniza e agrupa notas atômicas |
| `token-trace` | Mostra onde os tokens foram gastos por tarefa e subagent (só por chamada explícita) |

### `marketing`

`ad-creative`, `ai-seo`, `brand`, `content-strategy`, `copy-editing`,
`copywriting`, `cro`, `launch`, `marketing-psychology`, `seo-audit`, `social`,
`humanizer`, `mkt-image`, `mkt-video`, `brag`.

### `ops`

| Skill | Faz |
|---|---|
| `opentelemetry` | Instrumenta apps e envia métricas/logs/traces ao Grafana |
| `promql` | Escreve e otimiza consultas PromQL |
| `dashboarding` | Cria dashboards Grafana via API |
| `skill-scanner` | Escaneia skills em busca de problemas de segurança |
| `agentic-actions-auditor` | Audita GitHub Actions com agentes de IA |

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
| `design-dna` | Extrai, define e aplica o "design DNA" (tokens, estilo, efeitos) a partir de referências |
| `motion-design` | Princípios e implementação de animação e transições |
| `react-best-practices` | Performance em React/Next.js (Vercel) |
| `ui-styling` | shadcn/ui, Tailwind e temas |
| `ui-ux-pro-max` | Base de estilos, paletas, fontes e diretrizes de UX |
| `web-design-guidelines` | Revisa UI contra as Web Interface Guidelines |
| `threejs-*` | Three.js: `fundamentals`, `geometry`, `materials`, `textures`, `lighting`, `shaders`, `animation`, `interaction`, `loaders`, `postprocessing` |

### `dev`

| Skill | Faz |
|---|---|
| `context7-mcp` | Consulta a documentação atual de bibliotecas via Context7 |
| `supabase-postgres-best-practices` | Boas práticas de Postgres (Supabase) |
| `find-skills` | Descobre e instala skills |

## Instalação

### Em todos os projetos na nuvem (claude.ai/code)

No ambiente da nuvem: menu do ambiente → **Edit** → **Setup script**, adicione:

```bash
curl -fsSL https://raw.githubusercontent.com/LorenzoMarty/skills/main/scripts/cloud-setup.sh | bash
```

Toda sessão nova nesse ambiente já começa com os plugins instalados e
atualizados. Para escolher plugins: `SKILLS_PLUGINS="workflow knowledge dev" bash` (padrão: `workflow knowledge dev design`).

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
