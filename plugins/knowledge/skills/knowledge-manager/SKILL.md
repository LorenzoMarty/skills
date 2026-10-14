---
name: knowledge-manager
description: Reduz consumo de contexto/tokens construindo memória semântica reutilizável por projeto (conceitos + contextos), reutilizando o já sabido antes de buscar de novo. Usar SEMPRE que iniciar uma tarefa de código não-trivial (refatorar tela, implementar feature, investigar bug), ANTES de ler código/docs/grafo do zero. Também usar quando o usuário perguntar "o que já sabemos sobre X", "quanto contexto economizamos", ou pedir para esquecer/invalidar um conceito.
---

# Knowledge Manager

Camada de conhecimento reutilizável entre sessões. Princípio único: **nunca busque informação se ela já puder ser reutilizada.** Contexto é recurso caro — trate como budget, não como grátis.

Detalhe de cada peça está em `references/`. Este arquivo é só o pipeline de decisão — não carregue os `references/*` inteiros de uma vez, abra só o que a etapa atual exigir.

## Papel de cada ferramenta (nunca inverter sem justificativa)

| Ferramenta | Responsabilidade | Nunca usar para |
|---|---|---|
| Cache semântico (esta skill) | conceitos + contextos aprendidos, por projeto | fonte de verdade humana |
| Headroom | contexto da sessão atual | memória permanente |
| Obsidian (vault E_Mind) | conhecimento humano permanente (arquitetura, ADR, regras de negócio) | cache da IA, documentação redundante |

Escrita no vault Obsidian é **sempre** delegada ao skill `claude-obsidian` (regras de frontmatter, nome de arquivo, estrutura de pastas já vivem lá). Esta skill nunca escreve no vault diretamente — no máximo sugere e aciona `claude-obsidian`.

## Pipeline por tarefa

1. **Projeto tem `.claude/knowledge/`?** Não → rodar bootstrap (`references/bootstrap-flow.md`). É rápido e barato, não é análise completa do projeto.
2. **Extrair conceitos candidatos** da tarefa (raciocínio próprio, zero tool call — ex: "refatorar tela de Cenários" → `listagem-crud`, `paginacao`, `toolbar`, `filtros`).
3. **Checar `index/concepts.json`** do projeto (leitura única, arquivo leve). Para cada conceito:
   - hit com `confidence` alta → carregar só o(s) `contexts/ctx-*.md` apontado(s). Não buscar de novo.
   - miss ou `confidence` baixa → descer a cascata obrigatória em `references/search-order.md` (cache → Headroom → índice Obsidian → doc específico → código).
4. **Toda resolução nova vira conhecimento**: criar/atualizar concept em `concepts.json` e o `context.md` correspondente (schema em `references/context-model.md`). Isso é automático, sem perguntar ao usuário.
5. **Registrar a origem** em `metadata/tool-usage-log.jsonl` (qual nível resolveu, pra relatório de economia).
6. **Ao fim da tarefa**, se detectar decisão arquitetural/regra de negócio nova (critério em `references/obsidian-integration.md`) → sugerir ao usuário documentar no vault, acionando `claude-obsidian`. Nunca documentar sozinho.

## Invalidação (automática, nunca manual)

Ver `references/invalidation-policy.md`. Resumo: contexto perde confidence quando arquivo referenciado muda de `mtime`; abaixo de 0.3 vai pra `_archive/`. Nunca reconstrução total — só o contexto afetado.

## Comandos que o usuário pode disparar em linguagem natural

- "o que já sabemos sobre X" → buscar em `concepts.json`/`contexts/`, responder sem tocar em código/vault se já tiver.
- "esquece o conceito X" / "invalida contexto Y" → mover pra `_archive/`, remover do índice ativo, log da ação.
- "quanto contexto economizamos" → ler `metadata/tool-usage-log.jsonl` + `state.json`, montar relatório (nível 1 vs níveis mais caros, taxa de reuso).

## Estrutura de arquivos (por projeto, criada no bootstrap)

```
<projeto>/.claude/knowledge/
  state.json
  index/
    concepts.json
    obsidian-index.json
  contexts/
    ctx-<slug>.md
    _archive/
  cache/
    query-cache.json
  metadata/
    tool-usage-log.jsonl
```

Este diretório é estado derivado da IA (não fonte de verdade) — deve estar no `.gitignore` do projeto. Se o `.gitignore` do projeto não tiver `.claude/knowledge/`, adicionar na primeira execução do bootstrap.
