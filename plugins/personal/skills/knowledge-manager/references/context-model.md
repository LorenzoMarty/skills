# Modelo de dados: Contexto

Um arquivo Markdown por contexto: `.claude/knowledge/contexts/ctx-<slug>.md`. Humanamente auditável — o usuário pode abrir e editar na mão se quiser corrigir algo.

## Schema (frontmatter + corpo)

```markdown
---
id: ctx-<slug>
concepts: [conceito-1, conceito-2]
origin: task:AAAA-MM-DD-descricao-curta
confidence: 0.0
created: AAAA-MM-DD
updated: AAAA-MM-DD
last_verified: AAAA-MM-DD
files:
  - caminho/relativo/arquivo1.tsx
  - caminho/relativo/arquivo2.ts
docs:
  - "pasta no vault/Nome do Doc.md"
graph_nodes: []
depends_on: []
ttl_days: 60
---

Resumo curto (3-5 linhas): o que esta parte do código faz, decisões de
implementação relevantes, armadilhas conhecidas. NÃO é documentação completa —
só o suficiente pra não precisar reabrir o código na próxima tarefa parecida.
```

Campos:

- `id`: slug estável, vira o nome do arquivo.
- `concepts`: quais conceitos este contexto satisfaz (referência cruzada com `concepts.json`).
- `origin`: de onde veio (qual tarefa gerou este contexto pela primeira vez). Ajuda auditoria.
- `confidence`: mesma escala do conceito. Contexto herda a confidence mínima entre suas fontes.
- `files`: arquivos de código relevantes. Usado pra invalidação por `mtime` (ver `invalidation-policy.md`).
- `docs`: caminho relativo dentro do vault (não conteúdo, só caminho — se precisar do conteúdo, abre na hora).
- `depends_on`: outros `ctx-*` dos quais este depende (ex.: uma tela de listagem depende do contexto do client de API). Invalidação propaga como decay, não cascata total.
- `ttl_days`: quantos dias sem uso antes de considerar revalidação obrigatória na próxima vez que for tocado (não é expiração automática — é lazy, só verifica quando for usado de novo).

## Regras de escrita

- Corpo do contexto: 3-5 linhas. Se está crescendo além disso, provavelmente devia virar documentação de verdade no vault (avaliar critério em `obsidian-integration.md`) em vez de inchar o cache.
- Todo contexto novo ou atualizado grava `updated` e, se foi confirmado por uma fonte forte (código lido diretamente), atualiza `last_verified`.
- Contexto nunca é deletado — vai para `contexts/_archive/ctx-<slug>.md` quando invalidado, preservando `origin` e histórico para auditoria.
