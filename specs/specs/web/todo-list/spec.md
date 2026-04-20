---
app: web
domain: todo-list
status: living
---

# Todo List

The `todo-list` domain in the `web` app is the user-facing surface for the TODO feature: a single page where the user types a title, submits it, and sees the growing list of tasks they have created. Each row has a checkbox to mark it done (or undo that) and a delete control to remove it for good. The page is backed by the `api` app's `todo-list` endpoints; `web` holds no persistent state of its own.

---

## User Behavior

On the home page (`/`), the user can:

- Type a task title into a text input and submit it (Enter key or a submit button).
- See their new task appear at the top of the list immediately, not done, without a full page reload.
- Click the checkbox on any task to toggle its done-state. Done tasks render struck-through but remain in the same position in the list.
- Click a delete control on any task to remove it from the list. The row disappears immediately; the deletion is permanent (no undo).
- Reload the browser and still see every task they had created previously (minus any they deleted), each in its last-toggled state.
- See a clear empty-state message when no tasks exist — including after deleting the last remaining task.

The user cannot, in this domain: edit task titles, reorder, filter, search, undo a deletion, or bulk-delete.

---

## Interface

### UI

- **Screen**: `/` — the home page. Hosts the form and the list.
  - Initial render is a server component that fetches the current task list from the API so that a fresh page load shows persisted tasks — including their done-state — without a loading flash.
  - If the initial fetch fails, the page renders with an empty list and a non-blocking inline error message.

- **Component**: `<TodoList initial={Task[]} />` (client) — the stateful container for the feature.
  - Owns the in-memory array, seeded from `initial`.
  - Renders `<TodoForm />` above the list, passing a `prepend` callback so the form can add new tasks on successful creation.
  - Exposes a `setDone(id, done)` mutator to child items and owns the rollback path if a toggle fails.
  - Exposes a `deleteTask(id)` mutator: optimistically removes the task from local state, calls `DELETE /tasks/{id}`, and re-inserts the task at its original index if the call fails.
  - When the list is empty, shows an empty-state message (e.g. "No tasks yet — create your first above."). The empty-state reappears automatically when the last task is deleted.
  - Renders each task as a `<TodoItem />`.

- **Component**: `<TodoForm onCreated={(task) => void} />` (client) — a controlled text input plus a submit button.
  - Submits via `POST /tasks` on the API.
  - While the request is in flight, the input is disabled.
  - On success, the input is cleared and `onCreated` is invoked with the new task (which has `done=false`) so the enclosing `<TodoList />` can prepend it.
  - On error (e.g. validation, network), shows an inline error below the input; the input keeps its content so the user can retry.
  - Blocks submission when the title (trimmed) is empty.

- **Component**: `<TodoItem task={Task} onToggle={(id, done) => Promise<void>} onDelete={(id) => Promise<void>} />` (client) — a single row: checkbox + title + timestamp + delete control.
  - The checkbox reflects `task.done`.
  - Clicking the checkbox triggers an **optimistic** toggle: the component flips the local done-state immediately and calls `onToggle(id, newDone)`, which issues `PATCH /tasks/{id}`.
  - The delete control is a button with accessible name "Delete task". Clicking it calls `onDelete(id)`, which issues `DELETE /tasks/{id}`; there is no confirmation dialog.
  - On toggle failure, the local state is reverted and an inline error is shown on the row; the next successful interaction or page reload reconciles from the server.
  - On delete failure, the row is restored (re-inserted by the parent at its original index) and an inline error is shown on the row.
  - When `task.done` is true, the title is rendered with a strike-through style; the row stays in place in the list.

### API contract consumed

- `GET /tasks` — returns `Task[]`.
- `POST /tasks` body `{ title }` — returns the created `Task` (always `done: false`).
- `PATCH /tasks/{id}` body `{ done }` — returns the updated `Task`.
- `DELETE /tasks/{id}` — returns `204 No Content` on success, `404` if the task no longer exists.
- `Task = { id: number; title: string; done: boolean; created_at: string }`.

API base URL is read from `NEXT_PUBLIC_API_BASE_URL`, default `http://localhost:8000`.

---

## Data

`web` persists nothing of its own in this domain. All state lives in the `api` app's SQLite, including per-task done-state. In-browser state is ephemeral React state seeded from the server-rendered initial fetch.

---

## Rules / Invariants

- Tasks are always rendered newest-first (matches the API's ordering; no client-side re-sorting). Done-state does not affect position.
- The home page always reflects the server-persisted state after a reload, including each task's done-state.
- Title submitted to the API is the raw user input; the API is responsible for trimming and validating.
- A failed create does not mutate the displayed list.
- A failed toggle reverts the checkbox to the last server-confirmed value.
- A failed delete re-inserts the task at its original index; a successful delete removes it permanently from view.

---

## Out of scope

- Editing task titles.
- Undo for a deleted task; "recently deleted" recovery.
- Confirmation dialog before delete.
- Filtering (e.g. "hide done"), searching, pagination.
- Bulk actions ("mark all done", "clear completed", "delete all").
- Offline handling, long-term optimistic queues.
- Authentication, per-user views.
- Any route other than `/`.
