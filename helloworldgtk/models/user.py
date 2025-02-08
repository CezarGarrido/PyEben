from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import bcrypt

from .base import Base
from .role import Role
from .company import Company

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    username = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    active = Column(Boolean, default=True)
    photo = Column(String(255), nullable=True)
    role_id = Column(Integer, ForeignKey('roles.id'))
    user_creator_id = Column(Integer, ForeignKey('users.id'), nullable=True)  # Referência ao criador do usuário
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    role = relationship("Role", back_populates="users")
    company = relationship("Company", back_populates="users")
    creator = relationship("User", remote_side=[id], backref="created_users")  # Relacionamento recursivo
    
    @staticmethod
    def hash_password(plain_password: str) -> str:
        """Gera um hash seguro para a senha usando bcrypt."""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(plain_password.encode("utf-8"), salt).decode("utf-8")

    @staticmethod
    def check_password(plain_password: str, hashed_password: str) -> bool:
        """Verifica se a senha fornecida corresponde ao hash armazenado."""
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

    def set_password(self, plain_password: str):
        """Define a senha do usuário como um hash seguro."""
        self.password = self.hash_password(plain_password)
