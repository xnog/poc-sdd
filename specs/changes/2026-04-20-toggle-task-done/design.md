# Design — Toggle task done/undone

Technical approach. Written for an engineer reviewer.

## Approach per app

### `api`
- New endpoint: `PATCH /tasks/{id}` with body `{ "done": boolean }`. Returns `200` with the updated task record, `404` if the id does not exist, `400` if `done` is missing or not a boolean.
- Schema change: add `done INTEGER NOT NULL DEFAULT 0` to the `tasks` table (SQLite stores booleans as 0/1). Existing rows backfill automatically via the `DEFAULT 0`.
- `POST /tasks` continues to insert with `done = 0` implicitly; response shape now includes `done: false`.
- `GET /tasks` response shape now includes `done` for every row. Ordering is unchanged (`created_at DESC, id DESC`).
- Startup DDL is extended with an idempotent `ALTER TABLE tasks ADD COLUMN done ...` guarded by a check against `PRAGMA table_info`, so existing dev DBs upgrade in place without manual migration.
- Key trade-offs: a `PATCH` with a `done` body (rather than a dedicated `POST /tasks/{id}/complete` + `/uncomplete` pair) keeps the surface small and symmetrical for a toggle.

### `web`
- `Task` type gains `done: boolean`.
- `<TodoList />` passes each item to a new `<TodoItem task={Task} onToggle={(id, done) => Promise<void>} />` (client) component which renders the checkbox + title.
  - When the user clicks the checkbox, the item optimistically flips its own `done` flag, calls `PATCH /tasks/{id}` with the new value, and on failure reverts the checkbox and shows an inline error on the row.
- `<TodoList />` owns the list state and exposes a `setDone(id, done)` mutator used by `<TodoItem />` for the optimistic update and rollback.
- Done items get a `line-through` style on the title (Tailwind `line-through text-gray-500` or equivalent). The item itself stays in the list at the same position.
- Key trade-offs: optimistic toggle (with rollback) keeps the UI snappy; the previous domain already used non-optimistic create, but for a toggle the latency would be more visible per click.

## Data changes

```sql
-- New column, added idempotently at startup (guarded by PRAGMA table_info check).
ALTER TABLE tasks ADD COLUMN done INTEGER NOT NULL DEFAULT 0;
```

- Backfill: not needed — `DEFAULT 0` applies to existing rows.
- Breaking change to API response shape: `Task` now has an extra `done` field. Only known consumer is `web`, updated in the same change. Additive, so older clients that ignore unknown fields would still work, but we bump both sides together.

## Key decisions

- **`done` as INTEGER 0/1**: SQLite has no native boolean; staying with the idiomatic 0/1 avoids a serializer shim. API layer converts to/from JS boolean at the boundary.
- **Single `PATCH` endpoint, not two verbs**: the operation is symmetric (set a boolean); two endpoints would imply asymmetric semantics we don't want.
- **Optimistic UI**: toggle is a high-frequency, low-risk action; waiting for a round-trip per click would feel laggy. Rollback on error is cheap.
- **No `completed_at`**: out of scope per proposal; if later needed, it's an additive column and a new change.

## Alternatives considered

- **Soft-delete style `completed_at` timestamp instead of `done` boolean**: richer but not requested; adds nullability semantics and a sort-order question. Rejected to keep the change minimal.
- **Two endpoints `POST /tasks/{id}/complete` and `/uncomplete`**: more RPC-style but doubles surface area for a trivial toggle.
- **Removing done tasks from the list**: explicitly rejected by the proposal — users want to see what they finished.

## Risks

- Existing dev databases need the `ALTER TABLE` path to run on startup. Mitigated by the `PRAGMA table_info` check: if `done` is already present, the ALTER is skipped.
- Optimistic update can briefly show an inconsistent state if the network flaps; rollback + inline error is the defined behavior, and the next reload reconciles from the server.

---

<!-- Appended only during implementation if reality diverges from the agreed plan -->
## Divergences

- **Validation error code on `PATCH /tasks/{id}`**: design said `400` for missing/invalid `done`. FastAPI/Pydantic returns `422` for body schema validation by default, consistent with the rest of the API surface. Living spec updated to `422`; no custom exception handler was added.
