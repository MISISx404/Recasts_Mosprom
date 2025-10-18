"""add phone and name fields to users

Revision ID: 978fe7ab0018
Revises: 
Create Date: 2025-10-19 01:56:04.612685

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg


# revision identifiers, used by Alembic.
revision: str = '978fe7ab0018'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # ---- users table ----
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("phone", sa.String(length=255), nullable=False, unique=True),
        sa.Column("firstname", sa.String(length=255), nullable=True),
        sa.Column("surname", sa.String(length=255), nullable=True),
        sa.Column("lastname", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
    )

    # ---- posts table ----
    op.create_table(
        "posts",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("categories", pg.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("age_segment", sa.Integer(), nullable=True),
        sa.Column("community_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("author_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("author_name", sa.String(length=255), nullable=True),
    )

    # ---- comments table ----
    op.create_table(
        "comments",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("post_id", sa.Integer(), sa.ForeignKey("posts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("parent_id", sa.Integer(), sa.ForeignKey("comments.id", ondelete="CASCADE"), nullable=True),
        sa.Column("author_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("author_name", sa.String(length=255), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
    )

    # ---- likes table ----
    op.create_table(
        "likes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("post_id", sa.Integer(), sa.ForeignKey("posts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
    )
    op.create_unique_constraint("uix_user_post_like", "likes", ["user_id", "post_id"])


def downgrade():
    # Drop tables in reverse order to respect FKs
    op.drop_constraint("uix_user_post_like", "likes", type_="unique")
    op.drop_table("likes")
    op.drop_table("comments")
    op.drop_table("posts")
    op.drop_table("users")