---
name: specs-status
description: Lista, cross-project, toda spec pendente (status ready/in-progress/needs-changes) criada via write-spec em qualquer projeto já trabalhado — não só o projeto atual. Usar quando o usuário disser "/specs-status", "o que tá parado", "specs pendentes", "quais specs faltam implementar".
---

# Specs Status

Objetivo: dar visão de todas as specs pendentes em todos os projetos, não só o `cwd` atual — útil
pra quem alterna entre vários repos e perde de vista o que ficou sem `/implement`.

## Pipeline

1. **Descobrir projetos conhecidos.** Cada sessão do Claude Code grava um diretório de log em
   `~/.claude/projects/<encoded-path>/`. O nome do diretório é uma codificação lossy do caminho real,
   então não tente decodificar pelo nome — em vez disso, pegue o `cwd` real de dentro dos arquivos
   `.jsonl`:

   ```bash
   grep -oh '"cwd":"[^"]*"' ~/.claude/projects/*/*.jsonl | sort -u
   ```

   Isso dá a lista de caminhos reais de projeto já usados (dedupe automático pelo `sort -u`).

2. **Para cada caminho de projeto**, procurar `.claude/specs/*/spec.md` (se a pasta não existir,
   pular silenciosamente — a maioria dos projetos não tem spec).

3. **Para cada `spec.md` encontrado**, ler o frontmatter (`slug`, `status`, `created`,
   `revision_count`) e o título (primeira linha `# `). Calcular idade em dias a partir de `created`.

4. **Filtrar**: mostrar só `status: ready`, `status: in-progress` ou `status: needs-changes` —
   `status: done` não é "pendente", omita por padrão (a menos que o usuário peça "todas incluindo
   concluídas").

5. **Apresentar como tabela**, ordenada por idade decrescente (mais parada primeiro):

   | projeto | spec | status | idade | próximo passo |
   |---|---|---|---|---|

   "próximo passo" é `/implement` (se `ready`), `/verify` (se `in-progress` acabou de
   implementar), ou "aguardando ajuste" (se `needs-changes`).

6. Se não achar nenhuma spec pendente em lugar nenhum, diga isso direto — não é erro, é bom sinal.

## Regras

- Só leitura — nunca edita `spec.md` de outro projeto a partir daqui.
- Não abra/implemente nenhuma spec a partir deste comando; é só visão, ação fica a cargo do usuário.
