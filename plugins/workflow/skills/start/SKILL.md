---
name: start
description: >-
  Roteador do fluxo de trabalho. Use no início de QUALQUER tarefa que não seja
  trivial (feature, bug com causa desconhecida, refactor, tela nova, ideia
  vaga) para decidir qual skill vem a seguir e em que modo trabalhar. Também
  use quando não souber qual skill aplicar, ou quando o usuário disser
  "começa", "toca isso", "trabalha sozinho" ou "modo autônomo".
---

# Start

Você é o **roteador** do fluxo de trabalho do Lorenzo. Seu objetivo é levar
cada pedido pelo caminho mais curto até uma entrega **verificada**, com o
mínimo de revisão humana e o mínimo de tokens gastos.

Processo: **classificar o pedido → escolher o modo → seguir a cadeia de
skills → fechar com evidência.**

Exemplo:

> "Quero exportar o relatório do Estoque em CSV."
> → feature pequena, critérios claros → `workflow:write-spec` (curta) →
> `workflow:implement` → `workflow:verify` → PR.

## 0. Contexto primeiro

Se o projeto tem `.claude/knowledge/`, rode `knowledge:knowledge-manager`
**antes** de ler código ou docs (regra 1 da Política de Trabalho). Se não
tem e a tarefa não é trivial, rode o bootstrap dele (custo ~0).

## 1. Classificar o pedido

| Pedido | Cadeia |
|---|---|
| Ideia vaga, várias decisões em aberto | `grill-me` → `write-spec` → `to-tickets` → `implement` (por ticket) |
| Feature com objetivo claro | `write-spec` → `to-tickets` (se > 1 sessão de trabalho) → `implement` |
| Bug | reproduzir → `implement` (o teste que falha é a spec) → `verify` |
| Mudança pequena e óbvia (< ~30 linhas, sem decisão) | fazer direto → `verify` |
| Tela ou fluxo novo | `design:plan-screen` → `write-spec` → `implement` |
| Mock/imagem → HTML | `design:img-to-html` |
| Extrair design system de um site | `design:extract-ds` |
| Dúvida sobre API de biblioteca | `dev:context7-mcp` antes de escrever código |
| "Toca tudo", backlog inteiro, modo contínuo | `autopilot` (push, PR, review e novas issues sem parar; só o merge é seu) |
| Decisão, bug ou dívida fora de escopo | `file-issue` |
| Contexto acabando ou fim de sessão | `handoff` |

Os nomes sem prefixo são do plugin `workflow` (ex.: `workflow:implement`);
as de outros plugins levam o prefixo (`design:`, `dev:`, `knowledge:`).
Invoque cada skill pela ferramenta Skill quando chegar a vez dela. Não
reproduza as instruções de uma skill dentro de outra.

## 2. Escolher o modo

- **Autônomo (padrão)**: o usuário não está acompanhando. Decida sozinho tudo
  o que for reversível e esteja dentro do escopo, registrando cada decisão
  como `Assumido:` na spec ou no PR. Só pare para perguntar quando a decisão
  for irreversível, mudar escopo ou contrato público (API, schema, preço,
  segurança) **e** não houver padrão razoável.
- **Interativo**: o usuário pediu para ser consultado, ou a ideia ainda não
  tem objetivo. Use `grill-me`.

Na dúvida entre os dois: trabalhe no autônomo e deixe as perguntas
agrupadas no fim, com a resposta que você assumiu para cada uma.

## 3. Regras de contexto (economia de tokens)

1. **Delegue exploração.** Varreduras amplas ("onde está X", "como funciona
   Y") vão para um subagente Explore; você recebe só a conclusão.
2. **Leia trechos, não arquivos inteiros**, quando já souber onde olhar.
   Nunca releia um arquivo que acabou de editar.
3. **A spec é a memória.** Decisões vão para o arquivo da spec ou do ticket,
   não ficam só na conversa. Uma sessão nova deve conseguir continuar lendo
   apenas a spec e o ticket.
4. **Um ticket por contexto.** Se o trabalho não cabe numa sessão, ele
   precisa de `to-tickets`.
5. **Saída curta.** Não narre cada passo; reporte resultado, evidência e
   pendências.
6. **Pare antes de estourar.** Quando o contexto estiver perto do limite ou o
   trabalho mudar de assunto, rode `handoff` em vez de continuar degradando.

## 4. Fechar com evidência

Nenhuma entrega termina sem `workflow:verify`. O usuário revisa o
**relatório de verificação**, não o diff linha a linha. Por isso o relatório
precisa mostrar comandos rodados, saídas relevantes, critérios atendidos e
o que ficou de fora.

## Skills de apoio

A cadeia se liga a estas skills:

| Momento | Skill |
|---|---|
| Antes de explorar | `knowledge:knowledge-manager` |
| Spec salva | `workflow:spec-router` (grava `skills-plan.yaml`; `write-spec` chama) |
| Diff grande ou área sensível | `workflow:quality-gate` (dentro do `verify`) |
| Spec `done`, PR e issues | `workflow:ship-spec` (push e PR autorizados; merge nunca) |
| Qualquer issue nova | `workflow:file-issue` |
| Doc de biblioteca | `dev:context7-mcp` (consulta o vault antes, grava o que for não óbvio) |
| Tarefa concluída, não trivial | `knowledge:claude-obsidian` (registro) ou `/decisao` |
| Ver specs paradas | `workflow:specs-status` |

## Um fluxo só

```
grill-me ─► write-spec ─► spec-router ─► [to-tickets] ─► implement ─► verify ─► ship-spec
(se vago)                                                     ▲            │
                                                              └─ correções ┘
```

- `grill-me`: só quando a ideia é vaga e o usuário está presente (decide).
- `write-spec`: salva `.claude/specs/<slug>/spec.md` com `REQ-N` (especifica).
- `implement`: executa por ticket ou spec, commit por REQ.
- `verify`: confere cada REQ em runtime, fecha a spec (`done` ou
  `needs-changes`, que volta ao `implement`).
- `ship-spec`/`autopilot`: push, PR com assignee, review e issues novas;
  **você só aprova o merge**.

Não existem mais `spec-interview`, `implement-spec` e `review-spec`: o
trabalho deles é do `write-spec`, `implement` e `verify`.

## Contrato com o projeto

Se o projeto tiver `CLAUDE.md`, ele manda nos comandos (lint, testes,
typecheck) e nas convenções. Se não tiver, descubra os comandos uma vez
(package.json, pyproject, Makefile, CI) e sugira ao fim criar o `CLAUDE.md` a
partir de `templates/project/CLAUDE.md` do repositório LorenzoMarty/skills.
