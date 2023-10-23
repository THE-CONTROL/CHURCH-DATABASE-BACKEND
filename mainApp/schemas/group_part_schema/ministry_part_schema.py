from pydantic import BaseModel
from datetime import datetime
from typing import Any


class MinistryMembers(BaseModel):
    participant_name: str
    date_joined: str
    ministry: Any


class UpdateMinistryMembers(BaseModel):
    participant_name: str
    date_joined: str


class ReadMinistryMembers(BaseModel):
    id: int
    participant_name: str
    date_joined: str
    date_created: datetime = None
    ministry_id: int
    ministry_name: str

    class Config:
        orm_mode = True
