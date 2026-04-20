# Design — Initial TODO list

Technical approach for delivering create + list of tasks end-to-end, with SQLite persistence.

## Approach per app

### `api`

- Add a `todo-list` domain module: `apps/api/src/todo_list.py` (router) + `apps/api/src/db.py` (SQLite connection helper).
- Endpoints on the existing FastAPI app:
  - `POST /tasks` — body `{ "title": str }`. Trims whitespace; rejects empty with `400`. Inserts row, returns `201` with full record.
  - `GET /tasks` — returns `[{ id, title, created_at }, ...]` ordered by `created_at DESC, id DESC`.
- Persistence: single SQLite file. Path configurable via env var `POC_SDD_DB_PATH`, default `./data/poc-sdd.db` (relative to `apps/api`). The `data/` directory is created if missing and added to `.gitignore`.
- Schema is created on startup via `CREATE TABLE IF NOT EXISTS` — no migration tool for the POC (consistent with `project.md`: no ORM, raw `sqlite3`).
- CORS: allow `http://localhost:3000` so the Next.js dev server can call the API directly.
- Library choices: `sqlite3` stdlib (no ORM), `pydantic` (ships with FastAPI) for request/response models.

Key trade-offs:
- No migration tool — acceptable because schema is trivial and POC scope. Revisit when we add a second table or a column.
- SQLite file in the working directory — acceptable for local dev; production path would be configured via env var.

### `web`

- Single-page flow on `/` (existing `apps/web/src/app/page.tsx`, rewritten).
- Component tree:
  - `page.tsx` (server component) — fetches initial list from the API at render time so reloads show persisted state immediately.
  - `TodoForm` (client component) — controlled input + submit button, calls `POST /tasks`, on success prepends the new task to the list.
  - `TodoList` (client component) — receives initial tasks as prop, owns the in-memory list state, renders items newest-first. Empty state when list is empty.
- State: local React state in `TodoList`, seeded from server-fetched initial data. No global store, no SWR/React Query for the POC.
- API base URL read from `NEXT_PUBLIC_API_BASE_URL`, default `http://localhost:8000`.
- Styling: minimal inline / CSS modules — visual polish is out of scope.

Key trade-offs:
- Server-fetched initial list + client-managed updates keeps the POC simple while still showing persistence after reload. Switching to a data-fetching library is deferred until a feature actually needs it.
- Direct browser → API calls (no Next.js route handler proxy) — simpler for the POC; revisit if we need to hide the API URL or add auth.

## Data changes

```sql
CREATE TABLE IF NOT EXISTS tasks (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  title      TEXT    NOT NULL,
  created_at TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON tasks(created_at DESC);
```

- `created_at` stored as ISO-8601 UTC string (SQLite `datetime('now')`). String comparison preserves chronological order.
- No backfill needed — table is new.
- Not a breaking change — first version of the schema.

## Key decisions

- **Integer autoincrement ID over UUID**: simpler for the POC, trivial to inspect, no uuid dependency. Revisit if we expose IDs externally or shard.
- **`created_at` as TEXT (ISO-8601)**: native SQLite pattern, avoids timezone ambiguity, sorts lexicographically. Alternative (Unix epoch integer) rejected for readability.
- **No soft-delete column**: deletion isn't in scope. Adding it speculatively would violate "spec reflects what the system does".
- **CORS wide-open to localhost:3000 only**: matches the documented architecture (`web` → `api` over HTTP). Production hardening is out of scope.
- **DB path via env var with sensible default**: lets tests point to a temp file without code changes.

## Alternatives considered

- **Server-side rendering the list via Next.js route handlers proxying the API**: rejected, adds a layer without value for the POC.
- **In-memory list on the API**: rejected, explicitly violates the acceptance criterion of surviving restarts.
- **SQLAlchemy / ORM**: rejected per `project.md` — raw `sqlite3` is sufficient for one table.

## Risks

- SQLite file permissions on the deploy target — not relevant for the POC (fake deploy), flagged for later.
- Concurrent writes — SQLite locks the file; at POC scale (single user, single process) this is a non-issue.

---

<!-- Appended only during implementation if reality diverges from the agreed plan -->
## Divergences

### Composition of `<TodoForm />` and `<TodoList />`

The plan described `<TodoForm />` and `<TodoList />` as two siblings with "shared state at the page level". Because `page.tsx` is a Next.js server component it cannot hold React state, so the state must live in a client boundary. The implementation realizes this by having `<TodoList initial={...} />` own the in-memory array (as the spec says) and render `<TodoForm />` above its items within the same client component, passing a `prepend` callback via props.

Behavior is unchanged — the page still server-fetches the initial list, the form still lives above the list on `/`, the list still owns the array seeded from `initial`. Only the component composition is slightly different: `page.tsx` renders `<TodoList />` instead of rendering `<TodoForm />` and `<TodoList />` side-by-side. The living web spec has been adjusted to match.
