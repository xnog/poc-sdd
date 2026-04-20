---
app: api
domain: todo-list
status: living
---

# Todo List

The `todo-list` domain in the `api` app owns the persistent collection of tasks: the records users create, read back, toggle between "done" and "not done", and delete. It exposes a small HTTP surface (create, list, toggle, delete) backed by a single SQLite table. There is no ownership model. A task exists from creation until it is explicitly deleted; while it exists, it is always returned by the list endpoint in reverse-chronological order, carrying its current done-state.

---

## User Behavior

The API client (today: the `web` app) can:

- Create a task by sending a non-empty title. A newly created task is always **not done**.
- List all tasks, ordered from most recently created to oldest. Each task carries its current done-state.
- Toggle a task's done-state by id — set it to `true` or `false`. The operation is idempotent: setting `done=true` on an already-done task is a no-op success.
- Delete a task by id. The row is permanently removed; subsequent list calls do not return it, and subsequent operations on the same id return `404`.

There is no update of the title and no per-user scoping in this domain.

---

## Interface

### Endpoints

| Method | Path | Purpose | Success | Errors |
|---|---|---|---|---|
| POST | `/tasks` | Create a new task (`done=false`) | `201` with the full task record | `400` if `title` is missing, empty, or whitespace-only |
| GET | `/tasks` | List all tasks, newest first | `200` with an array of task records | — |
| PATCH | `/tasks/{id}` | Set the task's done-state | `200` with the updated task record | `422` if body is missing `done` or `done` is not a boolean (FastAPI/Pydantic schema validation); `404` if no task has that id |
| DELETE | `/tasks/{id}` | Permanently remove the task | `204` with empty body | `404` if no task has that id |

Request/response shapes:

```json
// POST /tasks request
{ "title": "Buy milk" }
```

```json
// 201 response
{
  "id": 42,
  "title": "Buy milk",
  "done": false,
  "created_at": "2026-04-20T14:32:10"
}
```

```json
// GET /tasks 200 response
[
  { "id": 43, "title": "Call mom", "done": false, "created_at": "2026-04-20T14:35:00" },
  { "id": 42, "title": "Buy milk", "done": true,  "created_at": "2026-04-20T14:32:10" }
]
```

```json
// PATCH /tasks/42 request
{ "done": true }
```

```json
// PATCH /tasks/42 200 response
{
  "id": 42,
  "title": "Buy milk",
  "done": true,
  "created_at": "2026-04-20T14:32:10"
}
```

```http
// DELETE /tasks/42
// 204 No Content
```

CORS allows the `web` dev origin (`http://localhost:3000`) for the methods in use (`GET`, `POST`, `PATCH`, `DELETE`).

---

## Data

Single table in SQLite. Database file path comes from the `POC_SDD_DB_PATH` env var, defaulting to `./data/poc-sdd.db` relative to `apps/api`.

```sql
CREATE TABLE IF NOT EXISTS tasks (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  title      TEXT    NOT NULL,
  done       INTEGER NOT NULL DEFAULT 0,
  created_at TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON tasks(created_at DESC);
```

Startup also runs an idempotent migration for pre-existing databases:

```sql
-- Only executed if the `done` column is not yet present (checked via PRAGMA table_info).
ALTER TABLE tasks ADD COLUMN done INTEGER NOT NULL DEFAULT 0;
```

- **Invariants**: `title` is non-empty after trimming; `done` is `0` or `1`; `created_at` is a UTC ISO-8601 string.
- **Serialization**: `done` is exposed over HTTP as a JSON boolean; the 0/1 representation is internal.
- **Lifecycle**: rows are inserted by `POST /tasks` with `done=0`. `PATCH /tasks/{id}` updates `done`. `DELETE /tasks/{id}` hard-deletes the row. `title` and `created_at` are never modified.

---

## Rules / Invariants

- A task always has a non-empty, trimmed title.
- A freshly created task always has `done=false`.
- `created_at` is set by the database at insert time, in UTC.
- `GET /tasks` is ordered by `created_at DESC`, with `id DESC` as a tie-breaker. Done-state does **not** affect ordering.
- `PATCH /tasks/{id}` is idempotent: applying the same `done` value yields the same end state and still returns `200`.
- `DELETE /tasks/{id}` is a hard delete: the row is removed immediately; re-issuing the same delete returns `404`.
- The schema is created on API startup if it does not exist; startup is idempotent and also applies the `done`-column migration in place if needed.

---

## Out of scope

- Editing the title.
- Undo / recovery of deleted tasks (deletion is hard and permanent).
- Bulk delete ("clear completed", "delete all").
- Tracking *when* a task was completed or deleted (no `completed_at` / `deleted_at` column).
- Per-user ownership, authentication, authorization.
- Pagination, search, filtering by done-state, tagging.
- Any non-HTTP interface (no CLI, no events).
