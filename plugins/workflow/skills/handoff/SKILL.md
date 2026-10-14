---
name: handoff
description: >-
  Compacta a conversa num documento de handoff para outra sessão continuar o
  trabalho sem reler tudo. Use quando o contexto estiver perto do limite, o
  trabalho mudar de assunto, a sessão for encerrar com tarefa pela metade,
  ou o usuário pedir "handoff", "passa o bastão" ou "continua em outra
  sessão".
argument-hint: "No que a próxima sessão vai focar?"
---

# Handoff

Você escreve o bilhete que permite a uma sessão nova continuar **sem
perguntar nada e sem reler a conversa**.

Processo: **ver o que já está registrado → escrever só o que falta →
salvar onde a próxima sessão vai encontrar.**

## Conteúdo

```markdown
# Handoff — <tarefa> (<data>)
## Objetivo
## Estado atual        <!-- feito, em andamento, branch e último commit -->
## Próximos passos     <!-- em ordem, cada um acionável -->
## Decisões e armadilhas  <!-- o que não está na spec e custaria tempo redescobrir -->
## Referências         <!-- spec, tickets, PRs, arquivos-chave (por caminho/link) -->
## Skills sugeridas    <!-- ex.: workflow:implement #43, workflow:verify -->
```

Regras:

- Não duplique o que já está em spec, ticket, commit ou PR: aponte o link.
- Remova segredos, tokens e dados pessoais.
- Se o usuário passou argumento, foque o documento no que a próxima sessão
  vai fazer.

## Onde salvar

Sessões na nuvem perdem o disco ao terminar, então:

1. Há PR ou issue aberta para o trabalho → publique como comentário nela.
2. Senão, há spec em `docs/specs/` → acrescente uma seção `## Handoff` nela e
   faça commit e push.
3. Senão → salve no diretório temporário do sistema e mostre o caminho.

Termine dizendo, em uma linha, como retomar: por exemplo
"Nova sessão: `workflow:implement #43` — o handoff está no comentário da
issue."
