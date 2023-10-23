from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from mainApp.data.database import Base
from datetime import datetime
from sqlalchemy.orm import relationship


class CommunionService(Base):
    __tablename__ = "communion_service"

    id = Column(Integer, primary_key=True, index=True)
    service_name = Column(String)
    service_date = Column(String)
    service_head_count = Column(String)
    congregation_name = Column(String)
    congregation = relationship("Congregation", back_populates="communion_services")
    congregation_id = Column(Integer, ForeignKey("congregation.id"))
    participants = relationship("CommunionServiceParticipant", back_populates="communion_service",
                                cascade="all, delete-orphan")
    date_created = Column(DateTime, default=datetime.today())


class Service(Base):
    __tablename__ = "service"

    id = Column(Integer, primary_key=True, index=True)
    service_date = Column(String)
    service_name = Column(String)
    description = Column(String)
    service_type = Column(String)
    no_men = Column(String)
    no_women = Column(String)
    no_children = Column(String)
    no_visitors = Column(String)
    head_minister = Column(String)
    assistant_minister = Column(String)
    time_period = Column(String)
    congregation_name = Column(String)
    congregation = relationship("Congregation", back_populates="service")
    congregation_id = Column(Integer, ForeignKey("congregation.id"))
    date_created = Column(DateTime, default=datetime.today())


class Baptism(Base):
    __tablename__ = "baptism"

    id = Column(Integer, primary_key=True, index=True)
    baptism_name = Column(String)
    minister = Column(String)
    baptism_date = Column(String)
    congregation_name = Column(String)
    congregation = relationship("Congregation", back_populates="baptism")
    congregation_id = Column(Integer, ForeignKey("congregation.id"))
    baptism_participants = relationship("BaptismParticipant", back_populates="baptism", cascade="all, delete-orphan")
    date_created = Column(DateTime, default=datetime.today())


class Confirmation(Base):
    __tablename__ = "confirmation"

    id = Column(Integer, primary_key=True, index=True)
    confirmation_name = Column(String)
    minister = Column(String)
    confirmation_date = Column(String)
    congregation_name = Column(String)
    confirmation_participants = relationship("ConfirmationParticipant", back_populates="confirmation",
                                             cascade="all, delete-orphan")
    congregation = relationship("Congregation", back_populates="confirmation")
    congregation_id = Column(Integer, ForeignKey("congregation.id"))
    date_created = Column(DateTime, default=datetime.today())
