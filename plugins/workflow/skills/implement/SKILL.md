---
name: implement
description: >-
  Implementa um ticket ou spec de ponta a ponta, sem supervisão: explora,
  escreve testes, codifica, roda as verificações do projeto, faz commit e
  abre PR. Use quando houver uma spec, um ticket ready-for-agent, um bug
  reproduzível ou o pedido "implementa", "toca o próximo ticket" ou "trabalha
  no backlog". Com "backlog" ou "--all", segue a fila de tickets
  desbloqueados até acabar.
---

# Implement

Você é um engenheiro autônomo. Seu objetivo é entregar um ticket **pronto
para merge**: CI verde, critérios de aceite comprovados e um PR que o
usuário aprove lendo só o relatório.

Processo: **carregar o contrato → explorar → teste que falha → implementar →
verificar → commit e PR → próximo ticket.**

Exemplo: `workflow:implement #42` → lê a issue 42 e a spec ligada a ela,
cria `feat/42-export-csv`, escreve `test_export_csv`, implementa, roda os
checks, abre o PR com o relatório do `verify`.

## 1. Carregar o contrato

- Ticket (issue ou `.scratch/<feature>/issues/NN-*.md`) e a spec que ele
  referencia (`.claude/specs/<slug>/spec.md`). Se a spec não existir nesta
  máquina (pasta ignorada pelo git), a issue é o contrato. Sem spec e sem
  critério claro → rode `workflow:write-spec` curta antes.
- `.claude/specs/<slug>/skills-plan.yaml`, se existir: invoque toda skill
  `required`, avalie o `trigger` das `conditional`, e marque o `status` de
  cada uma (`invoked`, `skipped-justified`, `unavailable`, `not-applicable`).
  Skill não usada nunca fica em silêncio: registre motivo e impacto no REQ.
  Skill nova descoberta no caminho vai em `discovered_during_implementation`.
- Comandos de verificação: `CLAUDE.md` do projeto; se não houver, CI e
  arquivos de build.
- Confira se os bloqueadores do ticket estão fechados. Se não estiverem,
  pegue outro ticket da fronteira.

## 2. Explorar

Subagente Explore para mapear onde a mudança entra e quais padrões seguir.
Leia você mesmo só os arquivos que vai editar.

## 3. Teste que falha

Escreva primeiro o teste que codifica o critério de aceite e confirme que
ele **falha pelo motivo certo**. Para bug, o teste reproduz o bug. Sem
infraestrutura de teste, defina o comando que demonstra o comportamento.

## 4. Implementar

- Mudança mínima que satisfaz os critérios. Nada fora do escopo do ticket.
- Siga os padrões do código ao redor (nomes, estrutura, densidade de
  comentários).
- Um commit por REQ (ou grupo coeso), só depois de o REQ passar: `git add`
  por nome de arquivo (nunca `-A`), leia `git diff` e desfaça hunks alheios.
  Nunca `--no-verify`; hook falhou → corrija e faça commit novo.
- Achou algo errado fora do escopo? Anote para o PR em vez de corrigir.
- Decisão não prevista na spec: se reversível, decida e registre como
  `Assumido:` no PR; se não, pare e pergunte.

## 5. Verificar

Rode `workflow:verify`. Se reprovar, corrija e rode de novo. Não abra PR com
verificação vermelha. Se travar três vezes no mesmo erro, pare, registre o
que tentou e peça ajuda.

## 6. Commit e PR

Siga o **Fluxo Git** do `CLAUDE.md` do projeto. O padrão do Lorenzo, quando o
projeto não disser nada diferente:

- branch `tipo/<n>-descricao` (ex.: `feat/12-export-csv`); se o ambiente
  impuser uma branch, use a do ambiente;
- Conventional Commits em inglês, no imperativo, um assunto por commit;
- PR no modelo `.github/pull_request_template.md`, com `Closes #N`, o
  **relatório do verify**, as decisões `Assumido:` e os itens anotados fora
  de escopo;
- marque os REQs como `[x]` (ou `[~]` parcial) na spec, some 1 em
  `revision_count` e acrescente no Log da entrevista o hash curto de cada
  REQ (`implement (<data>): REQ-2 → a1b2c3d`). Se `revision_count` >= 4 e
  ainda houver REQ aberto, pare e peça orientação em vez de repetir o ciclo
  com `verify`.
- Marque o ticket como em revisão (label `in-review`, se existir).

## 7. Próximo ticket

Em modo backlog, volte ao passo 1 com o próximo ticket desbloqueado. Antes,
avalie o contexto: se já estiver pesado, rode `workflow:handoff` e encerre;
a próxima sessão continua dali.
