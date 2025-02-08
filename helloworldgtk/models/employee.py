from sqlalchemy import (
    Column, BigInteger, String, Date, Numeric, Boolean, ForeignKey, TIMESTAMP
)
import sqlalchemy
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, declarative_base

from .base import Base

class Employee(Base):
    __tablename__ = 'employees'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    company_id = Column(BigInteger, ForeignKey('companies.id', ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    date_of_birth = Column(Date)
    hire_date = Column(Date)
    termination_date = Column(Date)
    ctps = Column(String(100))
    cnpj = Column(String(14), unique=True)
    cpf = Column(String(11), unique=True)
    rg = Column(String(30))
    rg_issuer = Column(String(30))
    position = Column(String(100))
    department = Column(String(100))
    salary = Column(Numeric(15, 2))
    active = Column(Boolean, default=True)
    marital_status = Column(String(255))
    wife_name = Column(String(255))
    wife_date_of_birth = Column(Date)
    user_creator_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    deleted_at = Column(TIMESTAMP, nullable=True)

    contacts = relationship("EmployeeContact", back_populates="employee", cascade="all, delete-orphan")
    addresses = relationship("EmployeeAddress", back_populates="employee", uselist=False, cascade="all, delete-orphan")
    company = relationship("Company", back_populates="employees")

class EmployeeContact(Base):
    __tablename__ = 'employee_contacts'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    employee_id = Column(BigInteger, ForeignKey('employees.id', ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    phone = Column(String(60), nullable=False)
    email = Column(String(60))

    employee = relationship("Employee", back_populates="contacts")

    __table_args__ = (  # Garante a unicidade de contatos por funcionário
        sqlalchemy.UniqueConstraint('employee_id', 'phone', 'email', name='uq_employee_contact'),
    )


class EmployeeAddress(Base):
    __tablename__ = 'employee_addresses'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    employee_id = Column(BigInteger, ForeignKey('employees.id', ondelete="CASCADE"), nullable=False, unique=True)
    street = Column(String(255), nullable=False)
    neighborhood = Column(String(255))
    complement = Column(String(255))
    city = Column(String(255), nullable=False)
    state = Column(String(2), nullable=False)  # Estado (UF) com 2 caracteres
    postal_code = Column(String(20))
    number = Column(String(100), nullable=False)
    country = Column(String(60), default='Brazil')

    employee = relationship("Employee", back_populates="addresses")
