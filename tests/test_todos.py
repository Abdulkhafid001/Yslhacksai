"""End-to-end tests for the to-do list API."""

import os
import tempfile

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete

os.environ["DATABASE_URL"] = f"sqlite:///{tempfile.mktemp(suffix='.db')}"

from app.database import SessionLocal  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Todo  # noqa: E402


@pytest.fixture()
def client():
    with TestClient(app) as test_client:
        with SessionLocal() as db:
            db.execute(delete(Todo))
            db.commit()
        yield test_client


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_todo(client):
    response = client.post(
        "/todos",
        json={"title": "Buy groceries", "description": "Milk and eggs"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["title"] == "Buy groceries"
    assert data["description"] == "Milk and eggs"
    assert data["completed"] is False


def test_list_todos_empty(client):
    response = client.get("/todos")
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0


def test_get_todo(client):
    todo_id = client.post("/todos", json={"title": "Test task"}).json()["id"]
    response = client.get(f"/todos/{todo_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Test task"


def test_get_todo_not_found(client):
    assert client.get("/todos/999").status_code == 404


def test_update_todo_put(client):
    todo_id = client.post("/todos", json={"title": "Old"}).json()["id"]
    response = client.put(
        f"/todos/{todo_id}",
        json={"title": "New", "description": "Updated", "completed": True},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New"
    assert data["completed"] is True


def test_patch_todo_toggle_complete(client):
    todo_id = client.post("/todos", json={"title": "Task"}).json()["id"]
    response = client.patch(f"/todos/{todo_id}", json={"completed": True})
    assert response.status_code == 200
    assert response.json()["completed"] is True


def test_filter_completed(client):
    client.post("/todos", json={"title": "Done", "completed": True})
    client.post("/todos", json={"title": "Not done"})
    done = client.get("/todos", params={"completed": True}).json()
    pending = client.get("/todos", params={"completed": False}).json()
    assert done["total"] == 1
    assert done["items"][0]["title"] == "Done"
    assert pending["total"] == 1
    assert pending["items"][0]["title"] == "Not done"


def test_delete_todo(client):
    todo_id = client.post("/todos", json={"title": "Delete me"}).json()["id"]
    assert client.delete(f"/todos/{todo_id}").status_code == 204
    assert client.get(f"/todos/{todo_id}").status_code == 404


def test_delete_todo_not_found(client):
    assert client.delete("/todos/999").status_code == 404


def test_validation_empty_title(client):
    response = client.post("/todos", json={"title": ""})
    assert response.status_code == 422
