---
app: <app>
domain: <domain>
status: living
---

# <Domain Name>

One-paragraph description of what this domain is and what problem it solves **in this app**. Written in the present tense — this doc describes how the system works **today**, not what it used to do or what it will do.

---

## User Behavior

What the end-user (or API client, for `api`) can do in this domain. Write this in terms of capabilities and expected outcomes.

Examples:
- Users can create a task with a title.
- Users can mark a task as done; done tasks remain visible until deleted.

---

## Interface

### Endpoints (for `api`)

| Method | Path | Purpose | Success | Errors |
|---|---|---|---|---|
| GET | `/path` | ... | 200 with body | 404 if ... |
| POST | `/path` | ... | 201 with body | 400 if ... |

Request/response shapes as JSON examples:

```json
// POST /path request
{ "field": "value" }
```

```json
// 201 response
{ "id": "...", "field": "value" }
```

### UI (for `web`)

Describe the screens, components, and interactions that implement this domain. Use user-visible language.

- **Screen**: `/route` — lists X, allows Y
- **Component**: `<ComponentName>` — behavior, states

---

## Data

Schema and persistence rules for this domain.

```sql
CREATE TABLE ...
```

- Invariants: what must always be true about this data
- Lifecycle: how records are created, updated, deleted

---

## Rules / Invariants

Business rules, not implementation details.

- Rule 1
- Rule 2

---

## Out of scope

Things this domain explicitly does **not** do, to make boundaries clear.

- Not handled here: ...
