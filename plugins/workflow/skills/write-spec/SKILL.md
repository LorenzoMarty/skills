---
name: write-spec
description: >-
  Escreve a spec de uma feature, refactor ou correção grande: objetivo,
  fora de escopo, decisões, critérios de aceite testáveis e como verificar.
  Use depois de grill-me, quando o objetivo já está claro, ou sempre que um
  trabalho for ser executado por um agente sem supervisão. A spec é o
  contrato que implement e verify seguem.
---

# Write Spec

Você é quem transforma intenção em **contrato executável**. Uma boa spec
permite que um agente implemente sem perguntar nada e que outro verifique
sem ler a conversa.

Processo: **reunir contexto → explorar o código → redigir → checar
testabilidade → salvar → apontar o próximo passo.**

Exemplo de requisito ruim e bom:

- ruim: "o export deve ser rápido"
- bom: "REQ-1: `GET /reports/stock.csv` com 10k itens responde em < 2 s
  no teste `test_export_large`"

## 1. Reunir contexto

Use o que já está na conversa (inclusive a saída de `grill-me`, que vai para
o **Log da entrevista**). Se o usuário passar uma issue ou arquivo, leia o
corpo e os comentários.

## 1.5. Reaproveitar contexto

Antes de explorar, rode `knowledge:knowledge-manager` sobre a área do pedido
(custo ~0) e leia o que ele apontar no Obsidian (hub, `Arquitetura.md`,
`Decisões.md`). Não pergunte ao usuário o que já está registrado; decisão
anterior que conflite com o pedido vira item em **Em aberto**.

## 2. Explorar o código

Delegue a um subagente Explore: módulos afetados, padrões existentes que a
solução deve seguir, testes próximos e comandos de verificação do projeto.
Peça só a conclusão com caminhos de arquivo.

## 3. Redigir

Use o modelo em [references/spec-template.md](references/spec-template.md).
Regras:

- Requisitos numerados `REQ-N` e **observáveis**: cada um vira um teste ou
  um comando com saída esperada. Commits, PR e verificação citam o REQ.
- Decisões que você tomou sozinho entram como `Assumido:` com o motivo.
  Perguntas que só o usuário responde entram em **Em aberto**, cada uma com a
  resposta que você recomenda.
- Sem caminhos de arquivo ou trechos de código no corpo, exceto quando
  codificam uma decisão (schema, tipo, máquina de estados).
- Curta. Se passar de ~1 página, o trabalho provavelmente precisa ser
  quebrado em tickets.

## 4. Salvar

Salve em `.claude/specs/<slug>/spec.md` (o padrão dos projetos do Lorenzo),
salvo se o `CLAUDE.md` do projeto indicar outro lugar. A cada revisão, some 1
em `revision_count`.

Confira se `.claude/specs/` está no `.gitignore`:

- **Versionada** → commit junto com o primeiro código.
- **Ignorada** (spec só local) → a spec não chega a outras sessões nem à
  GitHub Action. Copie Objetivo, Requisitos e Critérios de concluído para o
  corpo da issue; a issue passa a ser o contrato para quem trabalhar fora
  desta máquina.

## Próximo passo

1. **Em aberto** que bloqueia → pergunte agora, agrupado, e aguarde. Ideia
   ainda vaga → `workflow:grill-me` antes de redigir.
2. Spec salva com `status: ready` → `workflow:spec-router` (grava
   `skills-plan.yaml` ao lado da spec; `implement` e `verify` o consomem).
3. Cabe numa sessão → `workflow:implement`. Não cabe → `workflow:to-tickets`.
4. Decisão arquitetural (ADR-worthy) → avise e registre com
   `knowledge:claude-obsidian` (`/decisao`).
