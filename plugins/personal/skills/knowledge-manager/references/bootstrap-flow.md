# Bootstrap (primeira vez num projeto)

Objetivo: preparar o esqueleto, nunca analisar o projeto inteiro. Custo alvo: ~0 tokens além de operações de filesystem.

## Passos

1. **Detectar raiz do projeto**: raiz do git (ou pasta com `.claude/` já existente, como neste ambiente — ex.: `Qiron-Front/.claude/`).

2. **Checar se `.claude/knowledge/` já existe.** Se sim, bootstrap já rodou — não repetir.

3. **Criar esqueleto vazio**:
   ```
   .claude/knowledge/state.json
   .claude/knowledge/index/concepts.json          -> {"version":1,"concepts":{}}
   .claude/knowledge/index/obsidian-index.json    -> {"version":1,"project_folder":null,"docs":[]}
   .claude/knowledge/contexts/                    (pasta, com contexts/_archive/)
   .claude/knowledge/cache/query-cache.json       -> {"version":1,"entries":{}}
   .claude/knowledge/metadata/tool-usage-log.jsonl (arquivo vazio)
   ```

4. **Garantir `.gitignore`**: se o projeto tem `.gitignore` e não contém `.claude/knowledge/`, adicionar a linha. Se não tem `.gitignore`, não criar um só por causa disso — avisar o usuário uma vez.

5. **Localizar pasta correspondente no vault Obsidian** (só o caminho, não o conteúdo):
   - Usar o índice global do vault (mantido por `claude-obsidian`/`organizar-projeto-claude`, não duplicar aqui). Se esse índice global não existir ainda, não construir aqui — deixar `obsidian-index.json` com `project_folder: null` e resolver isso via cascata (`search-order.md` nível 3) na primeira vez que for realmente preciso.
   - Se resolver, gravar `project_folder` e a lista de `docs` (título + tag + caminho, nunca conteúdo) em `obsidian-index.json`.

6. **Gravar `state.json`**:
   ```json
   {
     "version": 1,
     "bootstrapped_at": "AAAA-MM-DDThh:mm:ss",
     "last_sync": null
   }
   ```

7. Fim. Nenhum código foi lido, nenhum doc foi aberto. O conhecimento real é construído incrementalmente, tarefa por tarefa (fluxo em `SKILL.md`, seção "Pipeline por tarefa").
