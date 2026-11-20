from __future__ import annotations

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.main import app, notes, word_count

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_notes() -> None:
    """Reset the in-memory notes list before each test."""
    notes.clear()

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