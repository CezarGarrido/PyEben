"""Inserindo dados iniciais

Revision ID: 10df10f143a3
Revises: 6b14acdad3a6
Create Date: 2025-02-14 15:52:29.418599

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text

# revision identifiers, used by Alembic.
revision: str = '10df10f143a3'
down_revision: Union[str, None] = '6b14acdad3a6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    """Insere os dados iniciais nas tabelas."""

    conn = op.get_bind()

    # Inserir empresa padrão
    conn.execute(text("""
        INSERT INTO companies (name, cnpj) VALUES ('Empresa Padrão', '12345678000195')
    """))

    # Inserir roles
    conn.execute(text("""
        INSERT INTO roles (company_id, active, description, role)
        VALUES 
        (1, TRUE, 'Administrador', 'ADMIN'),
        (1, TRUE, 'Padrão', 'PADRAO')
    """))

    # Inserir usuário admin
    conn.execute(text("""
        INSERT INTO users (company_id, username, password, email, role_id, active) 
        VALUES 
        (1, 'admin', '$2a$10$St2AvRkC5G9g1R9HmNRTyuCkKyL8051CR2FGkBmpDOJaBznH7xnVK', 'admin@admin.com', 1, TRUE)
    """))

def downgrade():
    """Remove os dados inseridos."""
    conn = op.get_bind()
    conn.execute(text("DELETE FROM users WHERE username = 'admin'"))
    conn.execute(text("DELETE FROM roles WHERE company_id = 1"))
    conn.execute(text("DELETE FROM companies WHERE name = 'Empresa Padrão'"))