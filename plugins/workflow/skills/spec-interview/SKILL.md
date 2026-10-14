---
name: spec-interview
description: Entrevista o usuário sobre um objetivo de desenvolvimento, uma pergunta por vez, até destrinchar objetivo, requisitos e critério de "concluído". Ao final salva a especificação em arquivo local e encadeia automaticamente spec-router e implement-spec. Usar quando o usuário disser "quero criar/fazer X", "me ajuda a especificar", "/spec", ou pedir para planejar/detalhar uma feature antes de codar.
---

# Spec Interview

Objetivo desta skill: transformar uma ideia vaga em especificação executável, via entrevista. Nunca
escreve ou edita código de produção durante esta skill — só arquivos de spec.

## Pipeline

1. **Capturar o pedido inicial** do usuário como está — não repita perguntas cuja resposta já veio
   na mensagem original.
1.5. **Carregar contexto já existente antes de perguntar.** Rode a skill `knowledge-manager` sobre a
   área do pedido (custo ~0, cache semântico do projeto). Se ela apontar doc relevante no Obsidian
   (hub do projeto, `Arquitetura.md`, `Decisões.md`), leia antes de formular perguntas. Objetivo: não
   perguntar algo cuja resposta já está registrada — só perguntar o que só o usuário sabe (regra 2).
   Se achar decisão anterior conflitante com o pedido atual, sinalize ao usuário já na entrevista, não
   só no fechamento.
2. **Entrevistar, uma pergunta por vez.** Espere a resposta antes de fazer a próxima. Antes de cada
   pergunta, cheque se ela já é inferível com confiança do pedido original + contexto carregado no
   passo 1.5 (código, convenções do repo, doc) — se sim, não pergunte, assuma e declare a suposição
   no resumo do passo 4 pra o usuário corrigir se estiver errada. Só pergunte o que só o usuário
   sabe: intenção, prioridade, trade-off de negócio, preferência sem sinal objetivo no repo. Cubra,
   na ordem que fizer sentido para o caso (pule o que já está claro ou inferível):
   - Objetivo específico e motivação (por que isso importa agora).
   - Requisitos funcionais (o que o sistema deve fazer, casos de uso).
   - Requisitos não-funcionais relevantes (performance, segurança, compatibilidade) — só se aplicável.
   - Casos de borda / exceções que importam.
   - **Critério de "concluído"**: o que precisa ser verdade, observável, para considerar a tarefa
     pronta. Sem isso a spec não está completa.
   - Fora de escopo — o que explicitamente não deve ser feito junto.
   - Se o projeto tem convenções relevantes (ex.: `CLAUDE.md`), leia para embasar/inferir a resposta
     antes de perguntar — só pergunte ao usuário o que a convenção não resolve.
3. **Não interrogue além do necessário.** Tarefa trivial → poucas ou zero perguntas de entrevista
   (pode ir direto ao checkpoint do passo 4 se objetivo+requisitos+critério já estão claros do
   pedido+contexto). Pare quando tiver o suficiente para alguém implementar sem adivinhar nada.
4. **Confirme antes de fechar**: resuma objetivo + requisitos + critério de concluído em UMA
   mensagem e peça confirmação (não é mais uma pergunta de entrevista, é checkpoint final).
5. **Salvar a spec** em `.claude/specs/<slug>/spec.md` (criar pastas se preciso; `<slug>` é um nome
   curto kebab-case derivado do objetivo). Estrutura sugerida:

   ```markdown
   ---
   slug: <slug>
   status: ready        # ready | in-progress | needs-changes | done
   revision_count: 0
   created: <data>
   ---

   # <Título curto>

   ## Objetivo
   ...

   ## Requisitos
   - [ ] REQ-1: ...
   - [ ] REQ-2: ...

   ## Critérios de concluído
   - ...

   ## Fora de escopo
   - ...

   ## Skills

   Ver `.claude/specs/<slug>/skills-plan.yaml` (gerado pelo `spec-router` após a aprovação).

   ## Log da entrevista
   - P: ... / R: ...
   ```

   `REQ-N` são a fonte da verdade para `implement-spec` e `review-spec` — escreva-os como
   afirmações verificáveis, não vagas. Não escreva seleção de skill aqui — isso é responsabilidade
   exclusiva do `spec-router` (passo 6 abaixo), que roda depois da aprovação, não antes.

6. Informe ao usuário onde a spec foi salva (caminho). **Encadeie automaticamente a skill
   `spec-router`** passando o caminho do `spec.md`. Apresente o resumo do plano de skills que o
   `spec-router` devolver (não o YAML inteiro).
7. **Encadeie automaticamente a skill `implement-spec`** logo em seguida, passando o caminho do
   `spec.md` — sem perguntar, mesmo padrão de encadeamento automático que `implement-spec` já usa
   para chamar `review-spec` sozinho. Não espere confirmação do usuário para iniciar a
   implementação. Exceção: se a spec for ADR-worthy (sinalizado pelo `spec-router` ou por você
   durante a entrevista), avise que vai registrar a decisão via `/decisao` antes de seguir — não
   precisa perguntar, só avisar (regra 7 da política: sem mudança silenciosa).

## Regras

- Nunca escreva/edite arquivos de código de produção nesta skill.
- Nunca presuma um requisito não perguntado — se não perguntou, não está na spec.
- Se o usuário responder de forma vaga, uma pergunta de esclarecimento é válida antes de seguir.
- Não escolha skill de implementação aqui — isso é exclusivo do `spec-router`, chamado
  automaticamente depois da aprovação (passo 6). Esta skill só entrevista e especifica produto.
- Depois do checkpoint do passo 4, o fluxo segue sozinho até `implement-spec`/`review-spec` — não
  pare pra perguntar se o usuário quer implementar.
