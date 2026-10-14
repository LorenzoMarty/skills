---
name: maestri-workflow
description: Workflow de desenvolvimento por camadas para o Maestro do Maestri. Define as 5 camadas (Specification, Execution, Review, Stress/Security, PR), o grafo de dependências, o perfil por projeto, o estado e as evidências em arquivos, o loop Review↔Execution, a política de gates e o paralelismo. Carregada pelo role Maestro ("Maestro" / "Maestro Projetos") antes de qualquer ação; também serve de referência para os terminais de camada. Usar quando o usuário der um objetivo de desenvolvimento ao Maestro (implementar, corrigir, revisar, preparar PR).
---

# Maestri Workflow

O **Maestro coordena; o workflow é o grafo de camadas que ele executa.** Cada camada é uma tarefa
independente, feita por um terminal recrutado. O fluxo é guiado por **dependências, estado e
evidências**, não por uma sequência fixa: o Maestro decide quais camadas entram, quais rodam em
paralelo, quando repetir e quando parar.

Ferramentas (Jira, Obsidian, browser, Notes, gráficos, `gh`) **não são camadas**: são capacidades
que cada camada usa quando fizer sentido.

## 1. Entrada: classificar e carregar o perfil

1. **Uma linha ao usuário, antes de qualquer outra ação:** modo de entrada + camadas previstas.
2. **Modos de entrada** (cada um é só um grafo predefinido; ver §5):
   `feature/mudança` (grafo completo; **inclui corrigir um bug já conhecido**) · `bug` (só **investigar/reproduzir** causa desconhecida, sem Execution) · `front+back` (duas
   Executions paralelas + contrato) · `vault` · `ideia→tarefas` · `sessões`.
3. **Carregar o perfil do projeto** (§2), reler `state.yaml` de um run em aberto (§6) e só então montar o DAG.

## 2. Perfil por projeto (opcional)

Arquivo `.claude/workflow.yaml` na raiz do repo alvo. **Sem arquivo, valem os padrões abaixo.**

```yaml
workflow:
  jira: false            # padrão: true só se hub do projeto está em 03 - Trabalho/ E o conector Atlassian responde
  jira_project: null     # chave do projeto Jira (ex.: BAC/WEB no Qiron); sem chave, não escreve no Jira
  obsidian: true         # padrão: true se existe hub em 02 - Projetos/ ou 03 - Trabalho/
  pr: true               # padrão: true se há remote GitHub e `gh auth status` ok
  stress: auto           # auto = só por gatilho (§10) | true | false
  security: auto         # idem
  visualization: auto    # auto = só quando o dado é numérico/estrutural (§13)
  max_review_rounds: 3
  gates: default         # default = 3 fixos + exceções | strict = para também ao fim de cada camada
```

**Detecção de padrão** (rode, não presuma): `git remote -v`, `gh auth status`, existência do hub no vault
(`C:/Users/loren/OneDrive/Desktop/E_Mind/02 - Projetos/<Projeto>` ou `03 - Trabalho/<Projeto>`), `CLAUDE.md`
do repo (`## Contexto no Obsidian` diz o hub real). Confirme Jira com uma leitura real antes de depender dele.

**Ferramenta ausente degrada e é reportada, nunca falha.** Sem Jira → contexto vem do Obsidian. Sem
Obsidian → `CLAUDE.md`, docs do repo e código. Sem `gh` → PR vira rascunho local. Reporte a degradação em uma linha.

## 3. Camadas

| Camada | Terminal (role) | Entrada | Saída | Critério de saída | Capacidades |
|---|---|---|---|---|---|
| **1 Specification** | Scout (contexto) + Maestro conduz `spec-interview` com o usuário | objetivo, ticket (se houver), Notes, docs | `spec.md` (REQs, critérios, riscos, camadas necessárias, ferramentas úteis) | usuário aprovou (**G1**) | Jira, Obsidian, Web, docs |
| **2 Execution** | Builder (N em paralelo se independentes) | `spec.md`, findings abertos (loop) | código em branch `feat/<slug>`, testes rodados, evidência | testes relevantes verdes, REQs marcados | repo, Web, docs, Notes |
| **3 Review** | Reviewer (N por foco) + Verifier (runtime) | diff, `spec.md`, evidência de Execution | `APPROVED` ou `CHANGES_REQUIRED` + findings | sem finding `high`/`blocker` aberto e todos os REQs ok | repo, testes, Notes, docs |
| **4 Stress/Security** | Stress Security (terminal próprio) | diff, spec, ambiente local | métricas, achados, evidência | limiares da spec atendidos ou achados tratados | terminal, ferramentas de teste, observabilidade, visualização |
| **5 PR** | PR Author | todas as evidências | `pr.md` (título+corpo) e, após G2, PR aberto | usuário aprovou (**G2**) | git, `gh`, Jira, Notes, evidências |

Stress/Security e PR podem ser `skipped` (com motivo no estado); qualquer camada pode ser repetida (`attempt` +1).
**Specification nunca é pulada.** Com escopo já fechado (bug conhecido, tarefa do hub ou do Jira), ela encolhe para uma **mini-spec**
(`spec.md` com REQs extraídos da tarefa e critérios observáveis, sem entrevista) e o fluxo **para em G1** mostrando-a.
"O escopo já está no hub" **não** dispensa o G1.

**Specification em detalhe.** Scout obtém o contexto (`/contexto`, Jira se `jira`, Obsidian se `obsidian`,
docs relevantes, Notes existentes) e devolve restrições/riscos. O Maestro roda `spec-interview` **com o usuário**
(uma pergunta por vez) e **não deixa encadear `implement-spec`** (regra de comportamento; a skill não é
alterada). A spec define: critérios de aceitação, riscos, quais camadas entram e quais ferramentas ajudam.
Salve em `.claude/specs/<slug>/spec.md` do repo alvo.

## 4. Grafo e caminhos

```text
Specification ─► Execution ─► Review ─┬─► PR                              (caminho A)
                    ▲            │    └─► Stress/Security ─► PR           (caminho B)
                    └─ findings ─┘        │  └─ findings ─► Execution ─► Review ─► PR   (caminho C)
```

O caminho **não é escolhido de antemão**: nasce das decisões (spec, risco, resultado do Review,
pedido do usuário). Modele tarefas como nós `id | agente | tarefa | depends_on | files_owned`.
Sem dependência não satisfeita ⇒ roda agora, no **mesmo** `maestri ask --batch`.

## 5. Modos de entrada (grafos predefinidos, sem regressão)

- **feature/mudança:** Specification → Execution → Review(+Verifier) → [Stress/Security] → PR.
- **bug:** Scout(s) investigam hipóteses independentes em paralelo → Verifier reproduz em runtime → Scribe registra. **Corrigir não faz parte**: proponha como próximo objetivo.
- **front+back:** Scout → nota de canvas `Contrato API <Projeto>` (endpoints, schemas, status, erros, auth; reutilize se já existir) → `maestri connect` aos dois Builders e ao Reviewer → Builder Front ‖ Builder Back (cada um com `--dir` do seu repo, `files_owned` disjuntos; a nota é o único artefato de coordenação) → Review + Verifier em paralelo → consolidar.
- **vault:** Vault Keeper. `organizar-vault` e `diluir-vault` só sob demanda, nunca agendadas. Exclusão/movimentação destrutiva ⇒ dry-run, lista ao Maestro, **G3**.
- **ideia→tarefas:** Planner identifica o projeto **primeiro** (`02 - Projetos/`, `03 - Trabalho/`); nunca assumir. Destino: `jira` ligado ⇒ Jira, senão hub `<Projeto>.md` seção `## Tarefas`. Jira: Planner devolve o payload exato e **não cria nada**; só cria com o token literal `APPROVED_GATE_2` no prompt do Maestro (**G2**).
- **sessões:** `python C:/Users/loren/OneDrive/Desktop/E_Mind/.claude/maestro/sessions.py [FILTRO] [--limit N] [--all]` acha conversas antigas. Para abrir: `maestri list` primeiro (nunca retomar sessão com terminal vivo nem a sessão atual), depois `maestri recruit "<codinome>" --preset "Claude Code" --dir "<cwd da sessão>" --command "claude --resume <id>"`. O `--dir` **tem** de ser o cwd da sessão.

## 6. Estado do workflow

Diretório do run: `<repo principal>/.claude/workflow/<run>/`, com `<run>` = `AAAAMMDD-HHMM-<slug>` (use `date`).
Repo principal = o da tarefa (workspace pai sem `.git`, como NewYork, usa o sub-app; em front+back, o que guarda a spec).
Na primeira criação, acrescente `.claude/workflow/` a `<repo>/.git/info/exclude` (local; não altera arquivo versionado).

`state.yaml` (o Maestro atualiza a cada batch e a cada gate):

```yaml
run: 20260925-1530-cadastros-bugs
goal: "Corrigir os 3 bugs de Cadastros"
project: {name: New York/Estoque, dir: "C:/.../Estoque-NY", profile: {jira: false, obsidian: true, pr: true, stress: auto, security: auto, max_review_rounds: 3, gates: default}}
mode: feature
path: A                       # A | B | C | custom; preenchido conforme o run avança
spec: .claude/specs/cadastros-bugs/spec.md
branch: feat/cadastros-bugs
review_round: 0
gate: {pending: null, since: null}      # null | G1 | G2 | G3 | review-exception | stress-exception
tasks:
  - {id: T1, layer: specification, agent: Sonda, status: completed, depends_on: [], attempt: 1, evidence: [evidence/specification-1.yaml]}
  - {id: T2, layer: execution, agent: Forja, status: running, depends_on: [T1], attempt: 1, evidence: [], files_owned: ["frontend/src/features/cadastros/**"]}
  - {id: T3, layer: review, focus: architecture, agent: Lupa, status: pending, depends_on: [T2], attempt: 0, evidence: []}
log:
  - "2026-09-25T15:41 T1 completed"
```

`status` da tarefa: `pending | running | completed | changes_required | blocked | skipped`.

Ao (re)iniciar, o Maestro lista `.claude/workflow/*/state.yaml` do projeto; havendo run não `completed`, **retome** por ele
(sem repetir camada concluída) e diga isso ao usuário em uma linha. Deve conseguir responder: onde está, o que terminou,
o que roda, o que está bloqueado, o que pode iniciar, o que repetir, que evidências existem e que gate espera o humano.

## 7. Evidência

Cada camada grava `evidence/<camada>-<n>.yaml` **em caminho absoluto indicado pelo Maestro** e devolve o bloco
`STATUS/SUMMARY/RESULT/OPEN` dos roles com `RESULT: evidence=<caminho>` (os 7 roles originais seguem intactos).

```yaml
layer: review                # specification | execution | review | stress_security | pr
focus: architecture          # opcional (Review)
status: changes_required     # approved | changes_required | ok | blocked | failed
summary: "1-3 linhas"
findings:
  - id: REV-001
    severity: high           # blocker | high | medium | low | info
    state: open              # open | resolved
    description: "..."
    evidence: "path:line ou saída de comando"
    suggested_action: "..."
artifacts: ["path/relatorio.md"]
```

**Anexe isto a toda delegação** (o Maestro é quem garante o protocolo):
> "Grave sua evidência em `<caminho absoluto>` no esquema do `maestri-workflow` §7 (layer, status, findings[id,severity,state,description,evidence,suggested_action], artifacts). Termine com o bloco STATUS/SUMMARY/RESULT/OPEN, com `RESULT: evidence=<caminho>`. Notas de canvas se leem com `maestri note read`, não como arquivo."

Devolveu só prosa? Marque a tarefa `blocked` e reenvie com o esquema. Nunca aprove com base em prosa.

**Lições da primeira validação (2026-09-25) — aplique sempre:**
- **Roles somente leitura (Reviewer, Verifier)** não podem gravar arquivo: eles devolvem o YAML **inline** no `RESULT` e **o Maestro grava** o `evidence/*.yaml`. Não force exceção ao role.
- **`ask`/`--batch` devolve só a tela final do terminal (truncada).** O YAML completo se recupera do transcript do recruta (`~/.claude/projects/*maestri-roles*/*.jsonl`, última mensagem do assistente) ou pedindo o envio via `maestri ask` de volta. Nunca julgue por uma resposta cortada.
- **Valide todo YAML ao gravar** (`python -c "import yaml; yaml.safe_load(open(...))"`). Agente escreve à mão e erra (dois-pontos sem aspas). Peça texto livre em bloco `>`; se ainda vier inválido, conserte **só a sintaxe**, registre isso no artefato e siga.
- **Não confie em "passou" de um agente sobre teste automatizado:** o Maestro reproduz o comando que sustenta um finding `high` ou um "verde" (vários runs quando houver suspeita de flakiness) antes de consolidar. Na validação, o Builder relatou 63/63 e o teste falhava em 6 de 10 execuções.
- **Recrutas pedem permissão de leitura por diretório** (primeiro acesso fora do cwd `.maestri/roles/<id>`); o `ask` "termina" com o recruta parado no prompt. Monitore (`maestri check`) por "Do you want to proceed" e trate; só libere leitura dentro do repo da tarefa.
- **Depois de qualquer `role write/edit/assign`, o terminal reinicia e o Maestro Mode fica desligado**: religue na UI. Terminal recrutado com role pode não aceitar o toggle; nesse caso o Maestro real é o terminal que já tem o modo.
- **Sujeira no repo:** recrutas criam `.maestri/` no `--dir` e a spec cria `.claude/specs/<slug>/`. Adicione `.maestri/` e `.claude/workflow/` a `.git/info/exclude`; decida com o usuário se a spec é versionada.

## 8. Loop Review ↔ Execution

1. Reviewers + Verifier rodam em paralelo; o Maestro **consolida**: qualquer finding `high`/`blocker` aberto, ou REQ em lacuna/bug ⇒ `CHANGES_REQUIRED`; senão `APPROVED` (findings `medium`/`low` abertos não bloqueiam e vão para "limitações" do PR).
2. `CHANGES_REQUIRED`: `review_round` +1; envie ao Builder **só os findings abertos** (YAML). O Builder corrige, marca `resolved` com evidência e roda os testes.
3. Re-review **só dos revisores que tinham finding aberto**, mais o Verifier (regressão) — não repita revisores que já aprovaram e não foram afetados.
4. Repita até `APPROVED` ou `review_round == max_review_rounds` (padrão 3). Ao estourar: gate `review-exception` com os findings pendentes; o humano decide (continuar, aceitar risco, replanejar).
5. Todo o loop é nativo do Maestro; `review-spec`/`implement-spec` **não** encadeiam (comportamento).

## 9. Gates humanos

**Sempre param (aguardam aprovação explícita):**
- **G1 — Specification pronta:** mostre caminho + lista de REQs antes de qualquer implementação. Vale também para a mini-spec de escopo já fechado; nunca é dispensado por "a tarefa já está clara".
- **G2 — Ação externa:** `git push`, `gh pr create`, escrita no Jira (mostre título, corpo, projeto e todos os campos). Só depois de aprovado, o prompt ao Planner/PR Author contém o token literal `APPROVED_GATE_2`.
- **G3 — Destrutivo/irreversível:** exclusão, movimentação destrutiva, migração/reset, push em `main`/`master`.

**Só por exceção:** Review (limite de rodadas estourado ou `high`/`blocker` sem resolução) e Stress/Security (idem, ou achado de segurança crítico). Com `gates: strict`, também param ao fim de cada camada.
Nada de aprovação por microetapa: o resto segue sozinho. Ao parar, grave `gate` no `state.yaml`.

## 10. Stress/Security (opcional)

Acione por: pedido do usuário; a spec exigir; mudança de performance, concorrência, API, autenticação/autorização ou dados sensíveis; ou julgamento do Maestro (registre a justificativa no `state.yaml`). Não acionada ⇒ `skipped` com motivo.
Roda em **terminal recrutado próprio** (visível na canvas). Tipos: stress, carga, concorrência, segurança, API, integração, regressão, performance. Só contra ambientes locais/dev do projeto ou alvo que o Maestro nomeou explicitamente. Saída com números (métrica, limiar, resultado, comando, versão).

## 11. PR

`PR Author` usa as evidências acumuladas e prepara `.claude/workflow/<run>/pr.md`: resumo, mudanças, testes e resultados, riscos, limitações, referências (Jira se houver, Notes). Execution trabalha em `feat/<slug>` (nunca direto em `master`/`main`). O fluxo **para em G2** antes de `git push` e `gh pr create`. Com `APPROVED_GATE_2`: `git push -u origin <branch>` e `gh pr create --title ... --body-file pr.md` (base = branch padrão do repo). **Nunca** merge, force-push nem PR de `main` para `main`.

## 12. Paralelismo

- Nó sem dependência pendente ⇒ mesmo `maestri ask --batch '{"Nome": "prompt", ...}'` (alvos distintos; timeout do Bash = tarefa mais lenta, até 10 min; se estourar **não reenvie**, use `maestri check "Nome"`). Nó dependente só começa depois das dependências.
- Não crie paralelismo artificial: se B lê a saída de A, é sequencial.
- Review em N instâncias do role `Reviewer` por foco (arquitetura, segurança, testes), codinomes distintos que não repetem o role.
- Builders paralelos no mesmo repo declaram `files_owned` disjuntos; recrutas sempre com `--dir` do repo do sub-app.
- Só o Maestro coordena; recrutas nunca chamam uns aos outros. Antes de recrutar: `maestri list` e reaproveite.
- Isolamento por floor **não é usado** (git-isolation não verificada no Windows; a CLI não exclui floors).

## 13. Notes, visibilidade e visualização

- **Notes** (`maestri note create --name "Workflow <slug>"`): registre só o que tem valor para o projeto, para outras camadas ou para trabalhos futuros — decisões, descobertas, problemas, hipóteses, resultados de teste, riscos. Sem registro indiscriminado. Camadas seguintes leem com `maestri note read`.
- **Vault:** no fechamento, Scribe grava o registro no hub via `claude-obsidian` sem pedir aprovação (objetivo, modo, roles, tarefas, paralelas, resultados, gates, decisões, resultado final).
- **Browser:** abra `maestri portal create URL "Nome"` quando houver interface relevante (docs oficiais, dashboard, UI de teste) para o usuário acompanhar. Sem portal decorativo.
- **Visualização:** só quando melhora a compreensão de dado numérico/estrutural (métricas, benchmark antes/depois, cobertura, distribuição de erros, dependências). Use `dagflo` ou um artefato HTML se estiverem disponíveis; caso contrário pule e avise. "Scalable Graph" não foi localizado no ambiente.

## 14. Falhas e degradação

- `maestri` bloqueado ("This terminal is not the Maestro"): **pare e avise** para ligar o Maestro Mode; não faça o trabalho sozinho.
- Recruta parado em pedido de permissão (primeiro acesso ao vault em `.maestri/roles/<id>`): `maestri check`, oriente o usuário a permitir; não reenvie.
- Troca de role (`role edit/write/assign`) **reinicia** o terminal e apaga a conversa: o estado está em `state.yaml`, não na memória de ninguém.
- Erro de ferramenta ou camada `failed`: uma tentativa com mais contexto; persistindo, reporte `blocked` ao usuário com o que foi tentado.
