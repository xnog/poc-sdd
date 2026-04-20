---
title: Allow deleting a task from the TODO list
scope: [api, web]
status: proposed
---

# Allow deleting a task from the TODO list

## Motivation

Today a task, once created, exists forever. Users who typo a title, change their mind, or finish a task they no longer want to see have no way to get rid of it — their only recourse is to leave it in the list or toggle it done, which still clutters the view. Deletion is the most basic expected operation on a TODO list and its absence makes the feature feel incomplete. This change closes that gap by letting the user remove a task they no longer want.

## What changes

- Each task in the list shows a way to delete it (e.g. a "Delete" button or trash icon next to the row).
- Clicking delete removes the task from the visible list and from the underlying data store, permanently.
- A reload of the page no longer shows a deleted task.
- Deletion is not reversible — no undo in this change.

## Acceptance criteria

- [ ] Sending `DELETE /tasks/{id}` to the `api` with a valid id removes the task and returns `204 No Content`.
- [ ] `DELETE /tasks/{id}` against a non-existent id returns `404` and does not alter any other row.
- [ ] After a successful delete, `GET /tasks` no longer includes that task.
- [ ] On the web home page, each task row exposes a delete control.
- [ ] Clicking the delete control removes the row from the UI immediately and calls the API; after a browser reload the task is still absent.
- [ ] If the delete request fails, the row reappears in the list and an inline error is shown on that row.
- [ ] Empty-state copy reappears if the last remaining task is deleted.

## Out of scope

- Undo / "recently deleted" recovery.
- Bulk delete ("clear completed", "delete all").
- Confirmation dialog before deleting (MVP: click is immediate).
- Soft-delete or archival (rows are hard-deleted from SQLite).
- Per-user ownership or authorization on deletion.
