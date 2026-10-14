---
name: diluir-vault
description: Trabalha o conteúdo do vault Obsidian E_Mind (não a estrutura): (1) diluir — condensa nota atômica longa/redundante, ou destila Registro/hub cru em nota atômica nova; (2) padronizar — alinha frontmatter e seções ao template `06 - Templates/Nota Atômica.md`; (3) agrupar — mescla notas atômicas que cobrem a mesma ideia numa canônica, atualizando `[[links]]` e MOC. Roda sem confirmar por item e fecha com resumo. Usar quando o usuário disser "/diluir-vault", "dilui as notas", "padroniza as notas atômicas", "agrupa notas duplicadas", "essas notas estão redundantes". NÃO usar para links quebrados, MOC faltando ou nome duplicado (isso é `organizar-vault`), nem para escrever registro novo (isso é `claude-obsidian`/`/registro`).
---

# Diluir Vault

Trabalha o **conteúdo** das notas do vault E_Mind (`C:/Users/loren/OneDrive/Desktop/E_Mind`) —
comprimento, formato, redundância entre notas. Diferente de [[organizar-vault]] (que mexe só em
estrutura: links, MOC, frontmatter básico, duplicata de nome idêntico) e de `claude-obsidian` (que
grava conteúdo *novo* vindo da sessão atual). Esta skill relê o que já existe e reescreve/funde.

Escopo: `01 - Notas Atômicas`, `02 - Projetos`, `03 - Trabalho`, `05 - MOCs`. Nunca toca
`06 - Templates` nem `08 - Claude`.

**Sem confirmação por item** — mesma exceção deliberada do `organizar-vault` ao
[[Contrato do Vault — E_Mind]]. Aplique e siga. Em troca, o passo 5 (resumo final) é obrigatório e
lista todo arquivo criado, reescrito ou apagado — transparência depois de agir, não antes.

## Pipeline

1. **Materialize antes de escanear.** Vault vive em OneDrive; force o download lendo (`Read` ou
   `dir /s` no PowerShell) as 4 pastas de escopo antes do scan. Arquivo que continuar ilegível
   depois disso: pule e anote no resumo final como "não verificado (online-only)".

2. **Rode o scanner** (só leitura, não escreve nada):
   ```
   python "C:/Users/loren/.claude/skills/diluir-vault/scripts/scan_notes.py"
   ```
   Devolve JSON com 4 listas: `notas_longas`, `fora_padrao`, `grupos_sobrepostos`,
   `registros_destilaveis`. `grupos_sobrepostos` usa sobreposição de palavras-chave
   (título + tags) como heurística barata — é candidato, não veredito; leia as duas notas antes de
   decidir se são a mesma ideia de fato.

3. **Trate cada categoria:**

   - **`notas_longas`** (nota atômica acima de ~550 palavras de desenvolvimento — sinal de que
     virou mais de uma ideia, ou de que está redundante): leia a nota inteira.
     - Se cobre **uma ideia só** mas com prosa redundante/repetitiva → condense no lugar. Cada
       frase deve carregar informação nova; corte reafirmação da mesma ideia com palavras
       diferentes. Preserve todo link `[[...]]`, todo dado concreto (nomes de arquivo, comandos,
       números) — diluir é cortar gordura de texto, nunca cortar informação.
     - Se cobre **mais de uma ideia** (nota virou um mini-hub) → divida em duas ou mais notas
       atômicas, uma por ideia, seguindo o template. Link as novas notas entre si em "Conexões" e
       atualize `05 - MOCs/MOC - Conhecimento.md` com as entradas novas no lugar da antiga.

   - **`registros_destilaveis`** (Registro ou hub com conteúdo técnico substancial que nenhuma
     nota atômica ainda cita como `Origem`): não é destilar tudo automaticamente — leia o conteúdo
     e destile só o que for um **padrão reusável** (decisão que se repetirá, gotcha que vai
     morder de novo, técnica aplicável em outro contexto). Registro que é só log operacional do dia
     ("rodei X, deu Y") não vira nota atômica — deixe como está. Quando destilar: crie a nota nova
     em `01 - Notas Atômicas/` no template, preencha `Fonte > Origem` com `[[registro-original]]`,
     linke em `MOC - Conhecimento.md`. Não apague o registro original — ele continua sendo o log
     bruto; a nota atômica é o resumo reusável.

   - **`fora_padrao`** (frontmatter incompleto ou seções fora do template
     `06 - Templates/Nota Atômica.md`): complete a chave/seção faltante lendo o conteúdo da nota
     pra inferir o valor certo — nunca deixe placeholder vazio. Seção faltando (ex.: nota sem
     "## Conexões"): adicione a seção; se não houver conexão óbvia pra listar, é aceitável deixar
     "Relacionado a:" sem alvo, mas a seção precisa existir pro template ficar consistente entre
     notas.

   - **`grupos_sobrepostos`** (candidatas a merge): leia as notas do par/grupo inteiras, não só o
     título. Mescle **somente** se, depois de ler, as notas defendem a mesma ideia central — não
     mescle duas notas que só compartilham domínio (ex.: duas notas sobre observabilidade, mas uma
     é sobre alerting e outra sobre dashboards, não são a mesma ideia). Ao mesclar:
     1. Escolha a nota mais completa/recente como base; funda o conteúdo exclusivo da outra nela
        (sem duplicar frases repetidas entre as duas).
     2. Apague o arquivo mesclado.
     3. Corrija todo `[[link]]` no vault que apontava pro arquivo apagado, redirecionando pro
        arquivo que sobrou (`Grep` por `[[Nome Antigo]]` nas 4 pastas de escopo).
     4. Corrija a entrada correspondente em `MOC - Conhecimento.md`.
     Se o conteúdo divergir na leitura mesmo com keywords em comum, não mescle — anote como falso
     positivo no resumo final.

4. **Depois de qualquer merge ou split, rode uma segunda passada de `Grep` por wikilinks quebrados**
   nas 4 pastas de escopo, pra garantir que nenhuma referência ficou órfã por causa da própria
   correção desta skill. Corrija o que achar.

5. **Resumo final obrigatório no chat**: por categoria, quantos itens tratados vs. pulados; lista
   explícita de arquivos criados, reescritos (com antes/depois de contagem de palavras pra
   `notas_longas`) e apagados; grupos que pareciam merge mas não eram (falso positivo); qualquer
   arquivo online-only não verificado.

## Regras

- Nunca cortar informação concreta (números, nomes de arquivo, comandos, decisões) achando que é
  "diluir" — diluir é remover repetição de prosa, não remover conteúdo.
- Apagar arquivo só depois de mesclar o conteúdo exclusivo dele em outro lugar e corrigir os links
  que apontavam pra ele — nunca apague uma nota mesclada sem essas duas coisas feitas primeiro.
- `registros_destilaveis` é a categoria com mais ruído (log operacional aparece nela também) — o
  filtro de "é padrão reusável?" é leitura humana disfarçada de Claude, não é pra destilar a lista
  inteira.
- Se o scanner marcar uma nota como `fora_padrao` só por frontmatter, mas a nota também aparecer em
  `notas_longas` ou num grupo de merge, resolva as três coisas na mesma edição em vez de reabrir o
  arquivo três vezes.
