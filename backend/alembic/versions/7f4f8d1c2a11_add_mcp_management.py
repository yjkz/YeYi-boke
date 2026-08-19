"""add MCP management settings and request logs

Revision ID: 7f4f8d1c2a11
Revises: 19c34fbeac15
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "7f4f8d1c2a11"
down_revision: Union[str, None] = "19c34fbeac15"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "mcp_service_settings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("api_key_ciphertext", sa.Text()),
        sa.Column("api_key_fingerprint", sa.String(64)),
        sa.Column("api_key_last4", sa.String(4)),
        sa.Column("rate_limit", sa.Integer(), nullable=False, server_default="120"),
        sa.Column("rate_window", sa.Integer(), nullable=False, server_default="60"),
        sa.Column("allowed_hosts", sa.JSON(), nullable=False),
        sa.Column("allowed_origins", sa.JSON(), nullable=False),
        sa.Column("log_retention_days", sa.Integer(), nullable=False, server_default="90"),
        sa.Column("updated_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_table(
        "mcp_request_logs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("request_id", sa.String(64), nullable=False),
        sa.Column("client_ip", sa.String(45)),
        sa.Column("user_agent", sa.String(500)),
        sa.Column("rpc_method", sa.String(100)),
        sa.Column("tool_name", sa.String(120)),
        sa.Column("success", sa.Boolean(), nullable=False),
        sa.Column("http_status", sa.Integer()),
        sa.Column("duration_ms", sa.Integer()),
        sa.Column("error_message", sa.String(500)),
        sa.Column("resource_type", sa.String(50)),
        sa.Column("resource_id", sa.String(100)),
        sa.Column("resource_slug", sa.String(200)),
        sa.Column("api_key_fingerprint", sa.String(64)),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )
    for name, table, column in (
        ("ix_mcp_logs_request_id", "mcp_request_logs", "request_id"),
        ("ix_mcp_logs_client_ip", "mcp_request_logs", "client_ip"),
        ("ix_mcp_logs_rpc_method", "mcp_request_logs", "rpc_method"),
        ("ix_mcp_logs_tool_name", "mcp_request_logs", "tool_name"),
        ("ix_mcp_logs_success", "mcp_request_logs", "success"),
        ("ix_mcp_logs_api_key_fingerprint", "mcp_request_logs", "api_key_fingerprint"),
        ("ix_mcp_logs_created_at", "mcp_request_logs", "created_at"),
    ):
        op.create_index(name, table, [column])


def downgrade() -> None:
    for name in (
        "ix_mcp_logs_created_at", "ix_mcp_logs_api_key_fingerprint", "ix_mcp_logs_success",
        "ix_mcp_logs_tool_name", "ix_mcp_logs_rpc_method", "ix_mcp_logs_client_ip", "ix_mcp_logs_request_id",
    ):
        op.drop_index(name, table_name="mcp_request_logs")
    op.drop_table("mcp_request_logs")
    op.drop_table("mcp_service_settings")
