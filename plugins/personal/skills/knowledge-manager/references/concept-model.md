# Modelo de dados: Conceito

Arquivo único por projeto: `.claude/knowledge/index/concepts.json`. É o hot path — precisa ficar leve (só ponteiros, nunca conteúdo pesado). Detalhe pesado vive nos arquivos de contexto (`context-model.md`).

## Schema

```json
{
  "version": 1,
  "concepts": {
    "<slug-do-conceito>": {
      "name": "Nome legível",
      "aliases": ["sinônimo1", "sinônimo2"],
      "confidence": 0.0,
      "created": "AAAA-MM-DD",
      "last_used": "AAAA-MM-DD",
      "decay_rate": 0.02,
      "contexts": ["ctx-slug-1", "ctx-slug-2"]
    }
  }
}
```

Campos:

- `slug`: kebab-case, estável, nunca renomear (renomear = perder histórico de matching). Se precisar renomear o nome legível, mexe só em `name`.
- `aliases`: cresce ao longo do tempo — toda vez que uma tarefa usar um sinônimo novo pro mesmo conceito e o match for confirmado, adicionar aqui. É a técnica de matching (léxico, não embedding — ver justificativa na arquitetura: custo de infra de vetor não se paga aqui).
- `confidence`: 0 a 1. Nova descoberta via código lido diretamente começa em 0.8. Via inferência do próprio Claude sem fonte verificável, começa em 0.4. Sobe +0.05 (cap 1.0) a cada reuso confirmado. Cai por decay (ver `invalidation-policy.md`).
- `decay_rate`: taxa de queda por invalidação estrutural. Conceito usado com frequência (muitos `contexts`) decai mais devagar — reduzir `decay_rate` proporcionalmente a `len(contexts)`.
- `contexts`: lista de ids de contexto (arquivos em `contexts/ctx-<id>.md`). Um conceito pode aparecer em vários contextos (ex.: `paginacao` aparece na listagem de Cenários e na de Atividades).

## Regras de escrita

- Nunca guardar `files`, `docs` ou texto longo aqui — isso é responsabilidade do contexto. Este arquivo é só índice.
- Escrita atômica: gravar em `concepts.json.tmp` e renomear por cima do original. Evita corrupção em escrita concorrente (last-write-wins é aceitável — não é sistema multiusuário).
- Nunca deletar um conceito. Se cair abaixo do limiar de confidence, ele sai da lista ativa de `contexts` (que vão pra `_archive/`), mas o conceito em si permanece (ele pode voltar a ser usado).

## Matching (busca de conceito a partir da tarefa)

1. Normalizar texto da tarefa (lowercase, sem acento).
2. Comparar contra `name` e `aliases` de cada conceito (substring/palavra-chave, feito pelo próprio raciocínio do Claude — não precisa de script).
3. Se nenhum bate mas a tarefa claramente introduz um conceito novo (ex.: primeira vez que o projeto usa "wizard multi-step"), criar entrada nova com `confidence: 0.4` (sem fonte ainda) e preencher depois que a cascata de busca resolver.
