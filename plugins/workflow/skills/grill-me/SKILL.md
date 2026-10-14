---
name: grill-me
description: >-
  Entrevista dura para afiar um plano ou design, rodada por rodada, até não
  sobrar decisão implícita. Use quando a ideia ainda é vaga, há várias
  decisões encadeadas em aberto, ou o usuário pedir "me questiona", "grill
  me" ou "vamos fechar esse plano". Termina entregando as decisões para
  write-spec.
---

Interview the user relentlessly until you reach a shared understanding. Map this as a **design tree**: every decision branches into the decisions that hang off it.

Work the tree in **rounds**. The **frontier** is every decision whose prerequisites are already settled: the questions you can ask _now_ without guessing at answers you haven't heard yet. Ask the whole frontier in one round: number each question and give your recommended answer. Then wait for the user's answers before the next round.

Each question should be formatted like so:

```
❓ **Q1** - **<question title>**: <question body, might be multiple paragraphs, including multiple choices>

➡️ <your recommended answer>
```

Each round the user answers reshapes the tree: settled decisions push the frontier outward and unblock questions that depended on them. Recompute the frontier and ask the next round. A question whose answer depends on another question still open in this round belongs to a _later_ round, not this one.

Finding _facts_ is your job, never the user's. When a frontier question needs a fact from the environment (filesystem, tools, etc.), dispatch a sub-agent to find it; don't ask the user for anything you could look up yourself. Don't block on it: a running exploration is an unsettled prerequisite, so only the questions downstream of it wait for the sub-agent to report; ask the rest of the frontier now. The _decisions_ are the user's: put each to them and wait.

The session is done when the frontier is empty: every branch of the design tree visited, nothing left silently assumed. Do not act on it until the user confirms you have reached a shared understanding.


## Próximo passo

Quando o usuário confirmar o entendimento comum, invoque `workflow:write-spec`
passando a árvore de decisões resolvida. Não comece a implementar a partir
da conversa: a spec é o que sobrevive à sessão.

Em modo autônomo (o usuário não está acompanhando), não rode esta entrevista:
vá direto para `workflow:write-spec` e registre as respostas recomendadas
como `Assumido:`.
