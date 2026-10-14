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

Exemplo de critério ruim e bom:

- ruim: "o export deve ser rápido"
- bom: "`GET /reports/stock.csv` com 10k itens responde em < 2 s no teste
  `test_export_large`"

## 1. Reunir contexto

Use o que já está na conversa (inclusive a saída de `grill-me`). Se o usuário
passar uma issue ou arquivo, leia o corpo e os comentários.

## 2. Explorar o código

Delegue a um subagente Explore: módulos afetados, padrões existentes que a
solução deve seguir, testes próximos e comandos de verificação do projeto.
Peça só a conclusão com caminhos de arquivo.

## 3. Redigir

Use o modelo em [references/spec-template.md](references/spec-template.md).
Regras:

- Critérios de aceite **observáveis**: cada um vira um teste ou um comando
  com saída esperada.
- Decisões que você tomou sozinho entram como `Assumido:` com o motivo.
  Perguntas que só o usuário responde entram em **Em aberto**, cada uma com a
  resposta que você recomenda.
- Sem caminhos de arquivo ou trechos de código no corpo, exceto quando
  codificam uma decisão (schema, tipo, máquina de estados).
- Curta. Se passar de ~1 página, o trabalho provavelmente precisa ser
  quebrado em tickets.

## 4. Salvar

Salve em `docs/specs/<AAAA-MM-DD>-<slug>.md` no projeto (crie a pasta se não
existir) e faça commit junto com o primeiro código, ou sozinho se o trabalho
for continuar em outra sessão.

## Próximo passo

- Itens em **Em aberto** que bloqueiam → pergunte agora, agrupados, e
  aguarde.
- Cabe numa sessão → `workflow:implement` com esta spec.
- Não cabe → `workflow:to-tickets` com esta spec.
