"""Add age restrictions and quality scoring

Revision ID: 8d309ba7d5f4
Revises: 978fe7ab0018
Create Date: 2025-10-19 04:26:07.770500

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8d309ba7d5f4'
down_revision: Union[str, None] = '978fe7ab0018'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Добавляем поля в таблицу users
    op.add_column('users', sa.Column('age', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('total_points', sa.Float(), nullable=False, server_default='0.0'))
    
    # Добавляем поля в таблицу posts
    op.add_column('posts', sa.Column('age_restriction', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('posts', sa.Column('quality_score', sa.Float(), nullable=True))
    op.add_column('posts', sa.Column('points_awarded', sa.Float(), nullable=True))


def downgrade():
    # Удаляем поля из таблицы posts
    op.drop_column('posts', 'points_awarded')
    op.drop_column('posts', 'quality_score')
    op.drop_column('posts', 'age_restriction')
    
    # Удаляем поля из таблицы users
    op.drop_column('users', 'total_points')
    op.drop_column('users', 'age')