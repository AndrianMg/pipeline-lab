from __future__ import annotations

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.main import app, notes, word_count
import app.main as main_module
from app.main import app, word_count
client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_state() -> None:
    """Reset the in-memory notes list and ID counter together before each test."""
    main_module.notes.clear()
    main_module.next_id = 1

def test_word_count_normal_input() -> None:
    assert word_count("hello fast api lab") == 4


def test_word_count_empty_string() -> None:
    assert word_count("") == 0


def test_word_count_extra_spaces() -> None:
    assert word_count("   hello    world  \n  again  ") == 3
    
def test_health_endpoint() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_get_notes_initially_empty() -> None:
    response = client.get("/notes")
    assert response.status_code == 200
    assert response.json() == []


def test_post_note_and_get_notes() -> None:
    create_response = client.post("/notes", json={"text": "  First note here  "})
    assert create_response.status_code == 201
    assert create_response.json() == {
        "id": 1,
        "text": "First note here",
        "words": 3,
    }

    list_response = client.get("/notes")
    assert list_response.status_code == 200
    assert list_response.json() == [
        {
            "id": 1,
            "text": "First note here",
            "words": 3,
        }
    ]


def test_post_empty_note_returns_422() -> None:
    response = client.post("/notes", json={"text": "   "})
    assert response.status_code == 422
    assert response.json() == {"detail": "Note text cannot be empty."}    
def test_delete_note_removes_it_from_notes() -> None:
    create_response = client.post("/notes", json={"text": "Temporary note"})
    assert create_response.status_code == 201
    created = create_response.json()
    delete_response = client.delete(f"/notes/{created['id']}")
    assert delete_response.status_code == 200
    assert delete_response.json() == created
    list_response = client.get("/notes")
    assert list_response.status_code == 200
    assert list_response.json() == []
def test_delete_missing_note_returns_404() -> None:
    response = client.delete("/notes/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Note not found"}
    
def test_ids_never_reuse_after_deleting_highest_id() -> None:
    first = client.post("/notes", json={"text": "First"}).json()
    second = client.post("/notes", json={"text": "Second"}).json()
    assert first["id"] == 1
    assert second["id"] == 2
    delete_response = client.delete(f"/notes/{second['id']}")
    assert delete_response.status_code == 200
    third_response = client.post("/notes", json={"text": "Third"})
    assert third_response.status_code == 201
    third = third_response.json()
    assert third["id"] == 3
    all_notes = client.get("/notes").json()
    ids = [note["id"] for note in all_notes]
    assert len(ids) == len(set(ids))
    assert ids == [1, 3]