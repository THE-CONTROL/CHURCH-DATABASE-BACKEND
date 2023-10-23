from pydantic import BaseModel
from datetime import datetime
from typing import Any


class Elder(BaseModel):
    elder_name: str
    sex: str
    marital_status: str
    date_joined: str
    elder_type: str
    elder_post: str
    telephone: str
    district: Any
    cottage: Any


class UpdateElder(BaseModel):
    elder_name: str
    sex: str
    marital_status: str
    date_joined: str
    elder_type: str
    elder_post: str
    telephone: str


class ReadElder(BaseModel):
    id: int
    elder_name: str
    sex: str
    marital_status: str
    date_joined: str
    elder_type: str
    elder_post: str
    telephone: str
    date_created: datetime = None
    district_id: int
    cottage_id: int
    congregation_id: int
    district_name: str
    cottage_name: str
    congregation_name: str

    class Config:
        orm_mode = True
