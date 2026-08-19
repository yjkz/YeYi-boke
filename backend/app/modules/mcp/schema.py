from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class MCPSettingsUpdate(BaseModel):
    enabled: bool | None = None
    api_key: str | None = Field(default=None, min_length=8, max_length=512)
    rate_limit: int | None = Field(default=None, ge=1, le=10_000)
    rate_window: int | None = Field(default=None, ge=1, le=86_400)
    allowed_hosts: list[str] | None = Field(default=None, max_length=50)
    allowed_origins: list[str] | None = Field(default=None, max_length=50)
    log_retention_days: int | None = Field(default=None, ge=1, le=3_650)

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    @field_validator("allowed_hosts", "allowed_origins")
    @classmethod
    def validate_allowlist(cls, values: list[str] | None) -> list[str] | None:
        if values is None:
            return values
        if any(not value for value in values):
            raise ValueError("allowlist entries cannot be empty")
        if len(set(values)) != len(values):
            raise ValueError("allowlist entries must be unique")
        return values


class MCPSettingsResponse(BaseModel):
    enabled: bool
    api_key_configured: bool
    api_key_fingerprint: str | None
    api_key_last4: str | None
    rate_limit: int
    rate_window: int
    allowed_hosts: list[str]
    allowed_origins: list[str]
    log_retention_days: int
    public_url: str
    updated_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class MCPApiKeyCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    api_key: str = Field(min_length=8, max_length=512)

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class MCPApiKeyUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    enabled: bool | None = None

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class MCPApiKeyResponse(BaseModel):
    id: int
    name: str
    fingerprint: str
    last4: str
    enabled: bool
    usage_count: int
    last_used_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MCPApiKeyListResponse(BaseModel):
    items: list[MCPApiKeyResponse]
    total: int


class MCPApiKeyExportResponse(BaseModel):
    url: str


class MCPOverviewResponse(BaseModel):
    settings: MCPSettingsResponse
    last_24h_total: int
    last_24h_success: int
    last_24h_failure: int


class MCPRequestLogResponse(BaseModel):
    id: int
    request_id: str
    client_ip: str | None
    user_agent: str | None
    rpc_method: str | None
    tool_name: str | None
    success: bool
    http_status: int | None
    duration_ms: int | None
    error_message: str | None
    resource_type: str | None
    resource_id: str | None
    resource_slug: str | None
    api_key_id: int | None
    api_key_name: str | None
    api_key_fingerprint: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MCPRequestLogListResponse(BaseModel):
    items: list[MCPRequestLogResponse]
    total: int
    page: int
    page_size: int


class MCPLogCleanupResponse(BaseModel):
    deleted_count: int
