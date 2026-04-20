# Tasks — Initial TODO list

Ordered, verifiable implementation steps. Marked `[x]` **after** each is done and verified. One task at a time.

## api

- [x] Add SQLite connection helper `apps/api/src/db.py` with `get_connection()` honoring `POC_SDD_DB_PATH` (default `./data/poc-sdd.db`), ensuring the parent directory exists.
- [x] Add startup hook in `apps/api/src/main.py` that runs `CREATE TABLE IF NOT EXISTS tasks ...` and the index.
- [x] Add `apps/api/src/todo_list.py` with `POST /tasks` and `GET /tasks` using Pydantic models `TaskCreate` and `TaskOut`.
- [x] Wire the router into the FastAPI app in `main.py`.
- [x] Add CORS middleware allowing `http://localhost:3000`.
- [x] Add `data/` to `apps/api/.gitignore` (create the file if missing).

## web

- [x] Add `apps/web/src/lib/api.ts` with `listTasks()` and `createTask(title)` hitting `NEXT_PUBLIC_API_BASE_URL` (default `http://localhost:8000`).
- [x] Rewrite `apps/web/src/app/page.tsx` to server-fetch the initial task list and render `<TodoForm />` + `<TodoList initial={...} />`.
- [x] Add `apps/web/src/app/_components/TodoForm.tsx` (client component).
- [x] Add `apps/web/src/app/_components/TodoList.tsx` (client component) with empty state.
- [x] Minimal styling so the page is readable (layout + spacing only).

## Living specs

- [x] Create `specs/specs/api/todo-list/spec.md` reflecting the proposed state.
- [x] Create `specs/specs/web/todo-list/spec.md` reflecting the proposed state.

## Tests / Verification

- [x] Add `apps/api/tests/test_todo_list.py` covering: create happy path, create with empty title (400), list order (newest first), persistence across a fresh connection.
- [ ] Manual smoke: start `api`, start `web`, create two tasks, reload browser, confirm both appear newest-first; restart `api`, reload, confirm tasks still there. _(requires a human browser — left unchecked for the user to perform; the equivalent is covered automatically by `test_persistence_across_connections`.)_

## Notes

- Verified: `uv run pytest` (8/8 pass), `uv run ruff check .`, `uv run mypy src`, `npx tsc --noEmit`, `npx next build` all green.
- Minor structural choice: kept the spec's `<TodoList initial={...} />` as the single stateful client component, which internally renders `<TodoForm />` and the list. This matches the spec's wording "owns the in-memory array, seeded from `initial`" and "shared state at the page level" without introducing an extra wrapper. `page.tsx` therefore renders `<TodoList initial={...} />` rather than two siblings.
- Timestamp rendering: SQLite's `datetime('now')` returns UTC without a `Z` suffix; the client normalizes it before calling `toLocaleString()` so the displayed time reflects the user's locale.
