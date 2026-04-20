# Plano — POC SDD + Monorepo

## 1. Objetivo

Provar um modelo de monorepo poliglota com disciplina de **Spec-Driven Development** (SDD) ensinada ao Claude via `CLAUDE.md` + skills, funcionando em dois ciclos (local e GitHub Actions) **sem dependência de framework externo**.

A POC usa Next.js + FastAPI + SQLite como apps de exemplo, mas o padrão foi desenhado pra escalar pra plataforma + N MCPs + N agentes.

## 2. Princípios

1. **Spec antes de código** — nenhuma implementação começa sem uma change aprovada
2. **Duas fases explícitas** — `plan-change` → aprovação humana → `implement-change`
3. **Tudo no mesmo PR** — change + spec viva atualizada + código, sem step pós-merge
4. **Histórico imutável** — changes antigas nunca são editadas; correção = nova change
5. **Sem framework** — regras no `CLAUDE.md` + skills, markdown puro, zero lock-in
6. **Separação clara** — regras SDD são agnósticas de ambiente; regras de git/PR vivem no workflow do GitHub

## 3. Invariantes (regras duras)

Inegociáveis — codificadas no `CLAUDE.md`:

> **I1.** Toda mudança de comportamento começa com uma pasta `specs/changes/YYYY-MM-DD-slug/`. Sem change, não tem código.
>
> **I2.** A spec viva (`specs/specs/<app>/<dominio>/spec.md`) é atualizada **na fase de planejamento**, refletindo o estado **proposto** do sistema. Cria se o domínio é novo, edita se já existe.
>
> **I3.** `specs/project.md` é atualizado **apenas** quando a change afeta algo global (stack, arquitetura, convenção ou novo app).
>
> **I4.** Entre `plan-change` e `implement-change` há **gate humano obrigatório**. Sem aprovação, Claude não escreve código.
>
> **I5.** Changes antigas (já merged) são **imutáveis**. Para corrigir, cria-se uma nova change.

## 4. Decisões

| Tema | Decisão | Racional |
|---|---|---|
| Monorepo tool | **Moon** | Poliglota nativo, `moon ci --affected` out-of-the-box |
| SDD | **Framework próprio** inspirado em OpenSpec/Kiro/spec-kit | Zero lock-in, apenas markdown versionado |
| Naming de changes | `YYYY-MM-DD-slug` | Evita conflitos entre devs em paralelo, ordena cronologicamente |
| Pasta raiz SDD | `specs/` | Direto, auto-explicativo |
| Estrutura de specs vivas | `specs/specs/<app>/<dominio>/spec.md` | Cada app é produto autônomo; domínios isolados por app |
| Estrutura de changes | `specs/changes/YYYY-MM-DD-slug/` | Uma change é um evento único, mesmo quando cross-app |
| Delta markers | **Não usar** | `git diff` do PR já é o delta |
| ADR separado | **Não existe** | Decisões vivas em `project.md`; racional específico no `design.md` da change |
| Arquivos por change | 3: `proposal.md`, `design.md`, `tasks.md` | Separação semântica: produto / tech / execução |
| Skills | `plan-change`, `implement-change` | Procedimentos detalhados carregados sob demanda |
| Feature de exemplo | TODO list CRUD | Exercita full-stack simples |
| Deploy (POC) | **Fake** via scripts `deploy.sh` | Prova o roteamento de deploy afetado; evolui depois |

## 5. Estrutura final do repo

```
CLAUDE.md                                  # invariantes SDD + ponteiros pras skills
PLAN.md                                    # este documento

.claude/
  skills/
    plan-change/
      SKILL.md                             # procedimento da fase de planejamento
    implement-change/
      SKILL.md                             # procedimento da fase de implementação

specs/
  project.md                               # worldview vivo: stack, arquitetura, domínio
  _templates/
    spec.md                                # template de spec viva
    change/
      proposal.md
      design.md
      tasks.md
  specs/                                   # estado ATUAL do sistema, por app
    web/
      todo-list/spec.md
    api/
      todo-list/spec.md
  changes/                                 # histórico append-only
    2026-04-20-initial-todo-list/
      proposal.md
      design.md
      tasks.md

apps/
  web/                                     # Next.js
    moon.yml
    deploy.sh                              # fake deploy
  api/                                     # FastAPI + SQLite
    moon.yml
    deploy.sh                              # fake deploy

.github/
  workflows/
    claude.yml                             # action do @claude (instruções de git/PR)
    ci.yml                                 # moon ci --affected (testes, lint)
    deploy.yml                             # moon run :deploy --affected

.moon/
  workspace.yml
  toolchain.yml
```

## 6. Separação de responsabilidades

### `CLAUDE.md` — universal, sempre em contexto
- Invariantes (seção 3)
- Estrutura de pastas (visão geral)
- Matriz de permissões por tipo de arquivo
- Naming (`YYYY-MM-DD-slug`)
- Ponteiros: "pra planejar, use skill `plan-change`; pra implementar, use `implement-change`"
- **Zero menção a** git, branch, commit, PR, issue
- **Enxuto** — detalhes procedurais moram nas skills

### Skills — carregadas sob demanda

**`.claude/skills/plan-change/SKILL.md`** — dispara quando usuário pede feature/mudança nova.
- Perguntas pra fechar ambiguidade (escopo, apps afetados)
- Cria `specs/changes/YYYY-MM-DD-slug/{proposal,design,tasks}.md`
- Cria **ou** edita `specs/specs/<app>/<dom>/spec.md` refletindo estado proposto
- Edita `specs/project.md` se houve mudança global
- **Pausa e pede aprovação** — não toca em código

**`.claude/skills/implement-change/SKILL.md`** — dispara quando há change aprovada pendente.
- Lê `tasks.md` da change atual
- Implementa código em `apps/`
- Marca `[x]` em `tasks.md` conforme progride
- Se implementação revela necessidade de ajuste, re-edita spec viva no mesmo PR e comunica
- Reporta conclusão

### `.github/workflows/claude.yml` — só ambiente GitHub
- Triggers: `@claude planeja X` / `@claude implementa X`
- Criação de branch, abertura de PR, comentário em issue
- Labels (`spec-review`, `implementation`)
- Regras de segurança (não mexer em main, não force-push)
- **Herda** regras SDD lendo `CLAUDE.md` + skills

### `.github/workflows/ci.yml` — validação
- `moon ci --affected` em PRs
- Testes, lint, type-check dos projetos impactados

### `.github/workflows/deploy.yml` — deploy (fake nesta POC)
- Dispara em push em `main`
- `moon run :deploy --affected` → executa `deploy.sh` só dos apps mudados
- Logs mostram quais apps teriam sido deployados

## 7. Regras de edição de arquivos

| Arquivo | Editável? | Fase | Quando |
|---|---|---|---|
| `specs/changes/<atual>/proposal.md` | ✅ | plan | Antes da aprovação. Depois congela. |
| `specs/changes/<atual>/design.md` | ✅ | plan | Antes da aprovação. Depois congela. |
| `specs/changes/<atual>/tasks.md` | ✅ | plan + implement | Criado no plan; marcado `[x]` no implement. |
| `specs/specs/<app>/<dom>/spec.md` | ✅ criar ou editar | plan (principal) / implement (ajuste) | **Sempre** que change altera comportamento. Reflete estado proposto no plan; reajusta no implement se divergir. |
| `specs/project.md` | ✅ | plan | **Só** se change afeta stack/arquitetura/convenção global |
| Código em `apps/*` | ✅ | implement | Só após aprovação humana |
| `specs/changes/<antigas>/*` | ❌ **nunca** | — | Imutável. Corrigir = nova change. |

## 8. Fluxo de uma feature — duas fases

### Fase 1: `plan-change`

1. Usuário pede feature
2. Claude invoca skill `plan-change`
3. Skill cria:
   - `specs/changes/YYYY-MM-DD-slug/proposal.md` (quê + porquê)
   - `specs/changes/YYYY-MM-DD-slug/design.md` (como)
   - `specs/changes/YYYY-MM-DD-slug/tasks.md` (checklist `[ ]`)
   - `specs/specs/<app>/<dom>/spec.md` criado/editado com estado **proposto**
   - `specs/project.md` editado se mudança é global
4. Claude **pausa** e apresenta pra aprovação

### Gate humano

Usuário revisa a change e as specs vivas propostas. Aprova, pede ajustes, ou rejeita.

### Fase 2: `implement-change`

1. Com aprovação explícita, Claude invoca skill `implement-change`
2. Lê `tasks.md` e specs vivas (já refletem estado alvo)
3. Escreve código em `apps/` satisfazendo o contrato da spec
4. Marca `[x]` em `tasks.md` conforme avança
5. Se precisar ajustar spec viva (edge case não previsto), re-edita **no mesmo PR** e comunica
6. Reporta conclusão

### Ciclo local vs GitHub

- **Local**: gate = usuário digita "aprovado" no chat. Claude não toca em git.
- **GitHub (`@claude`)**: gate = PR com label `spec-review` aprovado pelo humano. Workflow cuida de branch/PR/comments.

## 9. Mudanças cross-app

Uma change que toca múltiplos apps gera **uma única** pasta de change, mas edita/cria **múltiplas** specs vivas:

```
specs/changes/2026-04-22-add-rate-limiting/
  proposal.md                      # motivação única, scope: [platform, github-mcp]
  design.md                        # design global
  tasks.md

specs/specs/platform/rate-limiting/spec.md     # criado/editado
specs/specs/github-mcp/rate-limiting/spec.md   # criado/editado
```

Tudo no mesmo PR. Moon detecta paths afetados e roteia deploy apenas para os apps envolvidos.

## 10. Exceção: mudanças triviais

Não precisam passar pelas duas fases:
- Typo em comentário
- Rename de variável local
- Formatação / lint fix
- Bugfix óbvio de 1-2 linhas sem mudança de comportamento observável

**Qualquer mudança de comportamento externo** (API, UI, dados persistidos, contratos) — sempre passa pelo fluxo completo.

## 11. Plano de implementação (ordem)

1. **`CLAUDE.md`** — invariantes + ponteiros pras skills (enxuto)
2. **`.claude/skills/plan-change/SKILL.md`** — procedimento da fase 1
3. **`.claude/skills/implement-change/SKILL.md`** — procedimento da fase 2
4. **`specs/project.md`** — worldview inicial da POC
5. **`specs/_templates/`** — template de spec viva + template de change (3 arquivos)
6. **Primeira change de exemplo**: `specs/changes/2026-04-20-initial-todo-list/` completa
7. **Specs vivas iniciais**: `specs/specs/api/todo-list/spec.md` e `specs/specs/web/todo-list/spec.md`
8. **Setup Moon**: `.moon/workspace.yml`, `.moon/toolchain.yml`
9. **Scaffold `apps/api`** — FastAPI + SQLite, CRUD de TODO, `moon.yml`, `deploy.sh` fake
10. **Scaffold `apps/web`** — Next.js consumindo a api, `moon.yml`, `deploy.sh` fake
11. **`.github/workflows/ci.yml`** — `moon ci --affected`
12. **`.github/workflows/deploy.yml`** — `moon run :deploy --affected` (fake logs)
13. **`.github/workflows/claude.yml`** — action do `@claude` com instruções de git/PR

## 12. Critérios de "POC pronta"

- [ ] `CLAUDE.md` existe e é lido por Claude local
- [ ] Skills `plan-change` e `implement-change` instaladas e auto-invocáveis
- [ ] Estrutura de pastas criada conforme seção 5
- [ ] 1 change de exemplo completa (spec viva atualizada + código implementado)
- [ ] TODO list funcionando end-to-end (web ↔ api ↔ sqlite) localmente
- [ ] `moon ci --affected` detecta e roda tasks corretas
- [ ] `moon run :deploy --affected` imprime logs fake apenas dos apps tocados no commit
- [ ] Action `@claude` responde em issue de teste seguindo as duas fases

## 13. Fora de escopo desta POC

- Autenticação real
- Deploy real em cloud
- Multi-tenancy
- Observabilidade / logging estruturado
- Testes E2E completos (só smoke tests)
- Geração automática de tipos TS a partir do OpenAPI da FastAPI (nice-to-have futuro)
