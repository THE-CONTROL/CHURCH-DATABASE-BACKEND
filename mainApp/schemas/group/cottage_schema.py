from pydantic import BaseModel
from typing import List, Any
from mainApp.schemas.single import members_schema, elder_schema
from datetime import datetime


class Cottage(BaseModel):
    cottage_name: str
    cottage_address: str
    date_setup: str
    district: Any
    cottage_head: str
    assistant_cottage_head: str


class UpdateCottage(BaseModel):
    cottage_name: str
    cottage_address: str
    date_setup: str
    cottage_head: str
    assistant_cottage_head: str


class ReadCottage(BaseModel):
    id: int
    cottage_name: str
    cottage_address: str
    date_setup: str
    date_created: datetime = None
    cottage_head: str
    assistant_cottage_head: str
    congregation_id: int
    district_id: int
    district_name: str
    congregation_name: str

    class Config:
        orm_mode = True


class CottageMembers(BaseModel):
    members: List[members_schema.ReadMember] = []

    class Config:
        orm_mode = True


class CottageElders(BaseModel):
    elders: List[elder_schema.ReadElder] = []

    class Config:
        orm_mode = True
