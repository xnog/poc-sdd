---
title: Initial TODO list — create and list tasks
scope: [api, web]
status: proposed
---

# Initial TODO list — create and list tasks

## Motivation

The POC needs a first real, end-to-end behavior to exercise the SDD flow and the monorepo wiring (web ↔ api ↔ SQLite). A minimal TODO list is the canonical example: small surface, persistent data, one UI screen, two endpoints. It gives us something a human can click through and something CI can deploy.

This change delivers only the creation and listing flow. Completion, deletion, editing, and authentication are out of scope and will come as follow-up changes, each through its own spec.

## What changes

- User can type a title in a single input on the home page and create a task.
- User sees the list of existing tasks below the input, with the most recent at the top.
- Tasks persist across browser reloads and across API server restarts (SQLite file on disk).
- A new backend domain `todo-list` exposes `POST /tasks` and `GET /tasks`.
- A new frontend domain `todo-list` renders the home page with the input and the list.

## Acceptance criteria

- [ ] `POST /tasks` with `{ "title": "Buy milk" }` returns `201` with `{ id, title, created_at }`.
- [ ] `POST /tasks` with empty or whitespace-only title returns `400`.
- [ ] `GET /tasks` returns `200` with an array ordered by `created_at` descending (newest first).
- [ ] Tasks survive an API process restart (stored in SQLite file, not in memory).
- [ ] Home page `/` on `web` shows an input + submit; submitting creates a task and it appears at the top of the list without a full page reload.
- [ ] After a browser reload, previously created tasks are still listed.
- [ ] The UI shows a clear empty state when there are no tasks.

## Out of scope

- Marking tasks as done.
- Editing task titles.
- Deleting tasks.
- Authentication, user accounts, per-user lists.
- Pagination, search, filtering.
- Optimistic UI, offline support.
- Real deploy (deploy scripts remain fake in this POC).
