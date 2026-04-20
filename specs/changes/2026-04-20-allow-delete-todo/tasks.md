# Tasks — Allow deleting a task from the TODO list

Ordered, verifiable implementation steps. Marked `[x]` **after** each is done and verified. One task at a time.

## api

- [x] Add `DELETE /tasks/{id}` handler that executes `DELETE FROM tasks WHERE id = ?` and branches on `cursor.rowcount` (→ `204` vs `404`).
- [x] Ensure CORS middleware allows the `DELETE` method for the `web` origin. _(Already permitted via `allow_methods=["*"]` in `apps/api/src/main.py` — no change needed.)_

## web

- [x] Add `deleteTask(id)` client helper that calls `DELETE /tasks/{id}` and resolves/rejects on response status.
- [x] Extend `<TodoList />` with a `deleteTask(id)` mutator doing optimistic remove + rollback on failure.
- [x] Add a delete control (button with accessible name "Delete task") to `<TodoItem />`, wired to an `onDelete(id)` prop.
- [x] Surface inline row-level error when deletion fails and the task is re-inserted.

## Living specs

- [x] Update `specs/specs/api/todo-list/spec.md` to document `DELETE /tasks/{id}` and adjust "Out of scope" / lifecycle wording. _(Done during planning.)_
- [x] Update `specs/specs/web/todo-list/spec.md` to document the delete control, optimistic behavior, and revised "Out of scope". _(Done during planning.)_

## Tests / Verification

- [x] `api`: test `create → delete → list empty`.
- [x] `api`: test `delete unknown id → 404`.
- [x] `api`: test `delete twice → 204 then 404`.
- [ ] `web`: manual browser check — create 2 tasks, delete one, reload, verify deleted one stays gone. _(Not executed here: no browser available in this environment; TypeScript compiles cleanly. Recommend the user run `pnpm dev` in `apps/web` with the API running to verify.)_
- [ ] `web`: manual failure check (e.g. stop the API) — click delete, verify row returns with inline error. _(Same as above.)_

## Notes

_(Free-form notes added during implementation. Discoveries, follow-ups, etc.)_
