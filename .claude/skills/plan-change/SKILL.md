---
name: plan-change
description: Use when the user requests a new feature, behavior change, or any modification that affects the public contract of an app (API, UI, data, module signatures). Creates the change folder and updates the proposed state of living specs. Pauses for human approval before any code is written. Does NOT implement code. Use implement-change for that.
---

# plan-change

You are executing **Phase 1** of the SDD flow: **Planning**. Your output is a reviewable proposal, not code.

## Preconditions

- The user described a change they want.
- You have read `CLAUDE.md` and understand invariants I1–I5.

## Hard rules for this skill

- **You do not write code** in `apps/`. Not a single line. If you are tempted, stop.
- You do not `git commit`, `git push`, or open PRs. You edit files; the user (or CI) handles VCS.
- At the end, you **pause and request human approval**. You do not invoke `implement-change` yourself.

---

## Steps

### Step 1 — Clarify scope

Before creating any file, decide:

- **Slug**: short kebab-case description of the change. Example: `allow-delete-todo`, `add-rate-limiting`.
- **Date**: today's date in `YYYY-MM-DD` format.
- **Scope**: list of affected apps (from `apps/*`). Can be one or many.
- **Domains touched**: for each affected app, which domain folder under `specs/specs/<app>/` is affected. If the domain is new, you will create it.

If any of these is ambiguous, **ask the user one focused question** before proceeding. Do not guess scope silently.

### Step 2 — Create the change folder

Path: `specs/changes/<YYYY-MM-DD>-<slug>/`

Create three files by copying and filling the templates:

**`proposal.md`** — copy from `specs/_templates/change/proposal.md`. Fill in:
- Frontmatter: `title`, `scope` (array of apps), `status: proposed`
- **Motivation**: why this change exists. What problem, whose problem.
- **What changes**: high-level bullet list of user-visible changes.
- **Acceptance criteria**: concrete, testable statements.
- **Out of scope**: things intentionally NOT included.

Language: product-oriented. A non-engineer reviewer should understand this file.

**`design.md`** — copy from `specs/_templates/change/design.md`. Fill in:
- Technical approach per affected app (endpoints, schema changes, UI components, etc.)
- Key technical decisions with one-line rationale (trade-offs, alternatives considered)
- Data/schema changes, migrations if any
- Anything a technical reviewer needs to approve the approach

Language: technical.

**`tasks.md`** — copy from `specs/_templates/change/tasks.md`. Fill in:
- Ordered, verifiable `[ ]` items grouped by area (API, Web, Specs, Tests, etc.)
- Each task should be small enough that marking `[x]` is unambiguous
- Include tasks for updating living specs and tests, not only code

### Step 3 — Update living specs with the PROPOSED state

For each affected `<app>/<domain>`:

- If `specs/specs/<app>/<domain>/spec.md` **exists**: edit it to reflect the state **after** this change. You are writing what the system **will do**, not what it does today.
- If it **does not exist**: create it by copying `specs/_templates/spec.md` and filling in the domain's behavior.

This is the most important step. The living spec is the contract under review. The reviewer approves by reading the diff on this file.

### Step 4 — Update `project.md` only if global

Update `specs/project.md` only if the change introduces:
- A new app
- A new framework/library that becomes core
- A new architectural pattern or convention applied project-wide
- A new piece of domain vocabulary that will be reused across features

Otherwise, do not touch `project.md`.

### Step 5 — Stop and request approval

Do not proceed. Output a concise summary to the user:

```
Planning complete for <YYYY-MM-DD-slug>. Files created/edited:
  - specs/changes/<YYYY-MM-DD-slug>/proposal.md
  - specs/changes/<YYYY-MM-DD-slug>/design.md
  - specs/changes/<YYYY-MM-DD-slug>/tasks.md
  - specs/specs/<app>/<domain>/spec.md  (created|edited)
  [- specs/project.md  (edited, reason: ...)]

Please review the proposal and the living spec diff.
Reply "approved" to proceed with implementation, or request changes.
```

**Do not invoke implement-change.** The user decides when to advance.

---

## Anti-patterns (forbidden)

- Writing any code in `apps/` during this phase.
- Skipping the living spec update ("I'll do it during implementation").
- Filling `proposal.md` or `design.md` with vague placeholders.
- Creating the change folder and immediately proceeding to implementation without explicit approval.
- Editing a previous, merged change (`specs/changes/<past>/*`). Immutable.

---

## Edge cases

- **Trivial change** (see `CLAUDE.md` §7): if the request is genuinely trivial (typo, lint, rename), tell the user "this looks trivial, skipping the SDD flow. Confirm?" and only proceed if they agree.
- **Unclear scope**: ask one question. Don't fabricate scope.
- **Multi-app change**: one change folder, multiple living specs. Tasks in `tasks.md` should clearly indicate which app each task belongs to.
- **Domain reorganization** (splitting/renaming a domain): treat as a normal change, but be explicit in `design.md` about how existing specs are migrated.
