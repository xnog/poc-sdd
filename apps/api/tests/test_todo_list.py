"""Tests for the todo-list domain."""

from __future__ import annotations

import os
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    """Build a TestClient pointed at a fresh temp SQLite file."""
    db_path = tmp_path / "test.db"
    monkeypatch.setenv("POC_SDD_DB_PATH", str(db_path))

    # Import after env var is set so any module-level path capture is correct.
    from src.main import app

    with TestClient(app) as c:
        yield c


def test_create_task_happy_path(client: TestClient) -> None:
    response = client.post("/tasks", json={"title": "Buy milk"})
    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Buy milk"
    assert body["done"] is False
    assert isinstance(body["id"], int)
    assert isinstance(body["created_at"], str)
    assert len(body["created_at"]) > 0


def test_toggle_task_done_and_undone(client: TestClient) -> None:
    created = client.post("/tasks", json={"title": "Buy milk"}).json()
    task_id = created["id"]

    r = client.patch(f"/tasks/{task_id}", json={"done": True})
    assert r.status_code == 200
    assert r.json()["done"] is True

    r = client.patch(f"/tasks/{task_id}", json={"done": False})
    assert r.status_code == 200
    assert r.json()["done"] is False


def test_toggle_is_idempotent(client: TestClient) -> None:
    created = client.post("/tasks", json={"title": "x"}).json()
    task_id = created["id"]
    client.patch(f"/tasks/{task_id}", json={"done": True})
    r = client.patch(f"/tasks/{task_id}", json={"done": True})
    assert r.status_code == 200
    assert r.json()["done"] is True


def test_toggle_persists_in_list(client: TestClient) -> None:
    a = client.post("/tasks", json={"title": "a"}).json()
    b = client.post("/tasks", json={"title": "b"}).json()
    client.patch(f"/tasks/{a['id']}", json={"done": True})

    rows = client.get("/tasks").json()
    by_id = {r["id"]: r for r in rows}
    assert by_id[a["id"]]["done"] is True
    assert by_id[b["id"]]["done"] is False


def test_toggle_missing_task_returns_404(client: TestClient) -> None:
    r = client.patch("/tasks/999999", json={"done": True})
    assert r.status_code == 404


def test_toggle_invalid_body_returns_422(client: TestClient) -> None:
    created = client.post("/tasks", json={"title": "x"}).json()
    # FastAPI/Pydantic returns 422 for schema validation failures.
    r = client.patch(f"/tasks/{created['id']}", json={})
    assert r.status_code == 422
    r = client.patch(f"/tasks/{created['id']}", json={"done": ["not", "a", "bool"]})
    assert r.status_code == 422


def test_delete_task_happy_path(client: TestClient) -> None:
    created = client.post("/tasks", json={"title": "ephemeral"}).json()
    r = client.delete(f"/tasks/{created['id']}")
    assert r.status_code == 204
    assert r.content == b""
    assert client.get("/tasks").json() == []


def test_delete_missing_task_returns_404(client: TestClient) -> None:
    r = client.delete("/tasks/999999")
    assert r.status_code == 404


def test_delete_is_not_idempotent(client: TestClient) -> None:
    created = client.post("/tasks", json={"title": "x"}).json()
    first = client.delete(f"/tasks/{created['id']}")
    assert first.status_code == 204
    second = client.delete(f"/tasks/{created['id']}")
    assert second.status_code == 404


def test_delete_does_not_affect_other_tasks(client: TestClient) -> None:
    a = client.post("/tasks", json={"title": "a"}).json()
    b = client.post("/tasks", json={"title": "b"}).json()
    r = client.delete(f"/tasks/{a['id']}")
    assert r.status_code == 204
    rows = client.get("/tasks").json()
    assert [row["id"] for row in rows] == [b["id"]]


def test_create_task_trims_title(client: TestClient) -> None:
    response = client.post("/tasks", json={"title": "  hello  "})
    assert response.status_code == 201
    assert response.json()["title"] == "hello"


def test_create_task_rejects_empty_title(client: TestClient) -> None:
    response = client.post("/tasks", json={"title": ""})
    assert response.status_code == 400


def test_create_task_rejects_whitespace_title(client: TestClient) -> None:
    response = client.post("/tasks", json={"title": "   "})
    assert response.status_code == 400


def test_list_tasks_newest_first(client: TestClient) -> None:
    client.post("/tasks", json={"title": "first"})
    client.post("/tasks", json={"title": "second"})
    client.post("/tasks", json={"title": "third"})

    response = client.get("/tasks")
    assert response.status_code == 200
    titles = [t["title"] for t in response.json()]
    # Same-second inserts are disambiguated by id DESC.
    assert titles == ["third", "second", "first"]


def test_list_tasks_empty(client: TestClient) -> None:
    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == []


def test_persistence_across_connections(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Tasks written by one client must be visible after a fresh connection."""
    db_path = tmp_path / "persist.db"
    monkeypatch.setenv("POC_SDD_DB_PATH", str(db_path))

    from src.main import app

    with TestClient(app) as c1:
        r = c1.post("/tasks", json={"title": "persisted"})
        assert r.status_code == 201

    # New TestClient → new lifespan → new connection → still sees the row.
    with TestClient(app) as c2:
        rows = c2.get("/tasks").json()
        assert [row["title"] for row in rows] == ["persisted"]

    assert db_path.exists()
    # Avoid polluting other tests that might read this env var at import time.
    os.environ.pop("POC_SDD_DB_PATH", None)
