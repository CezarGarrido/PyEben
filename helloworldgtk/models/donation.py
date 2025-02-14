from sqlalchemy import (
    Column, BigInteger, Numeric, Date, String, Boolean, 
    TIMESTAMP, ForeignKey, CheckConstraint, func
)
from sqlalchemy.orm import relationship

from .base import Base

class Donation(Base):
    __tablename__ = 'donations'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    company_id = Column(BigInteger, ForeignKey('companies.id', ondelete='CASCADE'), nullable=False)
    user_creator_id = Column(BigInteger, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    appointment_id = Column(BigInteger, ForeignKey('appointments.id', ondelete='CASCADE'), nullable=True)
    donor_id = Column(BigInteger, ForeignKey('donors.id', ondelete='CASCADE'), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    received_at = Column(Date, nullable=True)
    received_time = Column(String(20), nullable=True)
    paid = Column(Boolean, default=False)
    notes = Column(String(255), nullable=True)
    active = Column(Boolean, default=True)

    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    deleted_at = Column(TIMESTAMP, nullable=True)  # Soft delete
    
    __table_args__ = (
        CheckConstraint('amount > 0', name='check_amount_positive'),
    )
    
    # Definição de relacionamentos (opcional)
    company = relationship("Company", back_populates="donations")
    appointment = relationship("Appointment")
    donor = relationship("Donor")
