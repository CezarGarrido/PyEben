from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from .base import Base
from .company import Company

class Role(Base):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    active = Column(Boolean, default=True)
    description = Column(String(255), nullable=True)
    role = Column(String(255), nullable=True)

    # Relacionamento reverso, será preenchido depois
    users = relationship("User", back_populates="role", lazy="joined")
    # Relacionamento com Company
    company = relationship("Company", back_populates="roles")
