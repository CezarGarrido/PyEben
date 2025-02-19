"""Adicionando Campos na Tabela Company

Revision ID: 8ea4e57cbb27
Revises: 10df10f143a3
Create Date: 2025-02-15 11:35:23.540479

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8ea4e57cbb27'
down_revision: Union[str, None] = '10df10f143a3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('company_addresses',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('company_id', sa.BigInteger(), nullable=False),
    sa.Column('street', sa.String(length=255), nullable=False),
    sa.Column('neighborhood', sa.String(length=255), nullable=True),
    sa.Column('complement', sa.String(length=255), nullable=True),
    sa.Column('city', sa.String(length=255), nullable=False),
    sa.Column('state', sa.String(length=2), nullable=False),
    sa.Column('postal_code', sa.String(length=20), nullable=True),
    sa.Column('number', sa.String(length=100), nullable=False),
    sa.Column('country', sa.String(length=60), nullable=True),
    sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('company_id')
    )
    op.create_table('company_contacts',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('company_id', sa.BigInteger(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('phone', sa.String(length=60), nullable=False),
    sa.Column('email', sa.String(length=60), nullable=True),
    sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('company_id', 'phone', 'email', name='uq_company_contact')
    )
    op.alter_column('companies', 'id',
               existing_type=sa.INTEGER(),
               type_=sa.BigInteger(),
               existing_nullable=False,
               autoincrement=True,
               existing_server_default=sa.text("nextval('companies_id_seq'::regclass)"))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('companies', 'id',
               existing_type=sa.BigInteger(),
               type_=sa.INTEGER(),
               existing_nullable=False,
               autoincrement=True,
               existing_server_default=sa.text("nextval('companies_id_seq'::regclass)"))
    op.drop_table('company_contacts')
    op.drop_table('company_addresses')
    # ### end Alembic commands ###
