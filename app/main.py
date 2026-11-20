from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Pipeline Lab Notes API")



notes: list[dict[str, int | str]] = [] #List to store notes
next_id: int = 1 # Variable to keep track of the next note ID
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
    global next_id
    cleaned = payload.text.strip()
    if not cleaned:
        raise HTTPException(status_code=422, detail="Note text cannot be empty.")
    
    note: dict[str, int | str] = {
        "id": next_id,
        "text": cleaned,
        "words": word_count(cleaned),
    }
    next_id += 1
    notes.append(note)
    return note
@app.delete("/notes/{note_id}", response_model=Note)
def delete_note(note_id: int) -> dict[str, int | str]:
    """Delete a note by ID and return it."""
    for index, note in enumerate(notes):
        if note["id"] == note_id:
            return notes.pop(index)
    raise HTTPException(status_code=404, detail="Note not found")