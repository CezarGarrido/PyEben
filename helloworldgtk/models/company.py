from sqlalchemy import TIMESTAMP, Column, BigInteger, ForeignKey, String, DateTime, func
import sqlalchemy
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import Base

class Company(Base):
    __tablename__ = 'companies'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    cnpj = Column(String(255), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    # Relacionamento com Users e Roles

    appointments = relationship("Appointment", back_populates="company",  lazy="joined", cascade="all, delete-orphan")
    donations = relationship("Donation", back_populates="company",  lazy="joined", cascade="all, delete-orphan")

    users = relationship("User", back_populates="company", lazy="joined")
    roles = relationship("Role", back_populates="company", lazy="joined")
    donors = relationship("Donor", back_populates="company", lazy="joined")
    employees = relationship("Employee", back_populates="company", cascade="all, delete-orphan")

    contacts = relationship("CompanyContact", back_populates="company", cascade="all, delete-orphan")
    addresses = relationship("CompanyAddress", back_populates="company", uselist=False, cascade="all, delete-orphan")
    

class CompanyContact(Base):
    __tablename__ = 'company_contacts'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    company_id = Column(BigInteger, ForeignKey('companies.id', ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    phone = Column(String(60), nullable=False)
    email = Column(String(60))

    company = relationship("Company", back_populates="contacts")

    __table_args__ = (  # Garante a unicidade de contatos por funcionário
        sqlalchemy.UniqueConstraint('company_id', 'phone', 'email', name='uq_company_contact'),
    )


class CompanyAddress(Base):
    __tablename__ = 'company_addresses'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    company_id = Column(BigInteger, ForeignKey('companies.id', ondelete="CASCADE"), nullable=False, unique=True)
    street = Column(String(255), nullable=False)
    neighborhood = Column(String(255))
    complement = Column(String(255))
    city = Column(String(255), nullable=False)
    state = Column(String(2), nullable=False)  # Estado (UF) com 2 caracteres
    postal_code = Column(String(20))
    number = Column(String(100), nullable=False)
    country = Column(String(60), default='Brazil')

    company = relationship("Company", back_populates="addresses")
