# Design — Allow deleting a task from the TODO list

Technical approach. Written for an engineer reviewer.

## Approach per app

### `api`

- Add endpoint `DELETE /tasks/{id}`:
  - On success: `204 No Content`, empty body.
  - On missing id: `404` with FastAPI's default JSON error shape (same style as `PATCH /tasks/{id}`).
- Implementation: a single `DELETE FROM tasks WHERE id = ?` executed in the existing SQLite connection layer. Use `cursor.rowcount` to distinguish hit (→ 204) from miss (→ 404).
- No schema change, no migration. Rows are hard-deleted.
- CORS already allows the `web` origin for all methods in use; verify `DELETE` is permitted (extend allow-list if needed).
- Tests: one happy-path test (`create → delete → list is empty`), one 404 test (`delete unknown id`), one idempotency-ish test (`delete same id twice → 204 then 404`).

### `web`

- Extend `<TodoItem />` with a delete control (button with label "Delete" or a trash glyph; accessible name: "Delete task").
- Add an `onDelete(id) => Promise<void>` prop passed from `<TodoList />`.
- `<TodoList />` owns the list state and gains a `deleteTask(id)` mutator:
  - Optimistic: splice the task out of local state immediately.
  - Call `DELETE /tasks/{id}`.
  - On non-2xx / network error: re-insert the task at its original index and surface an inline error on the row.
- When deletion leaves the list empty, the existing empty-state message is rendered automatically (already keyed off `tasks.length === 0`).
- No confirmation modal in this change.

## Data changes

No schema migration. Rows are removed with:

```sql
DELETE FROM tasks WHERE id = ?;
```

- Backfill needed? No.
- Breaking change? No — adding a method to an existing resource.

## Key decisions

- **Hard delete over soft delete**: the domain has no history/audit needs yet; a `deleted_at` column would add complexity with no current product use. If "undo" is added later, revisit.
- **`204 No Content` over `200` with body**: the client does not need the deleted record back; `204` is the conventional REST signal and keeps the contract minimal.
- **Optimistic UI over pessimistic**: matches the pattern already used for `PATCH /tasks/{id}` toggle, so the feature feels instant and error handling is consistent across the component.
- **No confirmation dialog**: MVP scope. The proposal explicitly defers undo; if users report accidental deletions we can add confirm or an undo toast as a follow-up.

## Alternatives considered

- **Soft delete (`deleted_at` column + filtered reads)**: rejected — adds schema, migration, and query complexity for a capability (undo/audit) not requested.
- **Confirmation modal before delete**: rejected for MVP — blocks the happy path; can be revisited if deletion proves error-prone.
- **Pessimistic UI (wait for 204 before removing row)**: rejected — inconsistent with the existing optimistic toggle; noticeably laggy on slow networks.

## Risks

- A user clicks delete by accident and there is no undo — acknowledged trade-off for MVP.
- If the API is slow, the row vanishes before the request completes; a subsequent failure re-inserts it, which could be visually jarring. Mitigated by showing an inline error on the restored row.

---

<!-- Appended only during implementation if reality diverges from the agreed plan -->
## Divergences

_None so far._
