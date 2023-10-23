from pydantic import BaseModel
from typing import List, Any
from mainApp.schemas.group_part_schema.confirmation_part_schema import ReadConfirmationParticipant
from datetime import datetime


class Confirmation(BaseModel):
    confirmation_name: str
    minister: str
    confirmation_date: str
    congregation: Any


class ReadConfirmation(BaseModel):
    id: int
    confirmation_name: str
    minister: str
    confirmation_date: str
    date_created: datetime = None
    congregation_id: int
    congregation_name: str

    class Config:
        orm_mode = True


class ReadConfirmationPart(BaseModel):
    confirmation_participants: List[ReadConfirmationParticipant] = []

    class Config:
        orm_mode = True
