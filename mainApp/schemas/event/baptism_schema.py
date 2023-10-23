from pydantic import BaseModel
from typing import List
from mainApp.schemas.group_part_schema.baptism_part_schema import ReadBaptismParticipant
from datetime import datetime


class Baptism(BaseModel):
    baptism_name: str
    minister: str
    baptism_date: str


class ReadBaptism(BaseModel):
    id: int
    baptism_name: str
    minister: str
    baptism_date: str
    congregation_id: int
    date_created: datetime = None
    congregation_name: str

    class Config:
        orm_mode = True


class ReadBaptismPart(BaseModel):
    baptism_participants: List[ReadBaptismParticipant] = []

    class Config:
        orm_mode = True
