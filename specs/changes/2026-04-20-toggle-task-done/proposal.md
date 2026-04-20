---
title: Toggle task done/undone
scope: [api, web]
status: proposed
---

# Toggle task done/undone

## Motivation

Today a task, once created, exists forever as a plain line in the list. Users have no way to record that they actually finished it, which defeats the basic purpose of a TODO list: separating what's pending from what's done. We want the simplest possible completion model — a checkbox per item, fully reversible — so the list starts reflecting real progress instead of being an append-only log.

Completed tasks stay visible (crossed out) rather than disappearing, so users can glance at what they've accomplished without losing context.

## What changes

- Each task in the list has a checkbox next to it.
- Clicking an unchecked checkbox marks the task as done; clicking a checked one marks it undone.
- Done tasks render with their title visually struck-through but remain in the same list, in the same position.
- The done/undone state persists in the database: reloading the page shows each task in the state it was last left in.

## Acceptance criteria

- [ ] A fresh task is created as **not done** (checkbox unchecked, title not struck-through).
- [ ] Clicking the checkbox of a not-done task marks it done: checkbox becomes checked and title is struck-through, without reloading the page.
- [ ] Clicking the checkbox of a done task marks it undone: checkbox becomes unchecked and strike-through is removed.
- [ ] After reloading the browser, every task appears in the last state it was toggled to.
- [ ] Done tasks are not removed from the list and do not change position relative to other tasks.
- [ ] The list order remains newest-first, regardless of done/undone state.
- [ ] Hitting the toggle endpoint for a non-existent task id returns a 404.

## Out of scope

- Filtering or hiding done tasks.
- Bulk actions ("mark all done", "clear completed").
- Editing or deleting tasks.
- Tracking *when* a task was completed (no `completed_at` timestamp).
- Per-user ownership / authentication.
- Optimistic UI rollback on failure beyond reverting the checkbox.
