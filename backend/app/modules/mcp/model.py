from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class MCPServiceSettings(Base):
    __tablename__ = "mcp_service_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    api_key_ciphertext: Mapped[str | None] = mapped_column(Text)
    api_key_fingerprint: Mapped[str | None] = mapped_column(String(64))
    api_key_last4: Mapped[str | None] = mapped_column(String(4))
    rate_limit: Mapped[int] = mapped_column(Integer, nullable=False, default=120)
    rate_window: Mapped[int] = mapped_column(Integer, nullable=False, default=60)
    allowed_hosts: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    allowed_origins: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    log_retention_days: Mapped[int] = mapped_column(Integer, nullable=False, default=90)
    updated_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


class MCPApiKey(Base):
    __tablename__ = "mcp_api_keys"
    __table_args__ = (
        Index("ix_mcp_api_keys_fingerprint", "fingerprint", unique=True),
        Index("ix_mcp_api_keys_enabled", "enabled"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    api_key_ciphertext: Mapped[str] = mapped_column(Text, nullable=False)
    fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    last4: Mapped[str] = mapped_column(String(4), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    usage_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


class MCPRequestLog(Base):
    __tablename__ = "mcp_request_logs"
    __table_args__ = (
        Index("ix_mcp_logs_request_id", "request_id"),
        Index("ix_mcp_logs_client_ip", "client_ip"),
        Index("ix_mcp_logs_rpc_method", "rpc_method"),
        Index("ix_mcp_logs_tool_name", "tool_name"),
        Index("ix_mcp_logs_success", "success"),
        Index("ix_mcp_logs_api_key_fingerprint", "api_key_fingerprint"),
        Index("ix_mcp_logs_api_key_id", "api_key_id"),
        Index("ix_mcp_logs_created_at", "created_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    request_id: Mapped[str] = mapped_column(String(64), nullable=False)
    client_ip: Mapped[str | None] = mapped_column(String(45))
    user_agent: Mapped[str | None] = mapped_column(String(500))
    rpc_method: Mapped[str | None] = mapped_column(String(100))
    tool_name: Mapped[str | None] = mapped_column(String(120))
    success: Mapped[bool] = mapped_column(Boolean, nullable=False)
    http_status: Mapped[int | None] = mapped_column(Integer)
    duration_ms: Mapped[int | None] = mapped_column(Integer)
    error_message: Mapped[str | None] = mapped_column(String(500))
    resource_type: Mapped[str | None] = mapped_column(String(50))
    resource_id: Mapped[str | None] = mapped_column(String(100))
    resource_slug: Mapped[str | None] = mapped_column(String(200))
    api_key_id: Mapped[int | None] = mapped_column(Integer)
    api_key_name: Mapped[str | None] = mapped_column(String(120))
    api_key_fingerprint: Mapped[str | None] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
