---
name: quality-gate
description: Roda verify + code-review + simplify em sequência sobre o diff atual, numa chamada só — pra quem não quer decorar quando usar cada skill separadamente. Usar quando o usuário disser "roda o quality gate", "/quality-gate", "checa isso antes de fechar", ou depois de terminar uma mudança de código não-trivial (sugestão proativa via hook de Stop).
---

# Quality Gate

Objetivo: um único ponto de entrada pra rodar a bateria de qualidade sobre o diff atual, decidindo
sozinho a ordem — usuário não precisa saber a diferença entre `verify`, `code-review` e `simplify`.

## Quando não rodar

- Diff só toca teste, doc ou config (nada de comportamento de produto pra verificar/revisar).
- Nenhuma mudança de código desde a última vez que o gate rodou nesta sessão.

Nesses casos, diga ao usuário por que está pulando em vez de rodar por rodar.

## Pipeline

1. **`verify`** primeiro — confirma em runtime que a mudança faz o que devia (não só lint/typecheck).
   `verify` é reservada ao usuário (`disable-model-invocation`): chamá-la via Skill falha e **não
   se replica o fluxo dela por outro caminho**. Portanto, quando o gate roda por modelo, pule este
   passo, avise "verify é manual — rode `/verify`" e registre no resumo que a verificação em
   runtime NÃO foi feita por esta skill. Se o usuário invocou `/verify` antes, aproveite o
   resultado. Se não há superfície de runtime (só teste/doc), pule também e avise.
2. **`code-review`** (nível `medium` por padrão; suba pra `high` se o diff for grande ou tocar
   área sensível — auth, pagamento, permissões) — acha bugs de correção e problemas de reuso.
3. **`simplify`** por último, só se `code-review` não achou bug bloqueante — limpeza de
   reuso/simplificação/eficiência não faz sentido rodar sobre código ainda quebrado.
4. **Resuma pro usuário** em poucas linhas: o que cada etapa achou, o que foi corrigido
   automaticamente (se `code-review`/`simplify` rodaram com `--fix`), o que ficou pendente.

## Regras

- Não rode as três incondicionalmente — pule etapa que não se aplica e diga por quê (passo 1).
- Não decida sozinho aplicar `--fix` em achado que muda comportamento (não só estilo) sem avisar
  o usuário antes — regra global "sem mudança silenciosa".
- Isso é uma orquestração fina: não reimplemente a lógica de `verify`/`code-review`/`simplify`
  aqui, só decida ordem e quando pular.
