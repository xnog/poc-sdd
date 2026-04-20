"""Todo list HTTP endpoints.

Exposes ``POST /tasks``, ``GET /tasks``, ``PATCH /tasks/{id}``, and
``DELETE /tasks/{id}`` backed by a single SQLite table. Titles are trimmed;
empty-after-trim requests are rejected with ``400``. Listing is ordered
newest-first by ``created_at DESC, id DESC``. The ``done`` column is stored as
``0``/``1`` in SQLite and serialized as a JSON boolean at the HTTP boundary.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Response, status
from pydantic import BaseModel, Field

from .db import get_connection

router = APIRouter(tags=["tasks"])


class TaskCreate(BaseModel):
    title: str = Field(..., description="Raw user-supplied title; trimmed server-side.")


class TaskPatch(BaseModel):
    done: bool


class TaskOut(BaseModel):
    id: int
    title: str
    done: bool
    created_at: str


def _row_to_task(row: object) -> TaskOut:
    return TaskOut(
        id=row["id"],  # type: ignore[index]
        title=row["title"],  # type: ignore[index]
        done=bool(row["done"]),  # type: ignore[index]
        created_at=row["created_at"],  # type: ignore[index]
    )


@router.post("/tasks", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate) -> TaskOut:
    title = payload.title.strip()
    if not title:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="title must be a non-empty string",
        )

    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO tasks (title) VALUES (?)",
            (title,),
        )
        task_id = cursor.lastrowid
        row = conn.execute(
            "SELECT id, title, done, created_at FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()

    assert row is not None  # just inserted
    return _row_to_task(row)


@router.get("/tasks", response_model=list[TaskOut])
def list_tasks() -> list[TaskOut]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, title, done, created_at FROM tasks "
            "ORDER BY created_at DESC, id DESC"
        ).fetchall()

    return [_row_to_task(row) for row in rows]


@router.patch("/tasks/{task_id}", response_model=TaskOut)
def set_task_done(task_id: int, payload: TaskPatch) -> TaskOut:
    with get_connection() as conn:
        cursor = conn.execute(
            "UPDATE tasks SET done = ? WHERE id = ?",
            (1 if payload.done else 0, task_id),
        )
        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"task {task_id} not found",
            )
        row = conn.execute(
            "SELECT id, title, done, created_at FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()

    assert row is not None
    return _row_to_task(row)


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int) -> Response:
    with get_connection() as conn:
        cursor = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"task {task_id} not found",
            )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
