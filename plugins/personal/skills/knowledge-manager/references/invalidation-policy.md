# Política de invalidação

Automática. Nunca pergunta ao usuário, nunca reconstrói tudo — só o que foi afetado, e de forma lazy (na próxima vez que aquele contexto for relevante, não em um job de "revalidar tudo agora").

## Triggers

**1. Arquivo referenciado mudou**
Para cada `files` de um contexto, comparar `mtime` atual contra `last_verified` do contexto. Se algum arquivo foi modificado depois de `last_verified`: `confidence *= 0.5`. Checagem é feita só quando o contexto é carregado (nível 1 da cascata), não em background.

**2. Confidence abaixo do limiar mínimo (0.3)**
Mover o arquivo de `contexts/ctx-<slug>.md` para `contexts/_archive/ctx-<slug>.md`. Remover a referência de `contexts` no(s) conceito(s) associado(s) em `concepts.json` (o conceito em si permanece, só perde este contexto). Registrar em `metadata/tool-usage-log.jsonl` a arquivação.

**3. Dependência invalidada (`depends_on`)**
Se `ctx-A` depende de `ctx-B` e `ctx-B` foi invalidado/arquivado: aplicar decay parcial em `ctx-A` (`confidence *= 0.75`, mais leve que invalidação direta), não arquivar automaticamente. `ctx-A` só é revisado quando usado de novo.

## Revalidação

Lazy: quando um contexto stale (confidence baixa mas ainda ativo) é carregado pra uma tarefa, a skill deve tratar ele como "hipótese, não fato" — usar mas verificar rapidamente contra a fonte mais barata disponível (ver `search-order.md`) antes de confiar 100%. Se confirmado, `confidence` sobe de volta e `last_verified` atualiza. Se contradito, atualizar o contexto com o novo achado (mesmo arquivo, não cria duplicado).

## O que nunca fazer

- Nunca apagar contexto ou conceito permanentemente — sempre arquivar.
- Nunca invalidar por invalidar "pra garantir" — só nos 3 triggers acima.
