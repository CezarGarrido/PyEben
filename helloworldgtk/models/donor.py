from datetime import datetime
from sqlalchemy import Column, BigInteger, String, Boolean, ForeignKey, TIMESTAMP
import sqlalchemy
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base

class Donor(Base):
    __tablename__ = 'donors'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    company_id = Column(BigInteger, ForeignKey('companies.id', ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    person_type = Column(String, nullable=False)
    cnpj = Column(String, nullable=True)
    ie = Column(String, nullable=True)
    cpf = Column(String, nullable=True)
    rg = Column(String, nullable=True)
    rg_issuer = Column(String, nullable=True)
    active = Column(Boolean, default=True)
    user_creator_id = Column(BigInteger, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    contacts = relationship("DonorContact", back_populates="donor", cascade="all, delete-orphan")
    addresses = relationship("DonorAddress", back_populates="donor", uselist=False, cascade="all, delete-orphan")
    company = relationship("Company", back_populates="donors")

class DonorContact(Base):
    __tablename__ = 'donor_contacts'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    donor_id = Column(BigInteger, ForeignKey('donors.id', ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    phone = Column(String(60), nullable=False)
    email = Column(String(60))

    donor = relationship("Donor", back_populates="contacts")

    __table_args__ = (  # Garante a unicidade de contatos por funcionário
        sqlalchemy.UniqueConstraint('donor_id', 'phone', 'email', name='uq_donor_contact'),
    )


class DonorAddress(Base):
    __tablename__ = 'donor_addresses'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    donor_id = Column(BigInteger, ForeignKey('donors.id', ondelete="CASCADE"), nullable=False, unique=True)
    street = Column(String(255), nullable=False)
    neighborhood = Column(String(255))
    complement = Column(String(255))
    city = Column(String(255), nullable=False)
    state = Column(String(2), nullable=False)  # Estado (UF) com 2 caracteres
    postal_code = Column(String(20))
    number = Column(String(100), nullable=False)
    country = Column(String(60), default='Brazil')

    donor = relationship("Donor", back_populates="addresses")
