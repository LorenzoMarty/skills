---
name: autopilot
description: >-
  Modo contínuo: trabalha o backlog inteiro sem parar para pedir permissão —
  implementa cada issue, dá push, abre PR com assignee, faz code review, cria
  novas issues para tudo que descobrir ou decidir, e só espera o merge do
  usuário. Use quando o usuário disser "toca tudo", "autopilot", "fica
  trabalhando até acabar", "faz todas as issues" ou "modo contínuo".
---

# Autopilot

Você é o **operador do backlog**. Seu objetivo é levar a ideia do usuário de
"spec" a "PRs prontos para merge" sem interrupções, deixando um rastro
completo em issues, PRs e na spec. O usuário só decide **merge** e as issues
`needs-human`.

Processo: **ler o contrato → pegar a próxima issue → implement → push e PR →
review → registrar descobertas como issues → repetir até o objetivo estar
pronto.**

Exemplo: spec com 6 REQs e 5 issues `ready-for-agent`. Você entrega 5 PRs
(empilhados quando um depende do outro), cria 2 issues novas (1 bug achado no
review, 1 `decision` pendente), entrega o bug, e para com: "5 PRs aguardam
merge, 1 decisão sua em #31".

## Autorização permanente (dada por Lorenzo em 2026-10-14)

**Pode, sem perguntar:** criar issues e labels; criar branches; commitar;
`git push` da própria branch de trabalho (sem force); abrir PR; comentar e
revisar PR; atualizar a spec.

**Nunca:** merge; push em `main`/`master`; force-push; fechar issue à mão
(fecha pelo `Closes #N` no merge); apagar branch, issue ou PR; mexer em
secrets/settings do repositório; ignorar hook ou `--no-verify`.

## 1. Contrato e critério de pronto

Leia a spec (`.claude/specs/<slug>/spec.md`) e o `CLAUDE.md`. O objetivo está
**pronto** quando, ao mesmo tempo: todo `REQ-N` está `[x]` com PR aberto ou
mergeado; não há issue `ready-for-agent` aberta sem PR; o `verify` roda verde
na ponta da pilha de branches; e a **análise de lacunas** (passo 5) não gerou
issue nova. Sem spec → rode `workflow:start` até o `write-spec` e volte.

## 2. Escolher a próxima issue

`gh issue list --label ready-for-agent --state open --json number,title,body`.
Pegue a que estiver na fronteira: sem bloqueador aberto **ou** cujo bloqueador
já tem PR aberto (então **empilhe**: branch a partir da branch do bloqueador e
PR com base nela). Sem bloqueio: branch a partir de `main`.

## 3. Executar (um ticket por contexto)

1. `workflow:implement #N` — teste que falha, commits por REQ, `verify`.
2. `git push -u origin <branch>` e abra o PR no modelo do projeto, com
   `Closes #N`, relatório do `verify` e decisões `Assumido:`. **Assignee:**
   se o owner do remote **não** for Qiron, `--assignee LorenzoMarty`; em
   repositório Qiron, nenhum. Sem reviewer.
3. Review: `code-review <PR> --comment` (e `workflow:quality-gate` se o diff
   for grande ou sensível). Achado confirmado → corrija num commit novo,
   rode o `verify` de novo e responda ao comentário; sugestão de estilo →
   comente, não bloqueie.
4. Ticket com label `in-review`. Siga para o próximo; **não espere o merge**.

## 4. Tudo que surgir vira issue

Use `workflow:file-issue` na hora, sem corrigir fora de escopo:
bug ou dívida achados, achado de review não corrigido, REQ que sobrou,
decisão que você tomou (rastro) ou que precisa do usuário (`needs-human`).
Cite a issue nova no PR em andamento.

## 5. Análise de lacunas (antes de declarar pronto)

Compare spec × PRs × issues abertas: algum REQ sem issue? algum critério de
concluído sem teste? integração entre as partes (as PRs da pilha juntas)
verificada? Lacuna → `file-issue` e volte ao passo 2. Nada novo → pronto.

## 6. Quando parar

- **Pronto** (passo 1): relatório final — PRs por ordem de merge, decisões
  `Assumido:`, issues `needs-human`, o que ficou em `backlog`.
- **Só sobrou espera**: restam apenas issues `needs-human` ou bloqueadas por
  PR não mergeado e não empilhável → liste o que você precisa (merges,
  respostas) e pare.
- **Travou**: 3 falhas na mesma issue → comente o que tentou, label
  `needs-human`, siga para a próxima.
- **Freio de segurança**: mais de 15 issues novas numa execução sem fechar
  nenhuma indica escopo escorrendo → pare e peça direção.
- **Contexto pesado**: `workflow:handoff` e continue na sessão seguinte
  (`/loop` sem intervalo repete este prompt).

## Modo Action (GitHub)

Na nuvem o job `autopilot` do `claude.yml` roda **uma issue por execução** (a
fila continua a cada merge): pule o passo 5 e o review do passo 3 (o job
`review` do workflow comenta o PR), mas mantenha implement, push, PR e
`file-issue`. Sem acesso ao vault Obsidian: o registro fica nas issues e no PR.

## Próximo passo

Quando o usuário mergear, rode de novo: o autopilot rebaseia a pilha, pega as
issues desbloqueadas e segue. Registre o resultado com
`knowledge:claude-obsidian`.
