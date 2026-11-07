"""add refresh_token_criptografado to conta_anuncio

Revision ID: b87b9d098acc
Revises: 4c0ab5873969
Create Date: 2026-11-07 18:15:23.227523

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b87b9d098acc'
down_revision = '4c0ab5873969'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('conta_anuncio', sa.Column('refresh_token_criptografado', sa.LargeBinary(), nullable=True))


def downgrade():
    op.drop_column('conta_anuncio', 'refresh_token_criptografado')
