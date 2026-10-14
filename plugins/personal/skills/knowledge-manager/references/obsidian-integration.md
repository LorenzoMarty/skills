# Integração com Obsidian (vault E_Mind)

Regra máxima: **o vault é conhecimento humano permanente. Nunca cache da IA. Nunca documentação redundante.** Esta skill não escreve no vault — delega para o skill `claude-obsidian`, que já conhece as regras de frontmatter, nomenclatura (`AAAA-MM-DD-resumo-curto.md`) e estrutura de pastas do vault (ver `Contrato do Vault — E_Mind.md` e `Regras de Trabalho.md`, ambos em `E_Mind/08 - Claude/`).

## Papel do Knowledge Manager aqui

Só **ler índice**, nunca ler o vault inteiro:

- `index/obsidian-index.json` local ao projeto: mapa leve (pasta do vault correspondente a este projeto + lista de docs com título/tags/caminho, sem conteúdo).
- Esse índice é construído no bootstrap (se o índice global do vault já existir) ou preenchido lazy, na primeira vez que a cascata de busca (`search-order.md` nível 3) precisar dele.
- Nunca reconstruir o índice inteiro do vault por causa de uma tarefa — só adicionar/atualizar a entrada relevante quando descoberta.

## Quando abrir um doc do vault de verdade

Só quando o índice apontar um doc candidato específico E a cascata de busca chegou no nível 3 sem resposta nos níveis anteriores. Abrir só aquele doc (via Read ou via skill `claude-obsidian` se a leitura exigir entender a estrutura do vault).

## Quando sugerir escrita no vault (critério ADR-worthy)

Sinalizar ao usuário — nunca escrever sozinho — quando, durante uma tarefa, descobrir:

- Um padrão novo que passa a ser usado por **2 ou mais conceitos/contextos** (ex.: um novo jeito de fazer paginação que se repete em duas telas).
- Uma decisão arquitetural (ex.: trocar de REST pra GraphQL num módulo).
- Uma regra de negócio nova ou alterada.
- Uma mudança que afeta mais de um contexto existente no cache.

Se algum desses critérios bater, perguntar ao usuário se quer documentar, e se sim, acionar o skill `claude-obsidian` passando o conteúdo (não formatar o frontmatter/nome de arquivo aqui, isso é responsabilidade dele).

## O que nunca fazer

- Nunca criar arquivo no vault diretamente por esta skill.
- Nunca duplicar conteúdo que já existe em um doc do vault dentro de um `context.md` do cache — o `context.md` deve apenas **apontar** (`docs: [...]`) pro doc do vault, não copiar o texto.
- Nunca marcar `docs` staleness aqui — se o doc do vault mudou, quem decide relevância é o próprio vault/usuário; o cache só reflete o caminho.
