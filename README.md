# Skills

Minhas skills para o [Claude Code](https://claude.com/claude-code), num só
repositório e distribuídas como **marketplace de plugins** (`lorenzo-skills`).
Valem para todos os projetos, local e na nuvem, e se encadeiam num fluxo que
vai da ideia ao PR verificado com o mínimo de revisão humana.

## O fluxo

```
ideia vaga ─► grill-me ─► write-spec ─► to-tickets ─► implement ─► verify ─► PR
                 ▲            ▲                           │            │
                 └──── start (roteador: escolhe a cadeia) ┘   handoff ◄┘ (contexto cheio)
```

- **`workflow:start`** classifica o pedido e escolhe a cadeia. Um hook de
  `SessionStart` lembra o Claude de usá-lo em toda sessão.
- **Modo autônomo por padrão:** decisões reversíveis são tomadas e registradas
  como `Assumido:`; só para quando a decisão é irreversível ou muda escopo.
- **Você revisa o relatório do `verify`**, não o diff linha a linha.
- **Economia de contexto:** exploração vai para subagentes, a spec guarda as
  decisões, um ticket por sessão, `handoff` antes de estourar.

## Plugins

| Plugin | Skills | Para quê |
|---|---|---|
| `workflow` | `start`, `grill-me`, `write-spec`, `to-tickets`, `implement`, `verify`, `handoff` | o fluxo de trabalho do dia a dia |
| `dev` | `context7-mcp` | documentação atual de bibliotecas (exige MCP do Context7) |
| `design` | `plan-screen`, `to-wireframe`, `img-to-html`, `extract-ds`, `to-img`, `openrouter-img`, `nano-banana-pro`, `fal-ai`, `mediabunny` | telas, wireframes, design systems, imagem e mídia (algumas usam APIs pagas) |

As skills aparecem com o prefixo do plugin: `/workflow:implement #42`.
Parte delas é fork de [rtadewald/skills](https://github.com/rtadewald/skills),
veja [UPSTREAM.md](UPSTREAM.md).

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
`.github/workflows/claude-agent.yml`. Preencha os comandos no `CLAUDE.md`: são
eles que o `verify` roda.

## Automação: o agente trabalhando sozinho

Com `claude-agent.yml` no projeto (requer o
[Claude GitHub App](https://github.com/apps/claude) e o secret
`CLAUDE_CODE_OAUTH_TOKEN`, gerado com `claude setup-token`):

1. Você escreve ou pede a spec (`workflow:write-spec`) e os tickets
   (`workflow:to-tickets`) → issues com a label `ready-for-agent`.
2. Cada issue com essa label dispara o agente, que roda `workflow:implement` e
   abre um PR com o relatório de verificação.
3. Você revisa o relatório e aprova; pede ajustes comentando `@claude` no PR.
4. Ticket que precisa de decisão sua volta com a label `needs-human`.

Numa sessão interativa, `workflow:implement backlog` faz o mesmo em sequência.

## Manutenção

```bash
scripts/import.sh ~/.claude/skills workflow   # trazer skills que estão no computador
scripts/new-plugin.sh backend "FastAPI, SQLAlchemy, Celery"
scripts/new-skill.sh fastapi-endpoint backend
python3 scripts/validate.py                   # o CI roda o mesmo + claude plugin validate
claude --plugin-dir ./plugins/workflow        # testar sem publicar
scripts/sync-upstream.sh                      # novidades no fork original
```

Convenções de escrita das skills: [CLAUDE.md](CLAUDE.md). Depois de importar
skills do computador, apague as cópias em `~/.claude/skills/` para não ter
versões duplicadas.
