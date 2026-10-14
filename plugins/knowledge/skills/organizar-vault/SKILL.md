---
name: organizar-vault
description: Varre o vault Obsidian E_Mind por 8 problemas estruturais — notas órfãs, Registros sem frontmatter `projeto` ou na pasta errada, hubs/notas faltando no MOC, frontmatter incompleto (`criado`/`status`/`tags`), `[[wikilinks]]` quebrados, nomes duplicados, Registros não listados no hub, hub sem Arquitetura.md/Decisões.md/Registros/ — e corrige tudo sem confirmar por item (mover, renomear, apagar, criar). Usar quando o usuário disser "/organizar-vault", "organiza o vault", "limpeza estrutural do vault", ou pedir manutenção geral do E_Mind. Não usar para conteúdo (registro, decisão, destilar — isso é `claude-obsidian`) nem para carregar contexto (isso é `/contexto`).
---

# Organizar Vault

Manutenção estrutural do vault E_Mind (`C:/Users/loren/OneDrive/Desktop/E_Mind`). Escopo fechado:
só `01 - Notas Atômicas`, `02 - Projetos`, `03 - Trabalho`, `05 - MOCs`. Nunca toca `06 - Templates`,
`08 - Claude` ou a raiz do vault, e nunca reescreve o texto de `Decisões.md`/`Arquitetura.md` — só
mexe em estrutura (frontmatter, links, entradas de MOC).

**Comportamento sem confirmação:** esta skill é uma exceção deliberada à regra geral do
[[Contrato do Vault — E_Mind]] de não mover/apagar nota sem confirmar. A exceção foi decidida
explicitamente pelo usuário via `write-spec` (`.claude/specs/organizar-vault-diario/spec.md`),
ciente do risco. Aplique a correção e siga — não pare para perguntar "posso mover/apagar X?".

## Pipeline

1. **Materialize antes de escanear.** Vault vive em OneDrive — arquivo pode ser placeholder
   online-only. Antes de rodar o scan, faça um `Read` rápido (ou `dir /s` no PowerShell) sobre as 4
   pastas de escopo pra forçar o OneDrive a baixar o conteúdo. Se algum arquivo continuar
   ilegível depois disso, pule ele e anote no relatório final como "não verificado (online-only)" —
   não invente conteúdo pra compensar.

2. **Rode o scanner.**
   ```
   python "C:/Users/loren/.claude/skills/organizar-vault/scripts/scan_vault.py"
   ```
   Devolve um JSON só-leitura com 8 listas: `orphans`, `registros_sem_hub`, `moc_faltando`,
   `frontmatter_incompleto`, `duplicatas_candidatas`, `links_quebrados`,
   `registros_nao_listados_no_hub`, `doc_contrato_faltando`. O script não faz nenhuma escrita — é
   detecção determinística; a correção é sua, guiada pelo relatório.

3. **Corrija cada categoria** (nenhuma pede confirmação ao usuário):

   - **`orphans`** (nota sem nenhum `[[link]]` apontando pra ela): a correção padrão é **linkar**,
     não apagar — adicione a nota no MOC certo (`MOC - Projetos` pra hub em 02/03,
     `MOC - Conhecimento` pra nota atômica em 01) ou, se for claramente um fragmento morto/
     duplicado de outra nota já linkada (leia o conteúdo pra confirmar — mesma ideia, mesmo
     assunto, nada que a outra já não cubra), apague o arquivo. Não invente onde linkar: se não
     der pra decidir a seção certa do MOC com confiança, adicione na seção mais genérica coerente
     (ex.: "Ideias (backlog)" pra projeto sem status claro) em vez de deixar sem entrada.

   - **`registros_sem_hub`**: duas causas possíveis, o `problema` no relatório diz qual. (a)
     frontmatter `projeto` ausente/sem link/apontando pra hub inexistente → abra o Registro,
     confirme qual projeto ele documenta pelo conteúdo e corrija `projeto: "[[Hub Certo]]"`. (b)
     "pasta errada" (hub linkado existe, mas vive em outra árvore de projeto) → mova o arquivo pra
     `Registros/` do projeto do hub — o script já aponta os dois caminhos (onde está vs. onde
     deveria estar) na mensagem.

   - **`links_quebrados`**: `[[alvo]]` cujo alvo não existe como arquivo em lugar nenhum do vault.
     Primeiro busque (`Grep`/`Glob`) se existe nota com nome parecido — nesse caso é typo, corrija
     o link pro nome certo. Se não existir nada parecido (ex.: link especulativo tipo "ver [[X]] se
     existir" escrito por incerteza de quem redigiu), remova só os colchetes duplos (`[[X]]` →
     `X`, texto plano) — não invente/crie a nota de destino, isso seria escopo de outra tarefa.

   - **`moc_faltando`**: adicione a entrada faltante no MOC (`05 - MOCs/MOC - Projetos.md` pra
     projeto/hub, `05 - MOCs/MOC - Conhecimento.md` pra nota atômica), na seção que fizer sentido
     pelo status/conteúdo da nota (ex.: projeto ativo → seção "Ativos"). Siga o formato de link já
     usado nas entradas vizinhas do mesmo MOC (path-qualificado quando o hub estiver em subpasta,
     ex. `[[Helix/Helix|Helix]]`).

   - **`frontmatter_incompleto`**: complete a chave faltante. `status` de nota existente sem valor
     declarado vira `permanente` (padrão do vault pra nota estável) salvo se o conteúdo indicar
     claramente outro estado (ex. nota marcada como rascunho no corpo). `criado` ausente: use a
     data de criação do arquivo no filesystem, formato `AAAA-MM-DD`. `tags` ausente: derive 1-3
     tags semânticas do conteúdo da nota (nunca deixe vazio, nunca `[nota]` genérico).

   - **`duplicatas_candidatas`** (nomes normalizados iguais na mesma pasta — provável erro de
     digitação ou nota recriada): leia as duas notas. Se o conteúdo for substancialmente igual,
     mantenha a mais completa/recente e apague a outra. Se o conteúdo divergir (não é duplicata de
     verdade, só nome parecido), não apague — deixe como está e anote no relatório final como falso
     positivo.

   - **`registros_nao_listados_no_hub`** (registro válido, mas o hub não lista o link dele no
     Log/tabela de Registros): leia o registro (título + primeiro parágrafo de contexto) e insira
     uma linha nova no hub, no formato já usado pelas entradas vizinhas do mesmo dia/seção (lista
     `- [[arquivo]] — resumo` ou tabela `| Data | [[arquivo]] |`), na posição cronológica correta.
     Não resuma o registro inteiro — uma frase que capture o que foi feito basta.

   - **`doc_contrato_faltando`** (hub sem `Arquitetura.md`, `Decisões.md` ou pasta `Registros/` em
     algum lugar da própria árvore — contrato do vault exige os 3): crie o(s) arquivo(s) faltante(s)
     com template mínimo (frontmatter `criado`/`status: permanente`/`tags` + título
     `# <Nome> — Arquitetura` ou `# <Nome> — Decisões`, sem conteúdo narrativo inventado) e link no
     hub, seção "Documentos do projeto"/"Notas". `Registros/` faltante: só crie a pasta, sem
     arquivo. Não preencha conteúdo real de Arquitetura.md — isso é `/contexto`/tarefa do usuário
     depois.

4. **Ao terminar, mostre um resumo no chat**: quantos itens por categoria foram corrigidos, lista
   curta de arquivos movidos/renomeados/apagados (esses sempre aparecem explicitamente, mesmo sem
   pedir confirmação prévia — o usuário precisa saber o que sumiu), e qualquer item pulado
   (online-only não materializado, falso positivo de duplicata).

## Regras

- Não editar o texto de `Decisões.md`/`Arquitetura.md` — essas correções são só de estrutura
  (frontmatter/links), nunca do conteúdo narrativo.
- Não sair do escopo `01/02/03/05 - *`.
- Apagar é reservado a duplicata confirmada por leitura — nunca apague por suspeita, sempre leia o
  conteúdo primeiro.
- O resumo final (passo 4) é obrigatório mesmo quando a correção rodou sem confirmação prévia —
  "sem confirmar antes" não é o mesmo que "sem transparência depois".
