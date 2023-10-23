from pydantic import BaseModel
from typing import List
from mainApp.schemas.single import members_schema, elder_schema
from mainApp.schemas.group import district_schema, cottage_schema, ministry_schema
from mainApp.schemas.event import communion_service_schema, service_schema, baptism_schema, confirmation_schema
from datetime import datetime


class Congregation(BaseModel):
    congregation_name: str
    location: str
    date_setup: str
    congregation_head: str
    assistant_congregation_head: str


class AllCongregation(BaseModel):
    id: int
    congregation_name: str
    date_setup: str
    date_created: datetime = None
    admin_id: int
    admin_name: str
    congregation_head: str
    assistant_congregation_head: str
    location: str

    class Config:
        orm_mode = True


class CongregationMembers(BaseModel):
    members: List[members_schema.ReadMember] = []

    class Config:
        orm_mode = True


class CongregationElders(BaseModel):
    elders: List[elder_schema.ReadElder] = []

    class Config:
        orm_mode = True


class CongregationCottages(BaseModel):
    cottages: List[cottage_schema.ReadCottage] = []

    class Config:
        orm_mode = True


class CongregationDistricts(BaseModel):
    districts: List[district_schema.ReadDistrict] = []

    class Config:
        orm_mode = True


class CongregationService(BaseModel):
    service: List[service_schema.ReadService] = []

    class Config:
        orm_mode = True


class CongregationMinistries(BaseModel):
    ministries: List[ministry_schema.ReadMinistry] = []

    class Config:
        orm_mode = True


class CongregationCommunionServices(BaseModel):
    communion_services: List[communion_service_schema.ReadCommunionService] = []

    class Config:
        orm_mode = True


class CongregationBaptism(BaseModel):
    baptism: List[baptism_schema.ReadBaptism] = []

    class Config:
        orm_mode = True


class CongregationConfirmation(BaseModel):
    confirmation: List[confirmation_schema.ReadConfirmation] = []

    class Config:
        orm_mode = True
