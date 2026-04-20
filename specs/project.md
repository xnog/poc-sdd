# Project

Living worldview of the monorepo. Updated **only** when something global changes (new app, new core framework, new convention, new domain vocabulary).

---

## Purpose

POC for a Spec-Driven Development (SDD) workflow inside a polyglot monorepo. Validates:
- One source of truth per app (living specs under `specs/specs/<app>/`)
- Change history as append-only folders (`specs/changes/YYYY-MM-DD-slug/`)
- Independent deploys per app based on what actually changed
- Same SDD discipline in two environments: local Claude Code and GitHub Actions `@claude`

---

## Apps

| App | Role | Stack |
|---|---|---|
| `web` | User-facing frontend | Next.js 15 (App Router), React 19, TypeScript |
| `api` | Backend HTTP API | FastAPI, SQLite, Python 3.12 |

Each app is autonomous: its own deploy pipeline, its own living specs, its own domain folders.

## Architecture

```
[user] → web (Next.js) → api (FastAPI) → SQLite (local file)
```

- `web` consumes `api` over HTTP (JSON).
- No shared state between apps beyond the HTTP contract.
- No message queue, no caching layer, no auth (POC scope).

---

## Monorepo tooling

- **Moon** orchestrates tasks across apps. Each app declares its tasks in `apps/<app>/moon.yml`.
- `moon ci --affected` detects which apps changed (via git diff) and runs only their tasks.
- `moon run :deploy --affected` routes deploy to affected apps only. In this POC, deploy scripts are fake (just echo what would happen).

## CI/CD

- **CI** (`.github/workflows/ci.yml`): runs `moon ci --affected` on PRs.
- **Deploy** (`.github/workflows/deploy.yml`): on push to `main`, runs `moon run :deploy --affected`. Deploys are currently fake scripts.
- **`@claude` action** (`.github/workflows/claude.yml`): responds to `@claude` mentions in issues/PRs. Instructions for git/PR behavior live there, not in `CLAUDE.md`.

---

## Code standards

### Python (`apps/api`)
- Python 3.12+
- Formatter/linter: `ruff`
- Type checker: `mypy` (strict for new code)
- Dependency manager: `uv` or `pip` + `pyproject.toml`

### TypeScript (`apps/web`)
- Node 20+
- Formatter/linter: `biome` (or Next.js default eslint + prettier)
- Package manager: `pnpm`

### Naming
- Files: kebab-case (`todo-list.tsx`, `todo_list.py`)
- Directories: kebab-case
- Domain folders in specs: short nouns, kebab-case (`todo-list`, `auth`)

---

## Domain vocabulary

_(Grows as domains are introduced. Each term is defined once here and referenced across specs.)_

Examples (to be filled as domains are added):
- **Task**: (stub) an item in a TODO list owned by a user.

---

## Decisions (global)

Append one bullet per decision that applies project-wide. Specific technical decisions for a single change live in that change's `design.md`.

- Using **Moon** for monorepo orchestration — polyglot-native, low setup, supports affected detection out of the box.
- Using **SQLite** for the POC — zero infra, single file, good enough for the behaviors being validated. To be reconsidered if multi-writer or scale requirements appear.
- **No ORM** in `apps/api` for the POC — raw SQL via `sqlite3` stdlib to keep the surface minimal. Revisit if schema complexity grows.
- **SDD discipline enforced via `CLAUDE.md` + skills** — no external framework, markdown only. See `CLAUDE.md`.
