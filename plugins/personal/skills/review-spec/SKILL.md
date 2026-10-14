---
name: review-spec
description: Compara o que foi construído com a especificação decidida (.claude/specs/<slug>/spec.md), lista lacunas e bugs com evidência concreta, e devolve correções para a skill implement-spec quando não estiver perfeito. Quando tudo passar, marca a spec como concluída (e atualiza o artefato HTML, se houver um publicado) e encerra o fluxo. Usar depois que implement-spec rodar, ou manualmente com "revisa a spec X", "/review-spec".
---

# Review Spec

Objetivo: verificar se a implementação atende a spec — de fato, em runtime, não só por leitura de
código (regra global de verificação).

## Pipeline

1. **Ler `spec.md`**: Objetivo, todos os REQ-N, Critérios de concluído, Fora de escopo.
2. **Verificar cada REQ-N contra o estado real do código/app**:
   - Leia o código relevante, mas não pare aí — quando o REQ for observável (endpoint, tela, fluxo),
     exercite de verdade: rode o teste, chame o endpoint, abra a tela no browser. Leitura de código
     sozinha não confirma comportamento.
   - Para cada REQ-N registre veredito: `atendido` / `lacuna` (não implementado) / `bug`
     (implementado errado) — com evidência concreta (arquivo:linha, saída de teste, comportamento
     observado).
3. **Verificar os Critérios de concluído** da mesma forma — eles podem cobrir coisas que nenhum
   REQ individual cobre (ex.: "não quebra fluxo X existente").
4. **Sinalizar scope creep**: qualquer coisa construída que não está na spec, mesmo que boa, deve
   ser listada à parte como desvio — não é motivo de reprovação sozinha, mas o usuário deve saber.
4.2. **Revisar qualidade do código** (dimensão separada da conformidade com a spec): invoque a
   skill `quality-gate` sobre `git diff <base>...HEAD` (base = a da branch; na dúvida, pergunte —
   branches `BAC-*` são empilhadas, a base costuma ser a branch anterior, não `main`).
   - Bug confirmado → entra em "Correções pendentes" como se fosse REQ em `bug`.
   - Sugestão de estilo/simplificação → anote no relatório final, não reprova.
   - Se o gate pular etapa (ex.: `verify` indisponível), registre isso como achado informativo —
     não declare "revisado em runtime" sem que tenha rodado de fato.
4.5. **Auditar a execução do plano de skills** (dimensão separada dos REQ-N; só roda se
   `.claude/specs/<slug>/skills-plan.yaml` existir — specs legadas sem o arquivo pulam esta etapa
   sem penalidade). Para cada skill em `selected`:
   - `priority: required` — foi `invoked`? Ok. Foi `skipped-justified` com motivo aceitável? Ok,
     registre como achado informativo, não bloqueante. Foi `skipped-unjustified`, `unavailable` sem
     alternativa registrada, ou `failed`? **É achado** — e se o REQ que ela cobria (campo
     `coverage`) está em lacuna ou bug, declare o vínculo explicitamente: "REQ-Y ficou em lacuna
     porque a skill X (required) não foi invocada" — não trate como coincidência.
   - `priority: conditional` — o gatilho disparou e foi invocada? Ok. Não disparou e ficou
     `not-applicable`? Ok, sem achado. Disparou e não foi invocada? Achado, mesmo tratamento de
     `required` acima.
   - `priority: optional` — nunca gera achado por não ter sido usada, independente do status.
   - Se a skill era `experimental` ou `verified` (sem histórico), registre em `evaluation` do
     `skills-plan.yaml`: `useful` (true/false/inconclusive), `requirement_coverage`, `issues`,
     `future_confidence` (increased/unchanged/decreased) — isso vira `historical_evidence` pra
     próxima vez que essa skill for candidata em outra spec.
5. **Decisão:**
   - **Se algum REQ está em lacuna ou bug** → escreva a seção "Correções pendentes" no `spec.md`
     (um item por REQ com problema: o que está errado, evidência, o que precisa mudar). Se a causa
     identificada na etapa 4.5 foi uma skill `required`/`conditional` não invocada, a correção não
     pode ser só "recomendar a skill de novo" — tem que ser uma ação explícita: "Invocar a skill X
     antes de corrigir REQ-Y" no início do item de correção correspondente. Set `status:
     needs-changes`. Depois:
     - Se `revision_count` do spec já é >= 4, **não encadeie de novo** — pare e peça orientação ao
       usuário (evita loop infinito entre as duas skills).
     - Senão, **chame automaticamente `implement-spec`** passando o `spec.md` atualizado.
   - **Se tudo está atendido e nenhum bug**:
     - Set `status: done` no `spec.md`.
     - Atualize `outcome.status` do `skills-plan.yaml` (se existir): `ok` se nenhum `required`
       ficou `skipped-unjustified`/`unavailable`/`failed`; `gaps-found` se algum ficou, mesmo que
       os REQs tenham fechado por outro caminho — isso **não** bloqueia o `status: done` da spec
       (o resultado observado é o que importa), mas fica registrado e deve aparecer no relatório
       final ao usuário como achado, não fica escondido só porque os REQs passaram.
     - Se `artifact_url` estiver preenchido no frontmatter (usuário optou por publicar na
       `spec-interview`): atualize (redeploy) o mesmo artefato HTML — mesmo `file_path` — para
       refletir o checklist final todo marcado, com a evidência de verificação de cada item. Se
       `artifact_url` estiver vazio, não publique nada agora — não é o momento de perguntar de
       novo, o usuário já optou por não ter artefato.
     - Reporte ao usuário: resumo do que foi entregue, achados da auditoria de skills (4.5), link
       do artefato (se houver), fim do fluxo. Se a tarefa foi não-trivial, sugira rodar a skill
       `claude-obsidian` para registrar (regra 3), sem encadear automaticamente essa parte.
     - **Ofereça `ship-spec`** (PR + issues) numa linha. Não encadeie sozinho: abrir PR envolve
       push, e push só com pedido explícito do usuário.

## Regras

- Nunca aprove um REQ só porque o código "parece" certo — precisa de verificação em runtime quando
  o REQ for observável.
- Correções pendentes devem ser específicas o bastante para `implement-spec` agir sem perguntar de
  novo (arquivo, o que está errado, o que deveria acontecer).
- Não expanda a spec durante a review — se encontrar algo fora de escopo que precisa virar
  requisito, sinalize para o usuário decidir, não adicione sozinho.
- Uma skill `optional` não usada nunca é motivo de achado. Uma skill `required` não usada sempre
  gera achado, salvo justificativa registrada no `skills-plan.yaml` — nunca reprove por skill
  sozinha, mas nunca deixe passar em silêncio também.
- Se a causa de uma lacuna foi skill não invocada, a próxima correção pede a invocação
  explicitamente — não é suficiente recomendar a skill de novo, igual já rodou antes.
