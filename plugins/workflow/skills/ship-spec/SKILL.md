---
name: ship-spec
description: Depois que uma spec está `done` (verify aprovou), prepara o PR a partir da spec e cria issues para o que sobrou — Jira para projetos da Qiron, GitHub Issues para projetos pessoais. Nunca faz push nem cria nada externo sem aprovação explícita do usuário naquele turno. Usar quando o usuário disser "/ship-spec", "abre o PR da spec", "cria as issues", ou aceitar a oferta do verify.
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
4. **Definir a base**: confirme com o usuário. Repo Qiron empilha branches `BAC-*` e abre uma PR
   única no final — pergunte "abre PR agora (base = ?) ou só acumula na pilha?". Nunca presuma
   `main`.
5. **Delegar a integração à skill `superpowers:finishing-a-development-branch`**, passando corpo,
   base e comando de teste. Ela apresenta o menu e executa. O push só acontece se o usuário
   escolher "Push and create PR" **neste turno** — push simples, nunca force. Não ofereça nem use
   a opção "merge local" em branch empilhada.
6. **Rascunhar issues** do que sobrou: REQ `[~]`/`[ ]`, scope creep que merece ticket, itens do
   "Fora de escopo" que viram trabalho, achados do review não corrigidos. Liste título + descrição
   curta + link pro REQ/commit de origem. Agrupe duplicatas.
7. **Mostrar os rascunhos e criar só os aprovados**:
   - **Jira**: `getAccessibleAtlassianResources` (cloudId) → `getJiraProjectIssueTypesMetadata`
     (tipo válido) → `createJiraIssue`. Linke a issue ao ticket da branch se houver. Epic/parent
     só se o usuário informar.
   - **GitHub**: `gh issue create --title ... --body ...` no repo do remote.
   - Reporte as chaves/URLs criadas.
8. **Registro**: se a tarefa foi não-trivial, sugira `claude-obsidian` (regra 3). Não encadeie.

## Regras

- Criar issue ou abrir PR é ação externa: sempre mostrar rascunho e esperar aprovação.
- Nunca push sem o usuário escolher na hora; nunca force-push; nunca `--no-verify`.
- Não reabra escopo da spec nem reimplemente `finishing-a-development-branch`/`quality-gate`.
- Se a ferramenta do tracker estiver indisponível (MCP fora, `gh` sem auth), não troque de tracker
  em silêncio: avise e entregue os rascunhos em texto para o usuário criar.

## Próximo passo

PR e issues criados → fim do fluxo; registre a tarefa com `knowledge:claude-obsidian`.
