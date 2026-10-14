---
name: spec-router
description: Depois que uma spec (`spec-interview`) é aprovada, seleciona o conjunto mínimo de skills para implementá-la, valida cada nome contra o inventário real instalado, resolve sobreposição entre skills concorrentes e grava o plano em `.claude/specs/<slug>/skills-plan.yaml` — separado do spec.md. Nunca implementa código nem faz pergunta de produto (isso é da entrevista). Invocado automaticamente pela `spec-interview` logo após a aprovação, e pode ser rodado manualmente para re-rotear uma spec existente ("roteia skills pra spec X", "/spec-router").
---

# Spec Router

Objetivo: decidir **quais skills usar, quais não, e por quê** — para uma spec já aprovada, antes de
`implement-spec` rodar. Não escolhe requisito, não muda escopo, não implementa nada.

Esta skill nasceu de uma auditoria real do workflow: a seleção de skill feita na entrevista era boa
na decisão, mas se perdia entre a decisão e a implementação (skill recomendada, nunca invocada, sem
registro do motivo). O papel desta skill é fechar esse buraco: toda decisão vira arquivo, todo
"pulei essa skill" vira motivo escrito.

## Quando roda

- **Automático**: chamado pela `spec-interview` assim que o usuário aprova a spec, antes de
  perguntar se quer implementar.
- **Manual**: usuário pode pedir para re-rotear uma spec (nova rodada de `needs-changes`, ou spec
  antiga sem `skills-plan.yaml`).

## Pipeline

### Etapa 1 — Ler a spec aprovada

Ler `spec.md` inteiro: Objetivo, Requisitos (REQ-N), Critérios de concluído, Fora de escopo. Extrair
dessas seções (não pergunte ao usuário — é leitura, não entrevista):
tipo de tarefa, stack envolvida, arquivos/áreas afetadas (se conhecidos), necessidades técnicas,
de UI/UX, de acessibilidade, de testes, de segurança, de performance, de documentação, de validação.

Se a spec não deixar claro o suficiente pra essa extração, **isso não é motivo pra perguntar ao
usuário** — é sinal de que a spec ficou vaga demais; sinalize isso no `skills-plan.yaml` (campo
`selection.notes`) e siga com o que der pra inferir.

### Etapa 2 — Inspecionar o projeto

Ler o que já existe antes de escolher qualquer skill: `CLAUDE.md` (raiz e `.claude/CLAUDE.md` se
houver), convenções de arquitetura, `package.json`/dependências (stack real), design tokens/design
system já em uso, testes existentes, integrações configuradas. Nunca escolha skill só pelo nome —
escolha pelo que o projeto já usa. Ex.: só recomende skill de motion se o projeto já tiver
`framer-motion`/`gsap`/lib equivalente instalada, ou se o REQ pedir animação explicitamente.

### Etapa 3 — Construir o inventário real

Fonte de verdade dupla:

1. **Skills próprias do usuário**: listar `~/.claude/skills/*/SKILL.md` — sempre ativas, sem
   conceito de versão.
2. **Skills de plugin**: ler `~/.claude/plugins/installed_plugins.json` — cada entrada tem
   `installPath` apontando pra a versão **ativa** (ex.: `.../vercel/0.45.1`), não a mais nova em
   cache. Listar `skills/*/SKILL.md` só dentro do `installPath` de cada plugin instalado. Ignorar
   qualquer outra versão que exista em `~/.claude/plugins/cache/` fora desse path — é lixo de cache,
   não skill ativa.

Registrar a fonte usada em `selection.inventory_source` do plano (ex.:
`"~/.claude/skills + installed_plugins.json (2026-08-02)"`). Se `installed_plugins.json` não puder
ser lido, cair para heurística "maior versão semver em cache" e **declarar isso como limitação** no
mesmo campo — nunca falhar silenciosamente.

Re-escanear a cada execução (é leitura de nomes+descrições, custo desprezível) — cobre skill nova
instalada depois da última rodada sem precisar de cache próprio.

### Etapa 4 — Avaliar candidatas

Para cada necessidade extraída na Etapa 1, levantar candidatas plausíveis do inventário (não liste
dezenas de skills irrelevantes — só as que cobririam a necessidade de fato) e pontuar:

```yaml
score:
  task_fit: 0-5              # cobre a necessidade específica do REQ?
  project_compatibility: 0-5 # compatível com stack/convenções já em uso?
  requirement_coverage: 0-5  # quantos REQs ela realmente cobre?
  instruction_quality: 0-5   # SKILL.md é claro, tem pipeline acionável?
  tool_compatibility: 0-5    # as ferramentas que ela precisa estão disponíveis nesta sessão?
  historical_evidence: 0-5   # se já foi usada em spec anterior, registrar o resultado observado
  overlap_penalty: 0-5       # quanto ela se sobrepõe a outra candidata já pontuada
  context_cost_penalty: 0-5  # quão pesada é (SKILL.md grande, references/ extensos)
```

Score é apoio à decisão, nunca veredito automático — toda escolha carrega **justificativa textual**
em `reason`. Não existe fórmula que soma os 8 números e decide sozinha.

**Popularidade não é critério de admissão.** Nome conhecido, número de estrelas/downloads do
plugin, ou posição em algum ranking podem aparecer como observação lateral em `reason`, mas nunca
como motivo suficiente — se `task_fit` ou `project_compatibility` forem baixos, a skill fica de
fora mesmo sendo popular.

### Etapa 5 — Selecionar o conjunto mínimo

Objetivo: cobertura máxima dos REQs com o menor número de skills, evitando redundância. Reaproveite
as regras de desempate que já existiam na `spec-interview` (não as reinvente):

1. Evidência de stack vence banco genérico.
2. Uma skill por necessidade — se duas cobrem >70% do mesmo escopo, escolha uma só. Desempate: uso
   local comprovado > especificidade pro caso > mais nova.
3. Estreita (escopo fechado) vence ampla em empate.
4. Execução vence teoria quando a spec exige código.
5. Complementares coexistem (etapas diferentes da mesma tarefa), redundantes não. Pergunta de
   corte: "a segunda repete o trabalho da primeira, ou continua de onde ela parou?" — se repete,
   corta.

Cada skill selecionada recebe uma prioridade:

- **`required`**: necessária para a implementação ser considerada completa. Se não puder ser
  invocada, `implement-spec` registra motivo/impacto/alternativa/se bloqueia — nunca ignora.
- **`conditional`**: só roda se um gatilho definido ocorrer durante a implementação (ex.:
  `accesslint` só se surgir componente interativo novo). Declare o(s) gatilho(s) por escrito.
- **`optional`**: ajuda, não é necessária. `implement-spec` só invoca se houver benefício real.

**Conjunto vazio é uma saída válida** — se a tarefa está totalmente coberta pelas convenções do
projeto:

```yaml
selected: []
decision: no-specialized-skill-needed
reason: >
  A tarefa é simples e está totalmente coberta pelas convenções e
  ferramentas padrão do projeto.
```

Não force uma skill só para o plano não ficar vazio.

### Etapa 6 — Registrar skills descartadas e conflitos

Para cada candidata plausível não escolhida, uma linha em `excluded` com o motivo — não é uma
lista de "todas as skills que existem", é só quem chegou a ser considerada de verdade.

Para pares quase-duplicados (ex.: `react-best-practices` vs `vercel:react-best-practices`),
registrar em `conflicts`: quem venceu e por quê. Critério padrão de desempate quando não houver
razão específica da spec: skill própria do usuário (mais alinhada às convenções já documentadas em
`CLAUDE.md`) vence skill de plugin genérico, salvo se o plugin cobrir algo que a própria não cobre.

Se uma capacidade desejada não tiver skill instalada nenhuma:

```yaml
unavailable:
  - capability: "auditoria de contraste de cor automatizada"
    reason: "nenhuma skill instalada cobre isso especificamente; accesslint cobre parcialmente (foco/teclado, não contraste)"
```

Nunca inventar um nome de skill que não existe no inventário da Etapa 3.

### Etapa 7 — Produzir o plano

Gravar (criar ou sobrescrever) `.claude/specs/<slug>/skills-plan.yaml`:

```yaml
version: 1

spec:
  slug: <slug>
  status: approved          # espelha o status do spec.md no momento em que o router rodou

selection:
  generated_at: "<ISO8601>"
  inventory_source: "~/.claude/skills + installed_plugins.json"
  project_context:
    framework: ""
    architecture: ""
  notes: ""                 # preenchido só se a spec era vaga demais pra extrair algo (Etapa 1)

selected:
  - name: ui-styling
    source: local            # local | plugin
    priority: required        # required | conditional | optional
    role: "implementação visual do dock e post-its"
    coverage: [REQ-1, REQ-2]
    score: {task_fit: 5, project_compatibility: 5, requirement_coverage: 4, instruction_quality: 4, tool_compatibility: 5, historical_evidence: 3, overlap_penalty: 0, context_cost_penalty: 1}
    reason: "design system e tokens já fixados no projeto; preferida sobre frontend-design por ser execução concreta, não direção estética."
    classification: established   # established | verified | experimental | rejected
    status: pending                # pending | invoked | skipped-justified | skipped-unjustified | unavailable | replaced | not-applicable | failed
    trigger: []                    # só relevante para priority: conditional

excluded:
  - name: frontend-design
    reason: "direção visual já definida pelos requisitos; ui-styling cobre a execução sem precisar de definição estética adicional."

unavailable:
  - capability: ""
    reason: ""

conflicts:
  - candidates: [react-best-practices, "vercel:react-best-practices"]
    decision: react-best-practices
    reason: "skill própria, alinhada às convenções documentadas em claude/CLAUDE.md; vercel:react-best-practices é genérica de plugin, sem ajuste ao projeto."

discovered_during_implementation: []   # implement-spec preenche se achar necessidade nova

validation:
  required: [review-spec]

outcome:
  status: pending           # pending | ok | gaps-found
```

Nunca escrever "Skills necessárias" de volta no `spec.md` — o plano vive só no `skills-plan.yaml`.
No `spec.md`, deixar (ou criar, se a spec for antiga e não tiver) uma linha:

```markdown
## Skills

Ver `.claude/specs/<slug>/skills-plan.yaml`.
```

### Depois de gravar

Apresentar ao usuário um resumo curto do plano (skills `required`/`conditional`/`optional`,
excluídas relevantes, conflitos resolvidos) — não despeje o YAML inteiro na conversa. Se
`selected: []`, diga isso claramente ("nenhuma skill especializada necessária, tarefa coberta pelo
padrão do projeto").

## Classificação de skill nova (`established` / `verified` / `experimental` / `rejected`)

- **`established`**: tem histórico local positivo (já foi usada em spec anterior com resultado
  bom, verificável via `historical_evidence` de outra rodada).
- **`verified`**: foi avaliada agora (Etapa 4), parece adequada, mas ainda sem histórico local.
  É o ponto de partida padrão pra qualquer skill já instalada nunca usada em spec.
- **`experimental`**: skill nova ou com evidência limitada, mas ainda assim selecionável se: cobre
  necessidade real, compatível com o projeto, não duplica skill melhor, instruções claras o
  bastante, risco aceitável.
- **`rejected`**: incompatível, redundante, inadequada ou de baixa qualidade — vai para `excluded`
  com o motivo, não para `selected`.

Depois que `implement-spec`/`review-spec` rodarem sobre uma skill `experimental` ou `verified`,
`review-spec` registra:

```yaml
evaluation:
  useful: true            # true | false | inconclusive
  requirement_coverage: ""
  issues: []
  future_confidence: increased   # increased | unchanged | decreased
```

Isso não é aprendizado automático — é só o registro ficando disponível pra próxima vez que essa
skill for candidata (via `historical_evidence` na Etapa 4). Sem pontuação agregada, sem ranking.

## Regras

- Nunca implementa código, nunca escreve fora de `skills-plan.yaml` (e a linha `## Skills` no
  `spec.md`, se ausente).
- Nunca faz pergunta de produto ao usuário — isso é `spec-interview`. Se a spec não tem informação
  suficiente pra rotear, registra a lacuna em `selection.notes` e segue com o que dá. Correção de
  escopo volta para `spec-interview`, não é resolvida aqui.
- Nunca inventa nome de skill fora do inventário real (Etapa 3).
- `implement-spec` consome o plano, não reabre a Etapa 5 — só pode propor adição registrada
  (`discovered_during_implementation`), nunca substituição silenciosa.
