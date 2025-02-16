from sqlalchemy import Column, BigInteger, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base
import bcrypt

class User(Base):
    __tablename__ = 'users'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    company_id = Column(BigInteger, ForeignKey('companies.id'), nullable=False)

    # 🔹 Vincula o usuário a um funcionário
    employee_id = Column(BigInteger, ForeignKey('employees.id', ondelete="SET NULL"), nullable=True)

    username = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    active = Column(Boolean, default=True)
    photo = Column(String(255), nullable=True)
    role_id = Column(BigInteger, ForeignKey('roles.id'))

    # 🔹 Especificamos explicitamente a chave estrangeira correta para evitar erro
    user_creator_id = Column(BigInteger, ForeignKey('users.id', ondelete="SET NULL"), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    role = relationship("Role", back_populates="users")
    company = relationship("Company", back_populates="users")

    # 🔹 Corrigimos o erro especificando `foreign_keys`
    creator = relationship("User", remote_side=[id], backref="created_users")
    
    # 🔹 Aqui especificamos que `employee_id` é a chave a ser usada no relacionamento
    employee = relationship("Employee", back_populates="users", foreign_keys=[employee_id])
    
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