from pydantic import BaseModel
from typing import List
from mainApp.schemas.single import members_schema, elder_schema
from mainApp.schemas.group import cottage_schema
from datetime import datetime


class District(BaseModel):
    district_name: str
    coverage_area: str
    date_setup: str
    district_head: str
    assistant_district_head: str


class ReadDistrict(BaseModel):
    id: int
    district_name: str
    coverage_area: str
    date_setup: str
    date_created: datetime = None
    congregation_id: str
    district_head: str
    assistant_district_head: str
    congregation_name: str

    class Config:
        orm_mode = True


class DistrictMembers(BaseModel):
    members: List[members_schema.ReadMember] = []

    class Config:
        orm_mode = True


class DistrictElders(BaseModel):
    elders: List[elder_schema.ReadElder] = []

    class Config:
        orm_mode = True


class DistrictCottages(BaseModel):
    cottages: List[cottage_schema.ReadCottage] = []

    class Config:
        orm_mode = True
