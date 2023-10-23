from pydantic import BaseModel
from datetime import datetime
from typing import Any


class ConfirmationParticipant(BaseModel):
    participant_name: str
    confirmation: Any


class UpdateConfirmationParticipant(BaseModel):
    participant_name: str


class ReadConfirmationParticipant(BaseModel):
    id: int
    participant_name: str
    date_created: datetime = None
    confirmation_id: int
    confirmation_name = str

    class Config:
        orm_mode = True
