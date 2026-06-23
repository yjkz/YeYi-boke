"""initial tables

Revision ID: 19c34fbeac15
Revises:
Create Date: 2026-06-23 20:55:42.912788

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '19c34fbeac15'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # users
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("username", sa.String(50), unique=True, nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("email", sa.String(100)),
        sa.Column("avatar", sa.String(500)),
        sa.Column("role", sa.Enum("admin", "editor", name="user_role"), server_default="admin"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # categories
    op.create_table(
        "categories",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(50), nullable=False),
        sa.Column("slug", sa.String(50), unique=True, nullable=False),
        sa.Column("description", sa.String(200)),
        sa.Column("sort_order", sa.Integer, server_default="0"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    # tags
    op.create_table(
        "tags",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(50), nullable=False),
        sa.Column("slug", sa.String(50), unique=True, nullable=False),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    # posts
    op.create_table(
        "posts",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("slug", sa.String(200), unique=True, nullable=False),
        sa.Column("content_md", sa.Text),
        sa.Column("content_html", sa.Text),
        sa.Column("excerpt", sa.String(500)),
        sa.Column("cover_image", sa.String(500)),
        sa.Column("status", sa.Enum("draft", "published", name="post_status"), server_default="draft"),
        sa.Column("category_id", sa.Integer, sa.ForeignKey("categories.id", ondelete="SET NULL")),
        sa.Column("view_count", sa.Integer, server_default="0"),
        sa.Column("is_top", sa.Boolean, server_default="0"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column("published_at", sa.DateTime),
    )

    # post_tags (association table)
    op.create_table(
        "post_tags",
        sa.Column("post_id", sa.Integer, sa.ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("tag_id", sa.Integer, sa.ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
    )

    # comments
    op.create_table(
        "comments",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("post_id", sa.Integer, sa.ForeignKey("posts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("parent_id", sa.Integer, sa.ForeignKey("comments.id", ondelete="CASCADE")),
        sa.Column("nickname", sa.String(50), nullable=False),
        sa.Column("email", sa.String(100)),
        sa.Column("website", sa.String(200)),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("status", sa.Enum("pending", "approved", "rejected", name="comment_status"), server_default="pending"),
        sa.Column("visitor_ip", sa.String(45)),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    # site_config
    op.create_table(
        "site_config",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("config_key", sa.String(50), unique=True, nullable=False),
        sa.Column("config_value", sa.Text),
        sa.Column("description", sa.String(200)),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # visit_logs
    op.create_table(
        "visit_logs",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("page_path", sa.String(500), nullable=False),
        sa.Column("page_title", sa.String(200)),
        sa.Column("visitor_ip", sa.String(45)),
        sa.Column("user_agent", sa.String(500)),
        sa.Column("referer", sa.String(500)),
        sa.Column("country", sa.String(50)),
        sa.Column("city", sa.String(50)),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    # visit_stats
    op.create_table(
        "visit_stats",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("stat_date", sa.Date, unique=True, nullable=False),
        sa.Column("page_views", sa.Integer, server_default="0"),
        sa.Column("unique_visitors", sa.Integer, server_default="0"),
        sa.Column("top_pages", sa.JSON),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("visit_stats")
    op.drop_table("visit_logs")
    op.drop_table("site_config")
    op.drop_table("comments")
    op.drop_table("post_tags")
    op.drop_table("posts")
    op.drop_table("tags")
    op.drop_table("categories")
    op.drop_table("users")

    # Drop enums
    op.execute("DROP TYPE IF EXISTS comment_status")
    op.execute("DROP TYPE IF EXISTS post_status")
    op.execute("DROP TYPE IF EXISTS user_role")
