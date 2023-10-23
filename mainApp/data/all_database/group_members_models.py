from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from mainApp.data.database import Base
from datetime import datetime
from sqlalchemy.orm import relationship


class MinistryMembers(Base):
    __tablename__ = "ministry_members"

    id = Column(Integer, primary_key=True, index=True)
    participant_name = Column(String)
    ministry_name = Column(String)
    date_joined = Column(String)
    ministry = relationship("Ministry", back_populates="members")
    ministry_id = Column(Integer, ForeignKey("ministry.id"))
    date_created = Column(DateTime, default=datetime.today())


class CommunionServiceParticipant(Base):
    __tablename__ = "communion_service_participant"

    id = Column(Integer, primary_key=True, index=True)
    participant_name = Column(String)
    participant_type = Column(String)
    service_name = Column(String)
    communion_service = relationship("CommunionService", back_populates="participants")
    communion_service_id = Column(Integer, ForeignKey("communion_service.id"))
    date_created = Column(DateTime, default=datetime.today())


class BaptismParticipant(Base):
    __tablename__ = "baptism_participant"

    id = Column(Integer, primary_key=True, index=True)
    participant_name = Column(String)
    baptism_name = Column(String)
    baptism = relationship("Baptism", back_populates="baptism_participants")
    baptism_id = Column(Integer, ForeignKey("baptism.id"))
    date_created = Column(DateTime, default=datetime.today())


class ConfirmationParticipant(Base):
    __tablename__ = "confirmation_participant"

    id = Column(Integer, primary_key=True, index=True)
    participant_name = Column(String)
    confirmation_name = Column(String)
    confirmation = relationship("Confirmation", back_populates="confirmation_participants")
    confirmation_id = Column(Integer, ForeignKey("confirmation.id"))
    date_created = Column(DateTime, default=datetime.today())
