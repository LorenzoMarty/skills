---
name: context7-mcp
description: This skill should be used when the user asks about libraries, frameworks, API references, or needs code examples. Activates for setup questions, code generation involving libraries, or mentions of specific frameworks like React, Vue, Next.js, Prisma, Supabase, etc.
---

When the user asks about libraries, frameworks, or needs code examples, use Context7 to fetch current documentation instead of relying on training data.

## When to Use This Skill

Activate this skill when the user:

- Asks setup or configuration questions ("How do I configure Next.js middleware?")
- Requests code involving libraries ("Write a Prisma query for...")
- Needs API references ("What are the Supabase auth methods?")
- Mentions specific frameworks (React, Vue, Svelte, Express, Tailwind, etc.)

## Vault primeiro, Context7 depois (ponte com o Obsidian)

O Context7 diz **o que a biblioteca documenta hoje**; o vault E_Mind guarda
**o que aprendemos usando-a** (armadilhas, decisões, versão fixada). Use os
dois, nesta ordem, sem duplicar:

1. **Ler o vault (custo ~0):** `grep -ril "context7_id\|<lib>" "<vault>/01 - Notas Atômicas"`
   filtrando por `tags: biblioteca` e o nome da lib (caminho do vault em
   `knowledge:claude-obsidian`). Leia só as notas que baterem. Nota com
   `context7_id` no frontmatter → **pule o Step 1** e use esse ID.
2. **Versão:** a do projeto (`package.json`, lockfile, `Stack` do hub) manda;
   prefira o ID versionado (`/org/proj/v15.0.0`) e cite a versão no resultado.
3. **Consultar o Context7** (passos abaixo) para a API atual, uma pergunta
   por conceito.
4. **Gravar de volta só o não óbvio:** se a doc contradisse o que a IA ou o
   vault assumiam, se houve breaking change entre versões, ou se uma
   armadilha custou tempo, acione `knowledge:claude-obsidian` para criar ou
   atualizar **uma nota atômica por armadilha** (`tags: [biblioteca, <lib>]`,
   `context7_id`, `versao`, `verificado: AAAA-MM-DD`, link para o Registro).
   Nunca copie a documentação para o vault: ele não é cache do Context7.
5. **Reconferir quando velho:** nota com `verificado` de mais de ~6 meses, ou
   versão do projeto diferente da nota → trate como hipótese e confirme no
   Context7 antes de usar.

## How to Fetch Documentation

### Step 1: Resolve the Library ID (pule se o vault já tem o `context7_id`)

Call `resolve-library-id` with:

- `libraryName`: The library name extracted from the user's question
- `query`: What to look up in the library's documentation (improves relevance ranking)

### Step 2: Select the Best Match

From the resolution results, choose based on:

- Exact or closest name match to what the user asked for
- Higher benchmark scores indicate better documentation quality
- If the user mentioned a version (e.g., "React 19"), prefer version-specific IDs

### Step 3: Fetch the Documentation

Call `query-docs` with:

- `libraryId`: The selected Context7 library ID (e.g., `/vercel/next.js`)
- `query`: What to look up in the library's documentation, scoped to a single concept

If the user's question spans multiple distinct concepts (e.g. routing and auth and caching), make a separate `query-docs` call per concept with the same library ID, unless the question is about how the concepts interact — combined queries dilute ranking and return shallow results for each topic.

### Step 4: Use the Documentation

Incorporate the fetched documentation into your response:

- Answer the user's question using current, accurate information
- Include relevant code examples from the docs
- Cite the library version when relevant

## Guidelines

- **Be specific**: Describe what to look up in the library's documentation, but keep each query to a single concept
- **One topic per query**: Split multi-topic questions into separate `query-docs` calls — resolve the library ID once, then query per concept, unless the question is about how the concepts interact
- **Version awareness**: When users mention versions ("Next.js 15", "React 19"), use version-specific library IDs if available from the resolution step
- **Dentro do fluxo**: `workflow:implement` e `workflow:write-spec` consultam esta skill antes de escrever código que use uma biblioteca; versão e ID usados entram na spec/PR.
- **Prefer official sources**: When multiple matches exist, prefer official/primary packages over community forks
