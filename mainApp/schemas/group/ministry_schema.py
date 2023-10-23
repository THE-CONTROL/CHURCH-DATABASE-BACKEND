from pydantic import BaseModel
from typing import List, Any
from mainApp.schemas.group_part_schema.ministry_part_schema import ReadMinistryMembers
from datetime import datetime


class Ministry(BaseModel):
    ministry_name: str
    ministry_head: str
    assistant_ministry_head: str
    date_setup: str


class ReadMinistry(BaseModel):
    id: int
    ministry_name: str
    ministry_head: str
    assistant_ministry_head: str
    date_setup: str
    date_created:  datetime = None
    congregation_id: int
    congregation_name: str

    class Config:
        orm_mode = True


class MinistryMembers(BaseModel):
    members: List[ReadMinistryMembers] = []

    class Config:
        orm_mode = True
