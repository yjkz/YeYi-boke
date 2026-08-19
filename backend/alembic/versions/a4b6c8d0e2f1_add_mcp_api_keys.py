"""add multiple MCP API keys and key metadata to request logs

Revision ID: a4b6c8d0e2f1
Revises: 7f4f8d1c2a11
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a4b6c8d0e2f1"
down_revision: Union[str, None] = "7f4f8d1c2a11"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "mcp_api_keys",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("api_key_ciphertext", sa.Text(), nullable=False),
        sa.Column("fingerprint", sa.String(64), nullable=False),
        sa.Column("last4", sa.String(4), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("usage_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_used_at", sa.DateTime()),
        sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index("ix_mcp_api_keys_fingerprint", "mcp_api_keys", ["fingerprint"], unique=True)
    op.create_index("ix_mcp_api_keys_enabled", "mcp_api_keys", ["enabled"])
    op.add_column("mcp_request_logs", sa.Column("api_key_id", sa.Integer()))
    op.add_column("mcp_request_logs", sa.Column("api_key_name", sa.String(120)))
    op.create_index("ix_mcp_logs_api_key_id", "mcp_request_logs", ["api_key_id"])


def downgrade() -> None:
    op.drop_index("ix_mcp_logs_api_key_id", table_name="mcp_request_logs")
    op.drop_column("mcp_request_logs", "api_key_name")
    op.drop_column("mcp_request_logs", "api_key_id")
    op.drop_index("ix_mcp_api_keys_enabled", table_name="mcp_api_keys")
    op.drop_index("ix_mcp_api_keys_fingerprint", table_name="mcp_api_keys")
    op.drop_table("mcp_api_keys")
