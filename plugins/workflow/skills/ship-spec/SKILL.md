---
name: ship-spec
description: Depois que uma spec está `done` (verify aprovou), prepara o PR a partir da spec e cria issues para o que sobrou — Jira para projetos da Qiron, GitHub Issues para projetos pessoais. Faz push da branch e cria PR e issues sem pedir aprovação (autorização permanente do Lorenzo); nunca faz merge. Usar quando o usuário disser "/ship-spec", "abre o PR da spec", "cria as issues", ou aceitar a oferta do verify.
---

# Ship Spec

Objetivo: transformar spec `done` em PR e issues, sem reimplementar o que skills existentes já
fazem. Esta skill é cola fina: monta o conteúdo a partir da spec e delega.

## Pré-condições

- `.claude/specs/<slug>/spec.md` com `status: done`. Senão, pare e diga que falta `verify`.
- Árvore limpa (`git status`) e commits por REQ já feitos pelo `implement`.

## Pipeline

1. **Detectar o tracker pelo remote**: `git remote get-url origin`.
   - Org/owner `Qiron-Robotics` → **Jira** (projeto `BAC`, salvo se a spec/branch indicar outra
     chave).
   - Qualquer outro remote → **GitHub Issues** nesse repo.
   - Sem remote ou ambíguo → pergunte (AskUserQuestion). Não adivinhe.
2. **Rodar a suíte do projeto** (comando do `CLAUDE.md` do repo; no `api/`:
   `poetry run pytest` e `poetry run lint-imports`). Vermelho → pare e mostre. Em worktree o
   `poetry run` usa outro venv sem dependências: use o interpretador do `.venv` do repo principal e
   ponha `.venv/Scripts` no **fim** do PATH. Se o hook `pre-commit` não estiver instalado, rode
   `pre-commit run --all-files` sobre os arquivos do diff. Registre no corpo da PR o que de fato
   rodou (ex.: só `test_mac.py` vs suíte completa) — não escreva "testes passam" sem isso.
3. **Montar o corpo da PR a partir do spec.md** e mostrar como rascunho:
   - Resumo (Objetivo), checklist REQ com evidência (`REQ-N → commit`, teste/saída), Fora de
     escopo, desvios/scope creep apontados pelo `verify`, achados do quality-gate não
     corrigidos, como testar. Título no estilo dos commits do repo.
4. **Definir a base**: repo Qiron empilha branches `BAC-*` e abre uma PR única no final — nesse
   caso a base é a branch anterior da pilha, não `main`. Demais repos: a branch anterior se a
   issue depende de PR aberto, senão `main`. Na dúvida real, registre `Assumido:` e siga.
5. **Delegar a integração à skill `superpowers:finishing-a-development-branch`**, passando corpo,
   base e comando de teste. Escolha sozinho "Push and create PR": push simples, nunca force. Nunca
   use "merge local". Assignee: owner que não seja Qiron → `LorenzoMarty`; Qiron → nenhum.
6. **Listar o que sobrou**: REQ `[~]`/`[ ]`, scope creep que merece ticket, itens do
   "Fora de escopo" que viram trabalho, achados do review não corrigidos. Agrupe duplicatas.
7. **Criar cada issue com `workflow:file-issue`** (dedupe, template, labels). No Jira da Qiron:
   `getAccessibleAtlassianResources` (cloudId) → `getJiraProjectIssueTypesMetadata` (tipo válido) →
   `createJiraIssue`; epic/parent só se o usuário informar. Reporte as chaves/URLs criadas.
8. **Registro**: se a tarefa foi não-trivial, sugira `claude-obsidian` (regra 3). Não encadeie.

## Regras

- Push, PR e issue estão autorizados em definitivo; **merge nunca** (é do usuário).
- Nunca force-push; nunca `--no-verify`.
- Não reabra escopo da spec nem reimplemente `finishing-a-development-branch`/`quality-gate`.
- Se a ferramenta do tracker estiver indisponível (MCP fora, `gh` sem auth), não troque de tracker
  em silêncio: avise e entregue os rascunhos em texto para o usuário criar (único caso em que não cria).

## Próximo passo

PR e issues criados → fim do fluxo; registre a tarefa com `knowledge:claude-obsidian`.
