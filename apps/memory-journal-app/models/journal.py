from pydantic import BaseModel
from typing import List
from datetime import datetime


class JournalEntry(BaseModel):
    id: str
    filename: str
    caption: str
    tags: List[str]
    mock_location: str
    timestamp: datetime


class JournalResponse(BaseModel):
    entries: List[JournalEntry]
    total: int


class JournalEntryCreate(BaseModel):
    filename: str
    caption: str
    tags: List[str]

