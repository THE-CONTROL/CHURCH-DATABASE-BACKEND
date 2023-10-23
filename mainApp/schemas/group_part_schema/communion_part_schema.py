from pydantic import BaseModel
from datetime import datetime
from typing import Any


class CommunionServiceParticipant(BaseModel):
    participant_name: str
    participant_type: str
    communion_service: Any


class UpdateCommunionServiceParticipant(BaseModel):
    participant_name: str
    participant_type: str


class ReadCommunionServiceParticipant(BaseModel):
    id: int
    participant_name: str
    participant_type: str
    date_created: datetime = None
    communion_service_id: int
    service_name: str

    class Config:
        orm_mode = True
