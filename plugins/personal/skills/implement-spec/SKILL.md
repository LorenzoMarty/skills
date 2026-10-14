---
name: implement-spec
description: Lê uma especificação já decidida (arquivo .claude/specs/<slug>/spec.md gerado pela skill spec-interview) e implementa exatamente o que está lá — sem inventar requisito, sem adicionar escopo. Ao final lista os REQ-N atendidos e chama automaticamente a skill review-spec. Usar quando o usuário disser "implementa a spec", "constrói conforme especificado", "/implement-spec", ou depois de aprovar uma especificação.
---

# Implement Spec

Objetivo: construir exatamente o que a spec descreve. Esta skill não reabre decisões de produto —
isso já aconteceu em `spec-interview`.

## Pipeline

1. **Localizar a spec.** Se o usuário passou slug/caminho, use. Senão procure em `.claude/specs/`
   por spec.md com `status: ready` ou `needs-changes`. Se houver mais de uma candidata ambígua,
   pergunte ao usuário qual (AskUserQuestion) — não adivinhe.
2. **Ler a spec inteira** antes de tocar em código: Objetivo, Requisitos (REQ-N), Critérios de
   concluído, Fora de escopo. Se veio de uma rodada anterior de `review-spec`, leia também a seção
   "Correções pendentes".
2.5. **Localizar `.claude/specs/<slug>/skills-plan.yaml`.**
   - **Existe**: valide que `spec.status` do yaml não está obviamente desatualizado em relação ao
     spec.md (ex.: spec foi re-aprovada com mudança grande de escopo depois do plano ter sido
     gerado) — se divergir, avise o usuário e pergunte se quer rodar `spec-router` de novo antes de
     continuar. Senão, siga com o plano como está.
   - **Não existe, mas o spec.md tem uma seção antiga "Skills necessárias"** (specs criadas antes
     desta versão do workflow): use essa lista como estava — comportamento legado, sem exigir
     retrofit. Não crie `skills-plan.yaml` sozinho; se o usuário quiser o formato novo, ele roda
     `spec-router` manualmente.
   - **Nenhum dos dois existe**: siga sem plano formal de skill — nem toda tarefa precisa de uma.
3. **Consumir o plano, não re-escolher.** Se há `skills-plan.yaml`:
   - Invoque (via ferramenta Skill) toda skill `priority: required`, no ponto do pipeline onde o
     `role`/`coverage` dela se aplica. Ao invocar, marque `status: invoked` no yaml. Se não puder
     invocar (indisponível, MCP fora do ar, etc.), **não ignore silenciosamente** — marque
     `unavailable` ou `skipped-justified`/`skipped-unjustified` conforme o caso, e registre em
     `implementation_notes`: motivo, impacto no REQ coberto, alternativa usada (se houver), e se
     isso bloqueia a conclusão do REQ.
   - Para cada `priority: conditional`, avalie o(s) `trigger` contra o que está sendo de fato
     implementado. Disparou → invoque e marque `invoked`. Não disparou → marque `not-applicable`.
   - Para `priority: optional`, invoque só se houver benefício concreto nesse momento; senão,
     `skipped-justified` com motivo breve.
   - Se perceber, trabalhando, que falta uma skill não prevista no plano: isso é permitido, mas
     **registre a descoberta** em `discovered_during_implementation` do yaml (nome, motivo, REQ
     afetado) antes de invocar — nunca substitua uma entrada existente do plano silenciosamente.
     A lista de `selected` gerada pelo `spec-router` é piso, não teto, mas toda adição fica visível.
   - Se não há `skills-plan.yaml` nem seção legada: siga o julgamento normal (mesma regra de antes:
     invocar skill relevante que perceber faltando, sem formalidade de registro).
3.5. **Explorar antes de editar.** Delegue a um subagente Explore o mapa de onde a mudança entra,
   padrões a seguir e testes próximos (só a conclusão, com caminhos). Leia você mesmo só o que vai
   editar. Contexto do projeto: `knowledge-manager` antes de varrer código.
4. **Implementar literalmente os REQ-N.** Regras:
   - **Teste primeiro**: para cada REQ observável, escreva o teste (ou defina o comando) que o
     codifica e confirme que falha pelo motivo certo antes de implementar. Bug = teste que reproduz.
   - Decisão não prevista na spec: se reversível e dentro do escopo, decida e registre como
     `Assumido:` (motivo e como reverter) no log da spec; se irreversível ou muda contrato, pare e
     pergunte (regra 7). Achou problema fora do escopo? Anote no log, não corrija.
   - Não adicionar funcionalidade fora da lista de requisitos, mesmo que pareça "óbvia" ou "boa
     prática" — isso é scope creep, e será sinalizado como tal por `review-spec`.
   - Não pular um REQ por parecer difícil; se for genuinamente inviável, pare e explique ao usuário
     em vez de silenciosamente ignorar.
   - Seguir as convenções já existentes no repo (ex.: `CLAUDE.md` do projeto) para estilo de código,
     não a spec — a spec define O QUÊ, o repo define COMO.
   - **Commit por REQ (ou grupo coeso de REQs), só depois do REQ passar em teste/lint:**
     - Estilo da mensagem: copie o de `git log --oneline -10` (ex.: `feat(ai): ... (BAC-N)`); a
       chave do ticket vem do nome da branch ou da spec — se não houver, omita, não invente.
     - `git add` só dos arquivos do REQ, por nome — nunca `-A`/`.`. Antes, `git status` pra não
       arrastar arquivo alheio.
     - Confira `ls "$(git rev-parse --git-common-dir)/hooks"`: se não há `pre-commit` instalado, o
       commit passa sem hook — rode `pre-commit run --files <arquivos>` na mão (com o `.venv`
       do projeto no **fim** do PATH, pois o `pre-commit` do venv pode falhar e `lint-imports`
       só existe lá). Nunca `--no-verify`. Hook falhou → corrija e crie commit novo, não `--amend`.
     - Antes de commitar, leia `git diff` e desfaça hunks fora do REQ (ex.: formatter reformatando
       código alheio) — scope creep colateral não entra no commit; se inevitável, registre como
       desvio na spec.
     - Termine a mensagem com a linha `Co-Authored-By` indicada pelo harness.
     - **Nunca `git push`** — push só no `ship-spec`, com pedido explícito do usuário.
5. **Se a spec for ambígua ou faltar informação necessária para implementar** (ex.: não diz qual
   endpoint usar), não presuma — pergunte ao usuário. Regra global "sem presunção" se aplica aqui:
   doc incompleta não vira decisão sua.
6. **Ao terminar**, atualize `spec.md`:
   - Marque cada `REQ-N` como `[x]` (atendido), `[~]` (parcial) ou deixe `[ ]` (não atendido) —
     honestamente, mesmo que incompleto.
   - Incremente `revision_count`.
   - Adicione entrada no log: o que foi implementado, quais arquivos, se rodou testes, e o hash
     curto do commit de cada REQ (`REQ-2 → a1b2c3d`) — `review-spec` usa isso pra ver o diff por REQ.
   - Se `revision_count` >= 4 e ainda houver REQ não atendido, PARE aqui e peça orientação ao
     usuário em vez de encadear para review-spec de novo (evita loop infinito).
   - Se há `skills-plan.yaml`: atualize `status` final de cada skill em `selected` (`invoked` /
     `skipped-justified` / `skipped-unjustified` / `unavailable` / `replaced` / `not-applicable` /
     `failed`) e `outcome.status` do plano (`ok` se nada ficou pendente sem justificativa,
     `gaps-found` se alguma `required` ficou `skipped-unjustified`/`unavailable`/`failed`).
7. **Liste para o usuário** os REQ-N atendidos vs não atendidos, uma linha cada.
8. Se um mesmo erro travar 3 tentativas seguidas, pare, registre o que tentou e peça ajuda.
9. **Chame automaticamente a skill `review-spec`** passando o caminho do `spec.md`, a menos que o
   passo 6 tenha te feito parar por excesso de revisões.

## Regras

- Fonte da verdade é a spec, não a memória da conversa nem suposições.
- Não reabra escopo — se o usuário quiser mudar requisito, isso volta para `spec-interview`, não
  para esta skill.
- Não reabra a seleção de skills — isso é exclusivo do `spec-router`. Esta skill executa o plano e
  registra o que aconteceu de fato; só pode adicionar (registrado), nunca remover ou trocar uma
  entrada silenciosamente.
- Rode testes/lint relevantes do projeto antes de considerar um REQ atendido, quando aplicável.
