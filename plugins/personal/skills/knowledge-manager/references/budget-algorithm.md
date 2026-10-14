# Algoritmo de budget (escolha da estratégia mais barata)

Antes de qualquer busca, perguntar internamente: "existe forma mais barata de descobrir isso?" — e responder com a tabela abaixo, não com achismo.

## Tabela de custo relativo

| Nível | Fonte | Custo relativo |
|---|---|---|
| 1 | Cache semântico (`concepts.json` + `context.md` específico) | ~0 |
| 2 | Headroom retrieve | baixo |
| 3 | Índice do Obsidian (`obsidian-index.json`) | baixo-médio |
| 4 | Doc específico do vault (conteúdo real) | médio |
| 5 | Código (Read/Grep pontual) | alto |
| 6 | Código (varredura ampla, múltiplos arquivos) | mais alto |

## Regra de decisão

1. Nunca pular nível sem que o nível anterior tenha sido de fato consultado e não tenha resposta suficiente.
2. "Resposta suficiente" = confidence do que foi encontrado é compatível com o risco da tarefa (ex.: renomear variável local tolera confidence baixa; mudar contrato de API pública exige verificar na fonte mesmo com cache hit de alta confidence).
3. Se dois níveis podem responder a mesma pergunta, escolher o mais barato mesmo que o mais caro seja "mais completo" — completude extra não usada é desperdício de tokens.
4. Registrar em `metadata/tool-usage-log.jsonl` qual nível respondeu, sempre (mesmo quando foi nível 1) — é o dado bruto do relatório de economia.

## Formato do log (`tool-usage-log.jsonl`, append-only)

```json
{"ts": "AAAA-MM-DDThh:mm:ss", "task": "descrição curta", "concept": "slug-ou-null", "level_resolved": 1, "level_name": "cache-semantico"}
```

## Relatório "quanto contexto economizamos"

Ao ser pedido, ler todo `tool-usage-log.jsonl` (arquivo pequeno, append-only, custo baixo) e agregar:
- % de resoluções por nível de custo.
- Taxa de reuso (nível 1) ao longo do tempo — deve subir conforme o cache amadurece.
- Combinar com `headroom_stats` (ver `headroom-integration.md`) pra cobrir também a economia de sessão.

Se a taxa de nível 1 estiver caindo (ou nunca subindo) pra um projeto que já tem uso, é sinal de que o matching léxico (`concept-model.md`) está fraco pra esse domínio — considerar ampliar `aliases` antes de qualquer mudança de arquitetura.
