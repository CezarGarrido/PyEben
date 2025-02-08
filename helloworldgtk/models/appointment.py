from sqlalchemy import TEXT, CheckConstraint, Column, BigInteger, String, ForeignKey, DateTime, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base

class Appointment(Base):
    __tablename__ = 'appointments'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    company_id = Column(BigInteger, ForeignKey('companies.id', ondelete='CASCADE'), nullable=False)
    user_creator_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    date = Column(DateTime, nullable=True)
    time = Column(String(20), nullable=True)
    event_type = Column(String(20), nullable=False, default='Ligação')
    notes = Column(String(255), nullable=True)

    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    company = relationship("Company", back_populates="appointments")
    calls = relationship("AppointmentCall", back_populates="appointment", uselist=False, cascade="all, delete-orphan")
    
    __table_args__ = (
        CheckConstraint("event_type = 'Ligação'"),
    )

class AppointmentCall(Base):
    __tablename__ = 'appointment_calls'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    appointment_id = Column(BigInteger, ForeignKey('appointments.id'), nullable=False)
    donor_id = Column(BigInteger, ForeignKey('donors.id', ondelete='CASCADE'), nullable=False)
    phone = Column(TEXT, nullable=True)
    status = Column(String(20), nullable=False, default="Agendado")
    duration = Column(String(30), nullable=True)
    
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    appointment = relationship("Appointment", back_populates="calls")
    donor = relationship("Donor")

    __table_args__ = (
        CheckConstraint("status IN ('Agendado', 'Realizado', 'Cancelado')"),
    )