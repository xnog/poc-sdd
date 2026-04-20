# Tasks — Toggle task done/undone

Ordered, verifiable implementation steps. Marked `[x]` **after** each is done and verified. One task at a time.

## api

- [x] Extend startup DDL: add idempotent `ALTER TABLE tasks ADD COLUMN done INTEGER NOT NULL DEFAULT 0`, guarded by `PRAGMA table_info`.
- [x] Update `Task` serialization to include `done` as a JSON boolean (convert from 0/1 at the boundary).
- [x] Update `POST /tasks` to return the new shape (done defaults to `false`).
- [x] Update `GET /tasks` to return `done` for every row; confirm ordering unchanged.
- [x] Add `PATCH /tasks/{id}` accepting `{ "done": boolean }`. Responses: `200` with updated task, `404` if id missing, `422` if body invalid (see Divergences in `design.md`).

## web

- [x] Extend the `Task` type with `done: boolean`.
- [x] Create `<TodoItem task onToggle />` client component: checkbox + title, `line-through` styling when `done`.
- [x] Refactor `<TodoList />` to render `<TodoItem />` per task and expose a `setDone(id, done)` mutator.
- [x] Implement optimistic toggle in `<TodoItem />`: flip local state, `PATCH /tasks/{id}`, revert + inline error on failure.
- [x] Confirm new tasks from `<TodoForm />` render with checkbox unchecked and no strike-through.

## Living specs

- [x] Update `specs/specs/api/todo-list/spec.md` (plan + post-implementation `422` correction).
- [x] Update `specs/specs/web/todo-list/spec.md` (done during planning).

## Tests / Verification

- [x] `pytest` suite on `apps/api` — 13 passed, covering: default `done=false`, toggle done/undone, idempotency, persistence in list ordering, 404 for unknown id, 422 for invalid body.
- [x] `tsc --noEmit` on `apps/web` — clean.
- [ ] Manual browser walkthrough (create → toggle → reload) — not performed in this environment; leaving for the reviewer.

## Notes

- Divergence logged in `design.md`: `PATCH` validation errors return `422` (FastAPI/Pydantic default), not `400`. Living spec updated to match.
- Pydantic coerces some truthy/falsy strings (e.g. `"yes"`) to booleans; the 422 test uses a non-coercible payload (a list) to exercise the validation path deterministically.
- Manual UI verification still pending — no dev server was started in this environment.
