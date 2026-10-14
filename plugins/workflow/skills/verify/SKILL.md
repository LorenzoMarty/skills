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
a evidência: teste que passou, comando e saída, ou captura do app rodando (skill `run`, se
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
  `personal:quality-gate` além da leitura acima.

## 3.6. Fechar a spec

- Tudo ✅ → `status: done` na spec e `outcome.status` no `skills-plan.yaml`.
  Tarefa não trivial → sugira `personal:claude-obsidian` (sem encadear) e
  ofereça `personal:ship-spec` numa linha (push só com pedido explícito).
- Algum ❌ → escreva "Correções pendentes" na spec (arquivo, o que está
  errado, o que deve acontecer), `status: needs-changes` e volte para
  `workflow:implement`. Se uma skill do plano não invocada causou a falha, a
  correção manda invocá-la explicitamente.

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
