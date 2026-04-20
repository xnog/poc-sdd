# Project Rules — Spec-Driven Development (SDD)

This repository follows **Spec-Driven Development**. Specs are the source of truth; code is an artifact that fulfills the spec.

These rules are **universal** — they apply to every environment (local Claude Code, GitHub Actions, any other tool). Rules about git, branches, and pull requests live in `.github/workflows/claude.yml`, not here.

---

## 1. Invariants (non-negotiable)

**I1.** Every change in system behavior begins with a folder `specs/changes/YYYY-MM-DD-slug/`. No change → no code.

**I2.** The living spec (`specs/specs/<app>/<domain>/spec.md`) is updated **during the planning phase**, reflecting the **proposed** state. Create the file if the domain is new; edit it if it exists.

**I3.** `specs/project.md` is updated **only** when the change affects something global (stack, architecture, convention, or a new app appears).

**I4.** Between planning and implementation there is an **explicit human gate**. Without approval, no code is written.

**I5.** Merged changes are **immutable**. To correct a past change, create a new change that supersedes it.

---

## 2. Two phases, two skills

Every feature/behavior change goes through two phases, each backed by a skill:

1. **Planning** → use the skill [`plan-change`](.claude/skills/plan-change/SKILL.md)
   - Creates the change folder (`proposal.md`, `design.md`, `tasks.md`)
   - Creates or edits the affected living specs with the proposed state
   - Updates `project.md` if the change is global
   - **Pauses and asks for human approval**

2. **Implementation** → use the skill [`implement-change`](.claude/skills/implement-change/SKILL.md)
   - Runs only after planning was approved
   - Writes code in `apps/` to satisfy the already-agreed spec
   - Marks `tasks.md` items `[x]` as they're completed
   - Re-adjusts living spec only if implementation reveals a gap

Do not invent intermediate phases. Do not skip either phase for behavior changes.

---

## 3. Folder structure

```
specs/
  project.md                              # global worldview (stack, arch, domain)
  _templates/                             # templates to copy from
    spec.md
    change/{proposal,design,tasks}.md
  specs/                                  # CURRENT state, per app
    <app>/<domain>/spec.md
  changes/                                # HISTORY, append-only
    YYYY-MM-DD-slug/
      proposal.md                         # what + why (product language)
      design.md                           # how (technical decisions)
      tasks.md                            # checklist (mark [x] during impl)

apps/
  <app>/                                  # each app is an autonomous product
    moon.yml
    deploy.sh

.claude/skills/                           # SDD procedures (loaded on demand)
  plan-change/SKILL.md
  implement-change/SKILL.md
```

---

## 4. File permissions matrix

| File | Editable? | Phase | When |
|---|---|---|---|
| `specs/changes/<current>/proposal.md` | ✅ | plan | Before approval. Frozen after. |
| `specs/changes/<current>/design.md` | ✅ | plan | Before approval. Frozen after. |
| `specs/changes/<current>/tasks.md` | ✅ | plan + impl | Created during plan; `[x]` marked during impl. |
| `specs/specs/<app>/<domain>/spec.md` | ✅ create or edit | plan (main) / impl (adjust) | Always if change alters behavior. |
| `specs/project.md` | ✅ | plan | Only when change is global. |
| Code in `apps/*` | ✅ | impl | Only after human approval. |
| `specs/changes/<past>/*` | ❌ **never** | — | Immutable. Fix via a new change. |

---

## 5. Naming

- **Change folder**: `YYYY-MM-DD-short-kebab-slug/`
  - Example: `2026-04-20-allow-delete-todo/`
  - Date = date the change was **started**
  - Slug = short, descriptive, lowercase, kebab-case
- **Domain folder** inside `specs/specs/<app>/`: short noun, kebab-case
  - Examples: `todo-list/`, `auth/`, `rate-limiting/`

---

## 6. Cross-app changes

A single change can affect multiple apps. It generates **one** folder in `specs/changes/`, but edits/creates **multiple** living specs:

```
specs/changes/YYYY-MM-DD-slug/
  proposal.md        # scope: [app-a, app-b]
  design.md
  tasks.md

specs/specs/app-a/<domain>/spec.md    # created or edited
specs/specs/app-b/<domain>/spec.md    # created or edited
```

Everything in the same PR. The `scope` field in the `proposal.md` frontmatter lists affected apps explicitly.

---

## 7. Trivial changes (exception)

These do **not** require the full flow:

- Typos in comments or docs
- Local variable renames
- Formatting / lint fixes
- One-line bugfixes with **no change in observable behavior**

**Any change to external behavior** (API contract, UI flow, persisted data, public module signatures) always goes through the full two-phase flow.

---

## 8. When in doubt

- "Is this a behavior change?" → yes → create a change
- "Does this affect the public contract of an app?" → yes → update the living spec
- "Does this change something that applies project-wide?" → yes → update `project.md`
- "Can I skip the approval gate?" → no

If you're unsure whether a request is trivial or warrants a change, **create the change**. Over-documenting is cheap; under-documenting erodes the process.
