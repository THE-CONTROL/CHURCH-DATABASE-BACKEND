from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from mainApp.data.database import Base
from datetime import datetime, timedelta
from sqlalchemy.orm import relationship


class Admin(Base):
    __tablename__ = "admin"

    id = Column(Integer, primary_key=True, index=True)
    admin_name = Column(String)
    email = Column(String)
    role = Column(String, default="System Administrator")
    password = Column(String)
    logged_in = Column(Boolean, default=False)
    congregation = relationship("Congregation", back_populates="admin", cascade="all, delete-orphan")
    date_created = Column(DateTime, default=datetime.today())


class Member(Base):
    __tablename__ = "member"

    id = Column(Integer, primary_key=True, index=True)
    member_name = Column(String)
    sex = Column(String)
    marital_status = Column(String)
    date_joined = Column(String)
    baptised = Column(String)
    telephone = Column(String, nullable=True, unique=True)
    district_name = Column(String)
    cottage_name = Column(String)
    congregation_name = Column(String)
    district = relationship("District", back_populates="members")
    district_id = Column(Integer, ForeignKey("district.id"))
    cottage = relationship("Cottage", back_populates="members")
    cottage_id = Column(Integer, ForeignKey("cottage.id"))
    congregation = relationship("Congregation", back_populates="members")
    congregation_id = Column(Integer, ForeignKey("congregation.id"))
    discipline = Column(String)
    date_created = Column(DateTime, default=datetime.today())


class Elder(Base):
    __tablename__ = "elder"

    id = Column(Integer, primary_key=True, index=True)
    elder_name = Column(String)
    sex = Column(String)
    marital_status = Column(String)
    date_joined = Column(String)
    telephone = Column(String, nullable=True, unique=True)
    elder_type = Column(String)
    elder_post = Column(String)
    district_name = Column(String)
    cottage_name = Column(String)
    congregation_name = Column(String)
    district = relationship("District", back_populates="elders")
    district_id = Column(Integer, ForeignKey("district.id"))
    cottage = relationship("Cottage", back_populates="elders")
    cottage_id = Column(Integer, ForeignKey("cottage.id"))
    congregation = relationship("Congregation", back_populates="elders")
    congregation_id = Column(Integer, ForeignKey("congregation.id"))
    date_created = Column(DateTime, default=datetime.today())


class ResetPassword(Base):
    __tablename__ = "reset_password"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String)
    reset_code = Column(String)
    status = Column(String, default="1")
    expires_in = Column(DateTime, default=datetime.utcnow() + timedelta(minutes=5))
