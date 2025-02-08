from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import Base

class Company(Base):
    __tablename__ = 'companies'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    cnpj = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamento com Users e Roles
    appointments = relationship("Appointment", back_populates="company",  lazy="joined", cascade="all, delete-orphan")

    users = relationship("User", back_populates="company", lazy="joined")
    roles = relationship("Role", back_populates="company", lazy="joined")
    donors = relationship("Donor", back_populates="company", lazy="joined")

    employees = relationship("Employee", back_populates="company", cascade="all, delete-orphan")
