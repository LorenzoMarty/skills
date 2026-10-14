# Integração com Headroom

Headroom é MCP (`mcp__headroom__*`), responsável apenas pelo contexto da **sessão atual**. Nunca armazenar conhecimento permanente nele — isso é papel do cache semântico desta skill.

## Ferramentas (carregar via ToolSearch antes de usar, se ainda deferred)

`select:mcp__headroom__headroom_compress,mcp__headroom__headroom_retrieve,mcp__headroom__headroom_stats`

## Quando usar

- **Retrieve**: nível 2 da cascata (`search-order.md`) — antes de ir pro índice do Obsidian, checar se a sessão atual (ou recente, se o Headroom mantiver histórico) já tem a resposta processada.
- **Compress**: quando a própria skill gerar bastante contexto intermediário durante a resolução de uma tarefa (ex.: várias buscas de código) que vale comprimir antes de seguir, mas que ainder não é "concept-worthy" o bastante pra virar contexto permanente.
- **Stats**: usado no relatório "quanto contexto economizamos" (junto com `tool-usage-log.jsonl`), pra mostrar economia também no nível de sessão, não só de cache permanente.

## Ponte Headroom -> cache semântico

Se o Headroom retornar algo útil que se repete entre sessões (não é fato de uma tarefa isolada, é um conceito/padrão reutilizável), promover pro cache permanente: criar/atualizar `concept` + `context.md`. Esse é o único jeito de "vazamento" controlado de sessão pra memória permanente — sem isso, Headroom nunca vira conhecimento persistido, e a skill reaprenderia a cada nova sessão.

## O que nunca fazer

- Nunca tratar retorno do Headroom como permanente sem promovê-lo explicitamente pro cache (arquivo `contexts/ctx-*.md`).
- Nunca gravar dado de sessão (ex.: estado temporário de uma tarefa em andamento) dentro de `concepts.json`/`contexts/` — isso polui o cache permanente com lixo de curto prazo.
