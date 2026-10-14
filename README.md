# Skills

Minhas skills para o [Claude Code](https://claude.com/claude-code), versionadas
num só lugar e distribuídas como um **marketplace de plugins**. Em vez de copiar
pastas `.claude/skills/` entre projetos e máquinas, instalo daqui e atualizo
com um comando.

## Instalação

No Claude Code:

```
/plugin marketplace add LorenzoMarty/skills
/plugin install core@lorenzo-skills
```

Para receber as atualizações mais recentes:

```
/plugin marketplace update lorenzo-skills
```

As skills de um plugin aparecem com o prefixo do plugin, por exemplo
`core:grill-me`.

### Ativar automaticamente num projeto

Para que quem clonar um projeto (ou uma sessão na nuvem) já receba as skills,
adicione ao `.claude/settings.json` do projeto:

```json
{
  "extraKnownMarketplaces": {
    "lorenzo-skills": {
      "source": { "source": "github", "repo": "LorenzoMarty/skills" }
    }
  },
  "enabledPlugins": {
    "core@lorenzo-skills": true
  }
}
```

## Estrutura

```
.claude-plugin/marketplace.json   catálogo de plugins
plugins/
  core/                           um plugin = um grupo de skills
    .claude-plugin/plugin.json    nome, versão, descrição
    skills/
      <skill>/SKILL.md            uma pasta por skill (+ scripts, referências)
templates/skill/                  modelo para skills novas
scripts/                          import, scaffolding e validação
```

Agrupe skills em plugins por área (ex.: `planning`, `backend`, `frontend`,
`llmops`) para instalar só o que cada projeto precisa.

## Fluxo de trabalho

**Migrar skills que estão no computador**

```bash
git clone https://github.com/LorenzoMarty/skills.git && cd skills
scripts/import.sh ~/.claude/skills                # skills globais → core
scripts/import.sh ~/projetos/donc/.claude/skills  # skills de um projeto
scripts/import.sh ~/.claude/skills/minha-skill planning   # uma skill → outro plugin
```

O script copia as pastas, pula as que já existem (use `--force` para
sobrescrever) e roda a validação no fim. Depois de instalar o plugin e conferir
que tudo funciona, apague as cópias antigas em `.claude/skills/` para não ficar
com versões duplicadas.

**Criar**

```bash
scripts/new-plugin.sh planning "Planejamento, specs e tickets"
scripts/new-skill.sh grill-me planning
```

**Testar localmente antes do push**

```bash
claude --plugin-dir ./plugins/core
```

**Publicar**

1. `python3 scripts/validate.py`
2. Suba o `version` em `plugins/<plugin>/.claude-plugin/plugin.json`
3. Commit e push. O CI roda a mesma validação.

## Convenções

- Nome da skill em kebab-case, igual ao nome da pasta e ao `name` do
  frontmatter.
- A `description` diz **o que** a skill faz e **quando** usar; é ela que decide
  se a skill é acionada.
- Skills que só devem rodar quando chamadas explicitamente levam
  `disable-model-invocation: true` no frontmatter.
- Nada de chaves de API nos arquivos: leia de variáveis de ambiente.
- Skill adaptada de terceiros: cite a origem e a licença no topo do `SKILL.md`.
