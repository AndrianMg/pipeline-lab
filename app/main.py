from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Pipeline Lab Notes API")



notes: list[dict[str, int | str]] = [] #List to store notes

class NoteCreate(BaseModel):
    text : str 

class Note(BaseModel):
    id : int
    text : str
    words : int
        
def word_count(text: str) -> int: 
    """Return the number of whitespace-separated words in text."""
    return len(text.split())
@app.get("/health")
def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/notes", response_model=list[Note])
def list_notes() -> list[dict[str, int | str]]:
    """Return all notes stored in memory."""
    return notes


@app.post("/notes", response_model=Note, status_code=201)
def create_note(payload: NoteCreate) -> dict[str, int | str]:
    """Create and store a new note in memory."""
    cleaned = payload.text.strip()
    if not cleaned:
        raise HTTPException(status_code=422, detail="Note text cannot be empty.")

    note: dict[str, int | str] = {
        "id": len(notes) + 1,
        "text": cleaned,
        "words": word_count(cleaned),
    }
    notes.append(note)
    return note