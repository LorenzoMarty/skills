---
name: quality-gate
description: Roda code-review + simplify em sequência sobre o diff atual, numa chamada só. É chamado pelo workflow:verify em diff grande ou área sensível, e serve também avulso. Usar quando o usuário disser "roda o quality gate", "/quality-gate", "checa isso antes de fechar", ou depois de terminar uma mudança de código não-trivial (sugestão proativa via hook de Stop).
---

# Quality Gate

Objetivo: um único ponto de entrada pra rodar a bateria de qualidade sobre o diff atual, decidindo
sozinho a ordem — usuário não precisa saber a diferença entre `code-review` e `simplify`.

## Quando não rodar

- Diff só toca teste, doc ou config (nada de comportamento de produto pra verificar/revisar).
- Nenhuma mudança de código desde a última vez que o gate rodou nesta sessão.

Nesses casos, diga ao usuário por que está pulando em vez de rodar por rodar.

## Pipeline

1. **Sem `verify` aqui.** `workflow:verify` é quem chama este gate (passo 3.5);
   chamá-lo de volta cria ciclo. Se o usuário quer a verificação completa, rode
   `workflow:verify`, que inclui este gate.
2. **`code-review`** (nível `medium` por padrão; suba pra `high` se o diff for grande ou tocar
   área sensível — auth, pagamento, permissões) — acha bugs de correção e problemas de reuso.
3. **`simplify`** por último, só se `code-review` não achou bug bloqueante — limpeza de
   reuso/simplificação/eficiência não faz sentido rodar sobre código ainda quebrado.
4. **Resuma pro usuário** em poucas linhas: o que cada etapa achou, o que foi corrigido
   automaticamente (se `code-review`/`simplify` rodaram com `--fix`), o que ficou pendente.

## Regras

- Não rode as etapas incondicionalmente — pule etapa que não se aplica e diga por quê (passo 1).
- Não decida sozinho aplicar `--fix` em achado que muda comportamento (não só estilo) sem avisar
  o usuário antes — regra global "sem mudança silenciosa".
- Isso é uma orquestração fina: não reimplemente a lógica de `code-review`/`simplify`
  aqui, só decida ordem e quando pular.

## Próximo passo

De volta ao `workflow:verify` (relatório) ou, avulso, ao usuário com o resumo.
