from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from mainApp.data.database import Base
from datetime import datetime
from sqlalchemy.orm import relationship


class Congregation(Base):
    __tablename__ = "congregation"

    id = Column(Integer, primary_key=True, index=True)
    congregation_name = Column(String)
    location = Column(String)
    date_setup = Column(String)
    congregation_head = Column(String)
    assistant_congregation_head = Column(String)
    admin_name = Column(String)
    admin = relationship("Admin", back_populates="congregation")
    admin_id = Column(Integer, ForeignKey("admin.id"))
    members = relationship("Member", back_populates="congregation", cascade="all, delete-orphan")
    elders = relationship("Elder", back_populates="congregation", cascade="all, delete-orphan")
    cottages = relationship("Cottage", back_populates="congregation", cascade="all, delete-orphan")
    districts = relationship("District", back_populates="congregation", cascade="all, delete-orphan")
    ministries = relationship("Ministry", back_populates="congregation", cascade="all, delete-orphan")
    baptism = relationship("Baptism", back_populates="congregation", cascade="all, delete-orphan")
    confirmation = relationship("Confirmation", back_populates="congregation", cascade="all, delete-orphan")
    communion_services = relationship("CommunionService", back_populates="congregation", cascade="all, delete-orphan")
    service = relationship("Service", back_populates="congregation", cascade="all, delete-orphan")
    date_created = Column(DateTime, default=datetime.today())


class District(Base):
    __tablename__ = "district"

    id = Column(Integer, primary_key=True, index=True)
    district_name = Column(String)
    coverage_area = Column(String)
    date_setup = Column(String)
    district_head = Column(String)
    assistant_district_head = Column(String)
    congregation_name = Column(String)
    members = relationship("Member", back_populates="district", cascade="all, delete-orphan")
    elders = relationship("Elder", back_populates="district", cascade="all, delete-orphan")
    cottages = relationship("Cottage", back_populates="district", cascade="all, delete-orphan")
    congregation = relationship("Congregation", back_populates="districts")
    congregation_id = Column(Integer, ForeignKey("congregation.id"))
    date_created = Column(DateTime, default=datetime.today())


class Cottage(Base):
    __tablename__ = "cottage"

    id = Column(Integer, primary_key=True, index=True)
    cottage_name = Column(String)
    cottage_address = Column(String)
    date_setup = Column(String)
    cottage_head = Column(String)
    assistant_cottage_head = Column(String)
    district_name = Column(String)
    congregation_name = Column(String)
    members = relationship("Member", back_populates="cottage", cascade="all, delete-orphan")
    elders = relationship("Elder", back_populates="cottage", cascade="all, delete-orphan")
    district = relationship("District", back_populates="cottages")
    district_id = Column(Integer, ForeignKey("district.id"))
    congregation = relationship("Congregation", back_populates="cottages")
    congregation_id = Column(Integer, ForeignKey("congregation.id"))
    date_created = Column(DateTime, default=datetime.today())


class Ministry(Base):
    __tablename__ = "ministry"

    id = Column(Integer, primary_key=True, index=True)
    ministry_name = Column(String)
    ministry_head = Column(String)
    assistant_ministry_head = Column(String)
    members = relationship("MinistryMembers", back_populates="ministry", cascade="all, delete-orphan")
    date_setup = Column(String)
    congregation_name = Column(String)
    congregation = relationship("Congregation", back_populates="ministries")
    congregation_id = Column(Integer, ForeignKey("congregation.id"))
    date_created = Column(DateTime, default=datetime.today())
