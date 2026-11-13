
"""add sku and description to products

Revision ID: 0124dd77021a
Revises:
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '0124dd77021a'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'products',
        sa.Column('sku', sa.String(50), nullable=True)
    )

    op.add_column(
        'products',
        sa.Column('description', sa.String(500), nullable=True)
    )

    op.create_index(
        'ix_products_sku',
        'products',
        ['sku'],
        unique=True
    )


def downgrade() -> None:
    op.drop_index('ix_products_sku', table_name='products')

    op.drop_column('products', 'description')
    op.drop_column('products', 'sku')
