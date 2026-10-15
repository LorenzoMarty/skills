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
| `workflow` | Fluxo da ideia ao PR verificado: roteador, entrevista, spec, tickets, implementação, verificação, entrega, handoff |
| `knowledge` | Memória entre sessões e vault Obsidian: cache por projeto, registros, decisões, manutenção do vault |
| `design` | Front-end e design: telas, wireframes, design systems, UI/UX, motion, Three.js, imagem e mídia (algumas skills usam APIs pagas) |
| `marketing` | Copy, SEO, CRO, lançamento, social, marca, imagem e vídeo de marketing |
| `ops` | Observabilidade e segurança: OpenTelemetry, PromQL, dashboards Grafana, auditoria de skills e GitHub Actions |
| `dev` | Documentação atual de bibliotecas (exige o MCP do Context7), boas práticas de Postgres, descoberta de skills |

Parte das skills é fork de [rtadewald/skills](https://github.com/rtadewald/skills),
veja [UPSTREAM.md](UPSTREAM.md). Plugins de outras pessoas que uso junto estão em
[Plugins de terceiros](#plugins-de-terceiros).

## O fluxo de trabalho

`workflow:start` é o roteador: classifica o pedido e escolhe a cadeia. Um hook
de `SessionStart` lembra o Claude de usá-lo em toda sessão.

```
grill-me ─► write-spec ─► spec-router ─► to-tickets ─► implement ─► verify ─► ship-spec
(se vago)                                (se grande)       ▲           │
                                                           └ correções ┘
file-issue: toda decisão, bug ou dívida descoberta vira issue na hora
handoff: em qualquer ponto, quando o contexto estiver acabando
```

Um fluxo só, com uma skill por etapa:

| Etapa | Skill | Saída |
|---|---|---|
| Decidir | `grill-me` | árvore de decisões resolvida (só se a ideia é vaga) |
| Especificar | `write-spec` | `.claude/specs/<slug>/spec.md` com `REQ-N` e `status` |
| Rotear skills | `spec-router` | `skills-plan.yaml` ao lado da spec |
| Quebrar | `to-tickets` | tickets com dependências (só se não cabe numa sessão) |
| Executar | `implement` | commits por REQ, teste primeiro |
| Provar | `verify` | relatório por REQ; fecha a spec (`done` ou `needs-changes`, que volta ao `implement`) |
| Entregar | `ship-spec` | push, PR com assignee e issues do que sobrou (merge é seu) |
| Em fila | `autopilot` | backlog inteiro até o objetivo ficar pronto |

`status` da spec: `draft | ready | in-progress | needs-changes | done`.

- **Modo autônomo por padrão:** decisões reversíveis são tomadas e registradas
  como `Assumido:`; só para quando a decisão é irreversível ou muda escopo.
- **Você decide só o merge** (e as issues `needs-human`): push, PR, review e issues são autorizados em definitivo; merge, force-push e push em `main` nunca.
- **Você revisa o relatório do `verify`**, não o diff linha a linha.
- **Economia de contexto:** exploração vai para subagentes, a spec guarda as
  decisões, um ticket por sessão, `handoff` antes de estourar.

Skills de apoio: `knowledge:knowledge-manager` (antes de explorar),
`workflow:quality-gate` (chamado pelo `verify` em diff grande ou área
sensível), `knowledge:claude-obsidian` (registro ao concluir),
`workflow:specs-status` (specs paradas em qualquer projeto) e
`workflow:find-bugs` (caça bugs na branch).

## Catálogo de skills

Legenda: 💲 usa API paga · ✋ só roda por chamada explícita (`disable-model-invocation`).
Para auditar o catálogo: `python3 scripts/audit.py`.

### `workflow`

| Skill | Faz |
|---|---|
| `start` | Roteador: classifica o pedido, escolhe cadeia e modo |
| `grill-me` | Entrevista em rodadas até não sobrar decisão implícita |
| `write-spec` | Escreve a spec com `REQ-N` testáveis |
| `spec-router` | Escolhe as skills para a spec e grava o `skills-plan.yaml` |
| `to-tickets` | Quebra a spec em tickets com dependências e publica no tracker |
| `implement` | Teste que falha → código → verify → commit e PR |
| `verify` | Checks, evidência por REQ, leitura adversarial do diff, fecha a spec |
| `ship-spec` | Push, PR (assignee `LorenzoMarty` em repositórios pessoais) e issues do que sobrou (Jira nos de trabalho, GitHub nos pessoais) |
| `autopilot` | Trabalha o backlog inteiro: implementa, PR, review, novas issues; só espera o merge |
| `file-issue` | Cria issue robusta: dedupe, tipo, critério de aceite, bloqueios, labels, assignee |
| `quality-gate` | `code-review` + `simplify` sobre o diff |
| `find-bugs` | Procura bugs e falhas de segurança nas mudanças da branch |
| `specs-status` | Lista specs pendentes em todos os projetos |
| `handoff` | Compacta a conversa num documento para outra sessão continuar |

### `knowledge`

| Skill | Faz |
|---|---|
| `knowledge-manager` | Cache semântico por projeto: reaproveita o que já se sabe antes de ler código |
| `claude-obsidian` | Grava registros, decisões, arquitetura e armadilhas de bibliotecas (`tags: biblioteca`, `context7_id`) no vault |
| `organizar-vault` | Corrige problemas estruturais do vault (órfãs, links quebrados, frontmatter) |
| `diluir-vault` | Condensa, padroniza e agrupa notas atômicas |
| `token-trace` ✋ | Mostra onde os tokens foram gastos por tarefa e subagent |

### `marketing`

| Skill | Faz |
|---|---|
| `brand` | Voz de marca, identidade visual, mensagens e consistência |
| `copywriting` | Escreve copy de página: home, landing, preços, produto |
| `copy-editing` | Edita e revisa copy existente em passadas |
| `humanizer` | Detecta 53 padrões de texto de IA e reescreve em cinco vozes |
| `content-strategy` | Planeja temas, clusters e calendário editorial |
| `social` | Posts e calendário para LinkedIn, X, Instagram, TikTok; escuta e engajamento |
| `ad-creative` | Gera e itera títulos, textos e variações de anúncio pago |
| `cro` | Otimiza conversão de páginas e formulários |
| `launch` | Plano de lançamento: produto, feature, Product Hunt, go-to-market |
| `marketing-psychology` | Princípios psicológicos e modelos mentais aplicados a marketing |
| `seo-audit` | Audita SEO técnico e on-page de um site |
| `ai-seo` | Otimiza conteúdo para ser citado por buscadores de IA (AEO/GEO) |
| `mkt-image` 💲 | Cria e edita imagens de marketing (heros, social, mockups) |
| `mkt-video` 💲 | Produz vídeo de marketing com ferramentas de IA ou Remotion/Hyperframes |
| `brag` | Transforma o site do projeto num vídeo de lançamento curto (Hyperframes) |

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
| `plan-screen` ✋ | Compara três propostas de tela com wireframes e gera os mocks em paralelo |
| `to-wireframe` | Cria wireframe tipado (ASCII ou SVG) a partir de imagem ou brief |
| `img-to-html` ✋ | Recria um mock de UI como HTML/CSS/JS estático, em etapas com aprovação |
| `extract-ds` | Monta um design system a partir de um site local pronto, preservando animações |
| `design-dna` | Extrai, define e aplica o "design DNA" (tokens, estilo, efeitos) |
| `ui-ux-pro-max` | Base de estilos, paletas, fontes e diretrizes de UX |
| `ui-styling` | shadcn/ui, Tailwind e temas |
| `web-design-guidelines` | Revisa UI contra as Web Interface Guidelines |
| `motion-design` | Princípios e implementação de animação e transições |
| `react-best-practices` | Performance em React/Next.js (Vercel) |
| `to-img` 💲 | Gera imagens em paralelo via OpenRouter |
| `openrouter-img` 💲✋ | Gera/edita imagem via OpenRouter com vários modelos |
| `nano-banana-pro` 💲 | Gera/edita imagem com a API Nano Banana Pro do Google |
| `fal-ai` 💲✋ | Chama as APIs do fal.ai, p. ex. detecção de caixas de UI para `img-to-html` |
| `mediabunny` | Manipulação de mídia com a biblioteca Mediabunny |
| `threejs-*` | Three.js: `fundamentals`, `geometry`, `materials`, `textures`, `lighting`, `shaders`, `animation`, `interaction`, `loaders`, `postprocessing` |

### `dev`

| Skill | Faz |
|---|---|
| `context7-mcp` | Documentação atual via Context7 (exige o MCP): lê o vault antes e grava no Obsidian só as armadilhas não óbvias |
| `supabase-postgres-best-practices` | Boas práticas de Postgres (Supabase) |
| `find-skills` | Descobre e instala skills |

## Plugins de terceiros

Não fazem parte deste marketplace: vêm de outros e são instalados à parte. Os
três rodam juntos com o `lorenzo-skills` nesta máquina sem conflito observado.

| Plugin | Origem | Faz | Instalar |
|---|---|---|---|
| `ponytail` | [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) | Modo "desenvolvedor preguiçoso": reutilizar antes de escrever, stdlib e nativo antes de dependência, diff mínimo e um check rodável | `/plugin marketplace add DietrichGebert/ponytail` e `/plugin install ponytail@ponytail` |
| `caveman` | [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) | Respostas curtas (menos tokens de saída); código e commits continuam normais | `/plugin marketplace add JuliusBrussee/caveman` e `/plugin install caveman@caveman` |
| `ifixai` | [ifixai-ai/iFixAi](https://github.com/ifixai-ai/iFixAi) (Apache-2.0) | Auditoria independente de agentes de IA: inspeções adversariais e scorecard de desalinhamento (`/ifixai:ifixai`) | já habilitado neste repositório (`.claude/settings.json`); em outro projeto: `/plugin marketplace add ifixai-ai/iFixAi` e `/plugin install ifixai@ifixai-community` |

- **Escopo:** `ponytail` e `caveman` estão no escopo de usuário (só na máquina
  do Lorenzo). Na GitHub Action eles **não** rodam: o job `autopilot` instala só
  `workflow` e `dev`. O `ifixai` fica no escopo do projeto.
- **`ifixai`:** o hook `SessionStart` cria um venv e instala `ifixai[anthropic]==3.3.0`
  (versão fixada) na primeira sessão. Cada provedor é cobrado na conta da sua
  chave; uma rodada completa com dois juízes custa na ordem de US$ 10–14, fora o
  agente testado. A fixture padrão traz defeitos plantados de propósito: ela
  serve para aprender, não para auditar o seu agente (use `--fixture`).
- **Quando usar o `ifixai`:** agentes que você entrega com permissões e
  ferramentas (ex.: os projetos com Agno). Não serve para auditar skills.

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
scripts/install-in-project.sh ~/projetos/meu-projeto
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

**Na sua máquina:** `/workflow:autopilot` (ou "toca tudo"). Ele pega cada issue
`ready-for-agent`, implementa, dá push, abre o PR com assignee e faz o code
review; tudo que descobre ou decide vira issue (`file-issue`); empilha PRs
quando uma issue depende de outra ainda não mergeada. Para quando o objetivo
da spec está pronto (REQs feitos, nenhuma lacuna nova) e lista o que depende
de você: merges e issues `needs-human`. Rode de novo depois de mergear.

**Na nuvem (GitHub Action):** o `claude.yml` do modelo tem três jobs
(requer o [Claude GitHub App](https://github.com/apps/claude) e o secret
`CLAUDE_CODE_OAUTH_TOKEN`, gerado com `claude setup-token`):

| Job | Dispara com | Faz |
|---|---|---|
| `claude` | `@claude` em issue ou PR | Explica, revisa ou implementa o pedido |
| `autopilot` | você aplica `ready-for-agent`, **ou** um PR é mergeado | Implementa uma issue, dá push, abre o PR (`Closes #N`, assignee, relatório do `verify`) e cria issues para o que descobrir |
| `review` | PR aberto ou atualizado | Code review em comentários; achado fora de escopo vira issue |

O ciclo: você escreve a spec e os tickets (`write-spec`, `to-tickets`) → aplica
`ready-for-agent` → PR com review → **você faz o merge** → o merge dispara a
próxima issue desbloqueada → e assim até a fila acabar. Issue que precisa de
decisão sua volta como `needs-human`. Issues criadas pelo próprio agente não
disparam sozinhas (evita cascata): entram na fila pelo próximo merge ou pela
sua label.

O `install-in-project.sh` libera push, `gh pr/issue` e nega `gh pr merge`,
force-push e push em `main` nas permissões do projeto. Se `gh pr create` falhar
com 403, ative "Allow GitHub Actions to create and approve pull requests" nas
configurações do repositório.

Limites do autopilot: nunca merge, nunca push em `main` nem force-push; para
após 3 falhas na mesma issue (`needs-human`) e se criar mais de 15 issues sem
fechar nenhuma.

## Context7 e Obsidian

Eles se complementam e não se duplicam: o **Context7** responde "o que a
biblioteca documenta hoje"; o **vault** guarda "o que aprendemos usando-a".

1. `dev:context7-mcp` lê antes as notas `tags: biblioteca` do vault (traz o
   `context7_id`, a versão e as armadilhas) e pula a resolução do ID.
2. Consulta o Context7 na versão do projeto.
3. Se a doc contradisse o esperado ou uma armadilha custou tempo, grava uma
   nota atômica via `knowledge:claude-obsidian` (sem copiar a doc).
4. `write-spec` e `implement` registram biblioteca, versão e ID na spec/PR.

## Manutenção

| Comando | Faz |
|---|---|
| `python3 scripts/validate.py` | Estrutura e frontmatter (o CI roda o mesmo + `claude plugin validate`) |
| `python3 scripts/audit.py` | Falhas de qualidade do catálogo: gatilho na description, API paga, tamanho, README, referências quebradas |
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
