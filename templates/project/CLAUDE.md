# <Projeto>

<Uma frase: o que é e para quem.>

## Comandos

<!-- O agente roda exatamente estes comandos no workflow:verify. Mantenha atualizados. -->

```bash
# instalar
<ex.: uv sync / pnpm install>
# lint + format
<ex.: uv run ruff check . && uv run ruff format --check .>
# typecheck
<ex.: uv run mypy src / pnpm tsc --noEmit>
# testes
<ex.: uv run pytest -q / pnpm test>
# rodar local
<ex.: uv run fastapi dev / pnpm dev>
```

## Fluxo

- Tarefas não triviais começam por `workflow:start`.
- Specs em `docs/specs/`; tickets como GitHub Issues com `ready-for-agent`.
- Pronto = `workflow:verify` verde e relatório no PR.

## Convenções

- <stack e padrões que o agente deve seguir: ex. FastAPI async + SQLAlchemy 2.0, routers em app/api/>
- <o que NÃO fazer: ex. não editar migrations já aplicadas>

## Limites do agente

- Pode sem perguntar: criar branch, commitar, abrir PR, adicionar testes, refatorar dentro do escopo do ticket.
- Pergunte antes: mudar schema público/API, apagar dados, mexer em infra/deploy, adicionar dependência pesada.
