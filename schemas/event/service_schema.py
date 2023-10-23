from pydantic import BaseModel
from datetime import datetime


class Service(BaseModel):
    service_name: str
    service_date: str
    description: str
    service_type: str
    no_men: str
    no_women: str
    no_children: str
    no_visitors: str
    head_minister: str
    assistant_minister: str
    time_period: str


class ReadService(BaseModel):
    id: int
    service_name: str
    service_date: str
    description: str
    service_type: str
    no_men: str
    no_women: str
    no_children: str
    no_visitors: str
    head_minister: str
    assistant_minister: str
    time_period: str
    date_created: datetime = None
    congregation_id: int
    congregation_name: str

    class Config:
        orm_mode = True
