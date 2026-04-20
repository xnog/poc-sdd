---
name: implement-change
description: Use after the user has approved a change (plan-change output). Implements the code in apps/ to satisfy the already-agreed living spec, marks tasks.md items as completed, and adjusts the living spec only if implementation reveals a gap. Do NOT use this skill before a change has been planned and approved.
---

# implement-change

You are executing **Phase 2** of the SDD flow: **Implementation**. The spec and design were already agreed in Phase 1. Your job is to make the code match the already-approved contract.

## Preconditions

- A change folder exists at `specs/changes/<YYYY-MM-DD-slug>/` with `proposal.md`, `design.md`, and `tasks.md`.
- The user has **explicitly approved** the proposal. Look for clear approval language (e.g., "approved", "go ahead", "proceed"). If unclear, ask — do not assume.
- The affected living specs already reflect the proposed post-change state.

If any precondition fails, stop and redirect to `plan-change`.

## Hard rules for this skill

- You do not re-open or renegotiate `proposal.md` or `design.md`. They are frozen after approval.
- You do not `git commit` or `git push`. The user (or CI) handles VCS.
- If reality contradicts the approved plan, **pause and escalate to the user** — do not silently rewrite the plan.

---

## Steps

### Step 1 — Load context

Read, in order:
1. `CLAUDE.md` (invariants)
2. `specs/project.md` (worldview)
3. `specs/changes/<current>/proposal.md`, `design.md`, `tasks.md`
4. All affected `specs/specs/<app>/<domain>/spec.md` files (the contract)

### Step 2 — Work through `tasks.md`

For each `[ ]` item in order:

1. Do the work (write/edit code in `apps/`, add tests, etc.)
2. Verify it locally when possible (run the test, hit the endpoint, load the page)
3. Mark the item `[x]` in `tasks.md` **after** it's done — not before
4. Move on

Don't batch checkmarks. One task at a time.

### Step 3 — Handle divergence (if it happens)

If during implementation you discover that the living spec is **wrong or incomplete** (edge case missed, contract can't be satisfied as written):

1. **Stop**. Do not silently patch the spec or the code to hide the gap.
2. Describe the divergence to the user: what the spec says, what reality requires, the options.
3. Wait for the user's decision.
4. If they say "update the spec and continue": edit `specs/specs/<app>/<domain>/spec.md` in this same PR to reflect the corrected contract, then resume.
5. Add a note in `design.md` under a `## Divergences` section (append-only within the current change, which is still unmerged) documenting the deviation and rationale.

### Step 4 — Verify completeness

Before reporting done, verify:

- [ ] All items in `tasks.md` are `[x]`
- [ ] Affected living specs match what was actually built
- [ ] Code compiles / tests pass (where applicable)
- [ ] No code was written outside the scope of the change

### Step 5 — Report

Output a concise summary:

```
Implementation complete for <YYYY-MM-DD-slug>.

Files changed:
  - apps/<app>/...           (new|modified)
  - specs/specs/<app>/<domain>/spec.md  (adjusted|unchanged since plan)
  [- specs/changes/<current>/design.md  (Divergences section appended)]

All tasks marked [x]. Ready for review.
```

Do not commit or push. The user decides next steps.

---

## Anti-patterns (forbidden)

- Starting without explicit user approval of the plan.
- Editing `proposal.md` or `design.md` to retroactively match what you built (that's revisionism — use the `Divergences` section instead).
- Silently updating the living spec to match broken code (spec drives code, not the reverse).
- Marking tasks `[x]` before the work is actually verified.
- Rewriting scope mid-implementation. If scope needs to grow, stop and escalate.
- Modifying any past, merged change in `specs/changes/<past>/*`.

---

## Edge cases

- **Task order dependencies**: if task B depends on task A, do them in order even if `tasks.md` lists them differently — but if `tasks.md` is badly ordered, fix the ordering (you may edit `tasks.md` freely during implementation).
- **New task discovered**: add it to `tasks.md` with `[ ]`, then execute it. Do not silently do unlisted work.
- **Can't implement a task**: stop, describe the blocker, ask the user. Do not skip or fake-complete.
- **Tests failing**: implementation is not complete. Do not report done with failing tests.
