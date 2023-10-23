from pydantic import BaseModel
from datetime import datetime
from typing import List
from mainApp.schemas.group import congregation_schema


class Admin(BaseModel):
    id: int
    admin_name: str
    email: str
    role: str
    password: str
    logged_in: bool
    date_created: datetime = None

    class Config:
        orm_mode = True


class LoginAdmin(BaseModel):
    admin_name: str
    password: str


class RegisterAdmin(BaseModel):
    admin_name: str
    role: str
    password: str
    confirm_password: str
    email: str


class UpdateAdmin(BaseModel):
    admin_name: str
    role: str
    email: str


class AdminCongregation(BaseModel):
    congregation: List[congregation_schema.AllCongregation] = []

    class Config:
        orm_mode = True


class ForgotPassword(BaseModel):
    email: str


class Reset(BaseModel):
    code: str
    password: str
    confirm_password: str
