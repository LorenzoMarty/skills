---
name: file-issue
description: >-
  Cria uma issue robusta (GitHub, ou Jira em projetos da Qiron): deduplica,
  classifica o tipo, exige critério de aceite observável, liga origem e
  bloqueios, aplica labels e assignee. Use sempre que uma decisão for tomada
  ou precisar ser tomada, um bug ou dívida aparecer fora do escopo, uma
  spec sobrar REQ, ou o usuário pedir "cria uma issue", "anota isso",
  "registra para depois". É a única porta de entrada de issues do fluxo.
---

# File Issue

Você é o **triador**. Seu objetivo é que toda issue criada possa ser pega por
um agente sem fazer nenhuma pergunta, e que nenhuma decisão fique só na
conversa.

Processo: **detectar tracker → deduplicar → classificar → redigir → checar
qualidade → criar e ligar → devolver o número.**

Exemplo: durante o `implement #12` você nota que o export não trata fuso
horário e que o formato de data é uma escolha de produto → duas issues: um
`bug` (`ready-for-agent`) e uma `decision` (`needs-human`, com a opção
recomendada).

## 1. Tracker

`git remote get-url origin`: owner `Qiron-Robotics` → **Jira** (projeto `BAC`,
salvo indicação da spec/branch; ver `ship-spec` para as chamadas do MCP).
Qualquer outro → **GitHub Issues** (`gh`). Ambíguo → decida pelo `CLAUDE.md`;
sem pista, GitHub e registre `Assumido:`. Garanta as labels (`gh label create
... || true`): `ready-for-agent`, `needs-human`, `in-review`, `decision`, `bug`,
`debt`, `feature`, `backlog`.

## 2. Deduplicar (obrigatório)

`gh issue list --state all --search "<2-3 palavras-chave>" --limit 10`. Achou
issue aberta que cobre → **comente** nela (nova evidência, link do PR) em vez
de criar. Fechada recentemente por mudança que não resolveu → crie e cite a
anterior. Nunca crie duas issues para o mesmo problema.

## 3. Classificar

| Tipo | Quando | Label de estado |
|---|---|---|
| `feature` | REQ a construir ou sobra de spec | `ready-for-agent` |
| `bug` | comportamento errado, com como reproduzir | `ready-for-agent` |
| `debt` | refactor, cobertura, dependência, achado de review não corrigido | `ready-for-agent` se pequeno, senão `backlog` |
| `decision` **tomada** | você escolheu algo reversível e o `Assumido:` merece rastro | sem label de estado; issue aberta para o usuário contestar |
| `decision` **pendente** | irreversível, muda contrato/escopo, ou exige negócio | `needs-human` |

Só vira `ready-for-agent` o que serve ao objetivo da spec corrente. Ideia
interessante fora disso → `backlog` (o autopilot não pega).

## 4. Redigir

Título imperativo, até ~72 caracteres, no vocabulário do domínio. Corpo:

```markdown
## Origem
<spec/REQ, PR, commit ou conversa que gerou isto> · Parent: #N (se houver)

## Contexto
<por que existe; o que foi observado, com evidência (saída, log, link)>

## O que entregar
<comportamento observável, não lista de arquivos>

## Critérios de aceite
- [ ] <observável> — verificado por `<comando ou teste>`

## Fora de escopo
- <o que parece incluído e não é>

## Blocked by
- #N ou "Nenhum"

## Tamanho
S | M | L (cabe numa sessão? se não, quebre)
```

`decision` troca "O que entregar" por **Opções** (2-3, com custo/risco de
cada), **Recomendação** (e a escolha tomada, se já tomada), **Impacto** e
**Como reverter**.

## 5. Checar qualidade antes de criar

- ≥ 1 critério de aceite que um comando ou teste comprova.
- Origem rastreável (nada de "conforme conversado").
- Sem caminhos de arquivo ou trechos de código, salvo se codificam uma decisão.
- `Tamanho` L → quebre em várias issues; não crie uma gigante.
- Sem segredo, token ou dado de cliente no corpo.

## 6. Criar e ligar

`gh issue create --title ... --body-file ... --label ... --assignee
LorenzoMarty` (repo da Qiron: Jira, sem assignee extra). Bloqueios: use a
relação nativa se existir, senão `Blocked by #N` no corpo e comente na issue
bloqueadora. Devolva `#N` e a URL para quem chamou colocar no PR e na spec.

## Regras

- Criar issue é autorizado em definitivo pelo Lorenzo (2026-10-14); não peça
  aprovação. Não feche, edite nem remova issues de outras pessoas.
- Nunca use `needs-human` para fugir de trabalho: só com a pergunta e a
  resposta recomendada escritas.

## Próximo passo

Volte a quem chamou (`workflow:autopilot`, `implement`, `to-tickets`, `verify`)
com o número da issue. Issue `ready-for-agent` vira trabalho do
`workflow:autopilot`.
