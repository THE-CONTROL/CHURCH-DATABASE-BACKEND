from pydantic import BaseModel
from datetime import datetime
from typing import Any


class Member(BaseModel):
    member_name: str
    sex: str
    marital_status: str
    date_joined: str
    telephone: str
    baptised: str
    district: Any
    cottage: Any
    discipline: str


class UpdateMember(BaseModel):
    member_name: str
    sex: str
    marital_status: str
    date_joined: str
    telephone: str
    baptised: str
    discipline: str


class ReadMember(BaseModel):
    id: int
    member_name: str
    sex: str
    marital_status: str
    date_joined: str
    telephone: str
    baptised: str
    discipline: str
    date_created: datetime = None
    district_name: str
    cottage_name: str

    class Config:
        orm_mode = True
