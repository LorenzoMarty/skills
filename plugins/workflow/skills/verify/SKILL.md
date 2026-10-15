---
name: verify
description: >-
  Verifica uma mudança com evidência antes de entregá-la: roda lint,
  typecheck e testes, confere cada critério de aceite da spec, relê o diff
  de forma adversarial e produz um relatório curto. Use antes de todo commit
  final, PR ou "pronto", e quando o usuário perguntar se algo está
  funcionando.
---

# Verify

Você é o revisor cético. Seu objetivo é que o usuário possa confiar na
entrega **lendo só o seu relatório**. Afirmação sem evidência não entra.

Processo: **checks automáticos → requisitos → leitura adversarial
do diff → relatório.**

Exemplo de linha do relatório:

> ✅ REQ-1 Export com 10k itens < 2 s — `pytest tests/test_export.py::test_large`
> passou (1,4 s)

## 1. Checks automáticos

Rode os comandos do `CLAUDE.md` do projeto (ou do CI): lint, format,
typecheck, testes dos pacotes alterados. Guarde só o resumo de cada saída.
Falhou → volte para quem chamou com o erro; não maquie.

## 2. Requisitos e critérios de concluído

Para cada `REQ-N` e cada critério de concluído da spec ou do ticket, aponte
a evidência **em runtime** (ler o código não confirma comportamento observável): teste que passou, comando e saída, ou captura do app rodando (skill `run`, se
disponível). Critério sem evidência fica ❌ ou ⚠️, nunca ✅.

## 3. Leitura adversarial do diff

Leia `git diff` da base até aqui procurando:

- o que faria o CI ou um revisor rejeitar;
- casos de borda dos critérios (vazio, nulo, limite, concorrência);
- segredos, logs de debug, código morto, arquivos sem relação;
- mudanças fora do escopo do ticket.

Corrija o que for seu e rode os checks de novo. Para mudanças grandes,
delegue esta leitura a um subagente com o diff e a spec, e trate o que ele
achar como hipótese a confirmar.

## 3.5. Escopo, plano de skills e qualidade

- Liste à parte o que foi construído e **não** está na spec (scope creep):
  não reprova sozinho, mas o usuário precisa saber.
- Se existir `skills-plan.yaml`: skill `required` (ou `conditional` cujo
  gatilho disparou) não invocada e sem justificativa é achado; se o REQ que
  ela cobria falhou, diga o vínculo. `optional` nunca gera achado.
- Diff grande ou em área sensível (auth, pagamento, permissão) →
  `workflow:quality-gate` além da leitura acima.

## 3.6. Fechar a spec

- Tudo ✅ → `status: done` na spec e `outcome.status` no `skills-plan.yaml`.
  Tarefa não trivial → sugira `knowledge:claude-obsidian` (sem encadear) e
  siga para `workflow:ship-spec`. Achado fora de escopo → `workflow:file-issue`.
- Algum ❌ → escreva "Correções pendentes" na spec (arquivo, o que está
  errado, evidência, o que deve acontecer; específico o bastante para o
  `implement` agir sem perguntar), `status: needs-changes` e volte para
  `workflow:implement`. Se `revision_count` >= 4, pare e peça orientação em vez
  de repetir o ciclo. Se uma skill do plano não invocada causou a falha, a
  correção manda invocá-la explicitamente.
- Skill do plano `experimental` ou `verified` (sem histórico): registre em
  `evaluation` do `skills-plan.yaml` `useful`, `requirement_coverage`, `issues`
  e `future_confidence`; o `spec-router` usa isso como `historical_evidence`.

## 4. Relatório

```markdown
## Verificação
- Checks: lint ✅ · typecheck ✅ · testes ✅ (`<comando>`, N passaram)
- ✅ REQ-1 <resumo> — <evidência>
- ⚠️ REQ-2 <resumo> — <o que falta e por quê>
- Assumido: <decisão> — <motivo>
- Fora de escopo, para depois: <item>
```

Esse bloco vai no PR e na resposta final. Nada além disso precisa ser
narrado.

## Próximo passo

Tudo ✅ → `workflow:ship-spec` (PR e issues, sem esperar aprovação; só o merge é seu). Algum ❌ →
`workflow:implement` com as "Correções pendentes" da spec.
