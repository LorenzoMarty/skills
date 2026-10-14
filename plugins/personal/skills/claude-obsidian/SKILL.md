---
name: claude-obsidian
description: Grava contexto de projeto no vault Obsidian E_Mind ao concluir uma tarefa de código não-trivial (regra 3 da Política de Trabalho) — classifica o que foi feito, roteia para o arquivo certo (hub, Arquitetura.md, Decisões.md ou Registros/) e aplica frontmatter/nomenclatura corretos. É também o gatilho "/registro" e a rota "/decisao" (append em Decisões.md). Usar ao concluir tarefa, quando o usuário pedir "salvar no obsidian", "/registro", "documenta a decisão", ou quando o knowledge-manager sinalizar critério ADR-worthy. Nunca usar como cache da IA ou documentação redundante do código.
---

# Claude Obsidian

Escreve no vault E_Mind (`C:/Users/loren/OneDrive/Desktop/E_Mind`) — conhecimento humano
permanente, nunca cache da IA. Regras de pasta/frontmatter/nomenclatura completas em
`references/obsidian-vault.md` — leia antes da primeira escrita da sessão, não recarregue depois.

## Quando disparar

- Fim de tarefa não-trivial de código (regra 3): refatorou, implementou feature, corrigiu bug com
  causa não óbvia, mudou fluxo/API/schema.
- Usuário pede explicitamente: "salvar no obsidian", "/registro", "documenta a decisão"/"/decisao".
- Usuário pede varredura retroativa ("destila os registros antigos", "atualiza as notas atômicas"):
  aplique o critério do passo 3.1 aos Registros já existentes no vault (todos os projetos), sem
  tocá-los — só cria/atualiza nota atômica quando achar padrão repetido ainda não coberto.
- `knowledge-manager` sinaliza critério ADR-worthy (padrão novo usado por 2+ conceitos, decisão
  arquitetural, regra de negócio nova/alterada, mudança que afeta contexto existente no cache) —
  nesse caso **pergunte ao usuário se quer documentar antes de escrever**, não escreva sozinho.

Não dispare para: leitura pura, exploração, tarefa trivial (typo, rename local), ou quando nada
mudou de fato no projeto.

## Pipeline

1. **Ache a pasta do projeto.** Leia `## Contexto no Obsidian` no `CLAUDE.md`/`claude/CLAUDE.md` do
   repo atual — é a fonte do caminho e nome do hub reais (projetos pessoais em `02 - Projetos/`,
   projetos de trabalho em `03 - Trabalho/`, hub pode ter nome próprio). Nunca adivinhe o caminho.
2. **Verifique materialização OneDrive.** Vault pode ter arquivos online-only (placeholder). Se a
   leitura/escrita falhar de forma estranha, sinalize online-only ao usuário — nunca invente
   conteúdo pra compensar.
3. **Classifique o que aconteceu** (ver tabela em `references/obsidian-vault.md#classificação`):
   - Tarefa concluída → novo arquivo em `Registros/AAAA-MM-DD-resumo-curto.md`.
   - Decisão arquitetural/ADR (rota `/decisao`) → **append** em `Decisões.md`, nunca sobrescreve.
   - Mudança estrutural (fluxo de request, camadas, integrações) → atualiza `Arquitetura.md`.
   - Mudança que afeta o hub (status, links novos) → atualiza `<Projeto>.md`, só append/edição
     pontual.
   - Padrão/lição que **já se repetiu em mais de um projeto, ou tem potencial claro de repetir**
     → além do Registro, cria ou atualiza nota em `01 - Notas Atômicas/` (ver passo 3.1). Não é
     "se o usuário pedir" — avalie sempre, silenciosamente, ao gravar o Registro.
   Mais de uma categoria pode se aplicar na mesma tarefa — grave em todas as que se aplicarem.

3.1. **Destilar em nota atômica (quando aplicável).** Critério: o padrão já apareceu em outro
   projeto (ex.: mesma solução de UI, mesmo tipo de bug, mesma decisão de arquitetura) ou é
   genérico o bastante pra claramente poder se repetir — não destile decisão/bug hiperespecífico
   de um projeto só sem sinal de generalização.
   - Padrão já coberto por nota atômica existente → **atualize** essa nota (seção
     `## Desenvolvimento` ganha o novo caso; `## Conexões` → `Aplicado em:` ganha o projeto novo).
     Nunca crie nota duplicada pro mesmo padrão.
   - Padrão novo, sem nota correspondente → crie nota nova em `01 - Notas Atômicas/`, formato:
     frontmatter `criado`/`tags`/`status: permanente`/`area` + `# Título` + `## Ideia central`
     (1 frase generalizável, sem nome de projeto) + `## Desenvolvimento` (caso concreto, com
     `[[link]]` pro Registro de origem) + `## Conexões` (`Relacionado a:` outras notas atômicas
     próximas, `Aplicado em:` hub(s) do(s) projeto(s)) + `## Fonte` (`Origem:` registro(s)).
   - **Registro original nunca é apagado, resumido ou esvaziado** por esse processo — a nota
     atômica é aditiva, o Registro continua sendo o histórico primário e completo.
   - Nota atômica criada/atualizada sempre linkada em `05 - MOCs/MOC - Conhecimento.md` (seção
     temática correspondente) — mesma regra geral de não deixar nota órfã.
4. **Aplique frontmatter e nomenclatura** conforme `references/obsidian-vault.md`. Registro novo usa
   o formato de `06 - Templates/Registro.md` (`criado`/`tipo: registro`/`projeto`/`tags`, sem
   `status`); hub/Arquitetura/Decisões/nota atômica usam `criado`/`status`/`tags`(+`area`). Datas
   absolutas, nunca "hoje"/"ontem".
5. **Linke, não duplique.** Toda referência a outra nota do vault usa `[[Nota]]`. Nunca copie
   conteúdo de uma nota existente para dentro de outra.
6. **Confirme antes de:** sobrescrever/apagar nota do usuário, mover/renomear nota existente, mudar
   status de projeto em qualquer MOC. Pare e pergunte — não é ação silenciosa.

## O que nunca fazer

- Nunca escrever fora do vault E_Mind por esta skill (não é lugar de gerar `claude/docs/` no repo).
- Nunca usar esta skill como fonte de verdade de código — código/estrutura de arquivos é
  responsabilidade de leitura direta (Read/Grep), não do vault.
- Nunca reescrever um arquivo inteiro quando um append/edição pontual resolve.
