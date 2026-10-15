# Contrato do vault E_Mind

Fonte canônica das convenções de escrita no vault. `E_Mind/08 - Claude/Contrato do Vault —
E_Mind.md` é o **espelho humano** deste arquivo — mudou uma convenção aqui, atualize a nota lá
também (e vice-versa).

## Caminho

```
~/OneDrive/Desktop/E_Mind   (ou a variável de ambiente E_MIND_VAULT)
```

Único lugar onde este caminho pode estar fixo (os scanners leem `E_MIND_VAULT`). Em `CLAUDE.md` de repo vai só o ponteiro
nominal (`## Contexto no Obsidian`).

## Aviso OneDrive

Vault está em OneDrive → arquivos podem estar **online-only** (placeholder, conteúdo não baixado).
Verifique materialização antes de ler/escrever. Se um caminho falhar de forma que não bate com
"arquivo não existe" comum, sinalize online-only ao usuário — nunca invente conteúdo pra compensar.

## Mapa de pastas

| Pasta | Uso | Relevante pra esta skill |
|---|---|---|
| `01 - Notas Atômicas` | Uma ideia/padrão reusável por nota | ✅ sistemático — avaliado a cada `/registro` (ver pipeline 3.1) |
| `02 - Projetos` | Projetos pessoais ativos. **Contexto de projeto vive aqui.** | ✅ núcleo |
| `03 - Trabalho` | Carreira/trabalho. Contexto de projeto de trabalho. | ✅ núcleo |
| `05 - MOCs` | Índices/mapas de navegação | só leitura, nunca editar sem confirmar |
| `06 - Templates` | Templates de nota | referência de formato |
| `07 - Arquivo` | Concluído/inativo | nunca escrever aqui |
| `08 - Claude` | Lógica do Claude: regras, contrato, skills/commands | nunca editar sem pedido explícito |

`02 - Projetos/` e `03 - Trabalho/` são **estáveis** — não renomear pastas de projeto existentes.

## Estrutura de contexto por projeto

```
02 - Projetos/<Projeto>/
├── <Projeto>.md     # hub
├── Arquitetura.md   # fluxo de request, camadas, integrações
├── Decisões.md      # log ADR-lite (append-only)
└── Registros/AAAA-MM-DD-resumo.md   # um por tarefa concluída
```

Projetos de trabalho seguem o mesmo padrão dentro de `03 - Trabalho/<Projeto>/`, mas o hub pode ter
nome próprio (não literalmente `<Projeto>.md`) — **o ponteiro `## Contexto no Obsidian` do repo é a
fonte do caminho e nome do hub reais**, leia-o antes de gravar. Nunca assuma a estrutura por
convenção quando o ponteiro existir e disser outra coisa.

### Topologia de links entre projetos

Projetos **não linkam entre si diretamente**. `Arquitetura.md`/`Decisões.md` linkam só os
`Registros/` do próprio projeto — decisão e arquitetura são conhecimento prático fechado no projeto.
`Registros/` pode linkar `01 - Notas Atômicas/` quando um padrão do trabalho é reusável. Se dois
projetos convergem pra mesma solução, a ponte é a **nota atômica compartilhada**
(`Aplicado em: [[Projeto A]], [[Projeto B]]`) — nunca um link direto projeto→projeto. Ao gravar
Decisões/Arquitetura, não crie `[[Outro Projeto]]`; se achar que o padrão é reusável, sinalize pro
usuário destilar em nota atômica em vez de linkar direto.

## Classificação

O que gravar depende do que a tarefa produziu — mais de uma linha pode se aplicar:

| Aconteceu | Grava em | Modo |
|---|---|---|
| Tarefa/feature/bugfix concluído | `Registros/AAAA-MM-DD-resumo-curto.md` | novo arquivo |
| Decisão arquitetural (ADR), trade-off escolhido | `Decisões.md` | append |
| Mudança de fluxo de request, camadas, integrações | `Arquitetura.md` | edição pontual |
| Status do projeto mudou, novo link relevante | `<Projeto>.md` (hub) | edição pontual, **confirmar antes** |
| Padrão/lição repetido em outro projeto, ou com potencial claro de repetir | `01 - Notas Atômicas/<Nota>.md` | cria (padrão novo) ou atualiza (padrão já coberto), **sempre aditivo — Registro nunca é apagado/resumido** |
| Armadilha, breaking change ou decisão de uso de biblioteca (Context7 ou prática) | `01 - Notas Atômicas/<Nota>.md` com `tags: [biblioteca, <lib>]`, `context7_id`, `versao`, `verificado` | uma armadilha por nota; nunca copiar a documentação |

## Convenções de escrita

- **Idioma:** pt-BR em todo o vault.
- **Frontmatter YAML** no topo de toda nota nova (hub/Arquitetura/Decisões/nota atômica):
  ```yaml
  ---
  criado: AAAA-MM-DD
  status: permanente | rascunho
  tags: [tag1, tag2]
  area: <opcional>
  ---
  ```
- **Frontmatter de Registro** é um formato à parte (template em `06 - Templates/Registro.md`), sem
  `status` (todo registro já é fato concluído por definição):
  ```yaml
  ---
  criado: AAAA-MM-DD
  tipo: registro
  projeto: "[[Nome do Hub]]"
  tags: [tag-semantica-1, tag-semantica-2]
  ---
  ```
  - `projeto`: link pro hub real do projeto (`## Contexto no Obsidian` do repo diz o nome — não
    assuma `<Projeto>.md` literal). Áreas do mesmo trabalho (backend/frontend) compartilham **um
    hub só** (ex. Qiron backend e frontend = mesmo `[[Qiron Robotics]]`) — vivem em subpastas
    simétricas (`<Projeto>/Backend/`, `<Projeto>/Frontend/`) só para Arquitetura/Decisões/Registros;
    a diferença de área é a pasta do registro + `tags`, não um hub separado.
  - `tags`: semânticas e específicas ao conteúdo (`bugfix`, `design-system`, `deploy`), nunca a tag
    genérica `registro` sozinha — o campo `tipo: registro` já cobre isso.
- **Links `[[Nota]]`** sempre que citar outra nota do vault — nunca duplicar o conteúdo dela.
- **Nomenclatura de registro:** `AAAA-MM-DD-resumo-curto.md`, kebab-case, resumo curto e específico
  (não "trabalho-hoje", sim "split-admin-service-5-services").
- **Datas absolutas sempre** — nunca "hoje", "ontem", "essa semana". Resolva pra data real antes de
  gravar.

## Não faça sem confirmar

- Sobrescrever ou apagar nota do usuário.
- Mover ou renomear nota existente.
- Mudar status de projeto em qualquer MOC (`05 - MOCs/`).

Nesses casos: pare, explique o que faria e por quê, espere resposta.
