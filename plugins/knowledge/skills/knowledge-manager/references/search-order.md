# Cascata de busca (ordem obrigatória)

Custo crescente. Sempre tentar nível N antes de N+1. Só pular nível se a tarefa exigir explicitamente aquele tipo de informação (ex: revisar linha exata de um bug → pula direto pro código, mas registrar o motivo no log).

## 1. Cache semântico (custo ~0)

Ler `index/concepts.json` do projeto (um arquivo, leve). Se conceito bate (nome ou alias) e `confidence >= 0.5`:
- Carregar apenas o(s) arquivo(s) `contexts/ctx-*.md` listados nesse conceito.
- Não abrir mais nada. Responder/trabalhar com o que está ali.

Se `confidence < 0.5` ou conceito ausente: descer pro nível 2, mas manter o contexto parcial encontrado (pode complementar, não precisa redescobrir do zero).

## 2. Headroom (custo baixo)

Chamar `mcp__headroom__headroom_retrieve` (carregar o tool via ToolSearch se ainda não carregado: `select:mcp__headroom__headroom_retrieve`). Serve pra reaproveitar algo já processado nesta sessão ou sessão recente que ainda não foi promovido a contexto persistente. Se achar algo útil, promover pro cache semântico (nível 1) ao final — é assim que o Headroom "vaza" conhecimento de sessão pro cache permanente, sem duplicar responsabilidade (Headroom continua só sessão, mas o que vale a pena persistir por concept-worthy, o Knowledge Manager persiste).

## 3. Índice do Obsidian (custo baixo-médio)

Ler `index/obsidian-index.json` (mapa local: quais pastas/arquivos do vault correspondem a este projeto, com título+tags — nunca conteúdo). Ver `references/obsidian-integration.md` pra detalhe de como esse índice é construído/consultado. Se o índice apontar um doc candidato, ir pro nível 4 (abrir só aquele doc). Nunca varrer o vault inteiro aqui. Tarefa que usa biblioteca: busque as notas `tags: biblioteca` da lib (`context7_id`, versão, armadilhas) e, para a doc atual, `dev:context7-mcp` — que já parte dessas notas.

## 4. Documentação específica (custo médio)

Abrir só o doc que o índice (nível 3) apontou. Nunca abrir documentação "só pra garantir".

## 5. Código (custo alto — último recurso)

Read/Grep/Glob direto no código. Só quando os níveis 1-5 não têm a resposta e a tarefa realmente exige ver a implementação atual (ex.: comportamento exato de uma função, bug específico). Depois de ler, o achado vira concept/context novo (nível 1 passa a responder da próxima vez).
