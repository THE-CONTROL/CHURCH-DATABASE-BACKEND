from pydantic import BaseModel
from typing import List, Any
from mainApp.schemas.group_part_schema.communion_part_schema import ReadCommunionServiceParticipant
from datetime import datetime


class CommunionService(BaseModel):
    service_name: str
    service_date: str
    service_head_count: str


class ReadCommunionService(BaseModel):
    id: int
    service_name: str
    service_date: str
    service_head_count: str
    date_created: datetime = None
    congregation_id: int
    congregation_name: str

    class Config:
        orm_mode = True


class ReadCommunionServicePart(BaseModel):
    participants: List[ReadCommunionServiceParticipant] = []

    class Config:
        orm_mode = True




class ReadCommunionService(CommunionService):
    id: int
    participants: List[ReadCommunionServiceParticipant] = []
    date_created: datetime = None
    congregation_id: int

    class Config:
        orm_mode = True


