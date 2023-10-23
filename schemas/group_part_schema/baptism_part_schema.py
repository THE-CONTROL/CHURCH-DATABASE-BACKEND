from pydantic import BaseModel
from datetime import datetime
from typing import Any


class BaptismParticipant(BaseModel):
    participant_name: str
    baptism: Any


class UpdateBaptismParticipant(BaseModel):
    participant_name: str


class ReadBaptismParticipant(BaseModel):
    id: int
    participant_name: str
    date_created: datetime = None
    baptism_id: int
    baptism_name: str

    class Config:
        orm_mode = True
