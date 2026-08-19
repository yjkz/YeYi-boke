from contextvars import ContextVar
from dataclasses import dataclass, field
from uuid import uuid4


@dataclass
class MCPRequestContext:
    request_id: str = field(default_factory=lambda: uuid4().hex)
    client_ip: str | None = None
    user_agent: str | None = None
    api_key_fingerprint: str | None = None
    api_key_id: int | None = None
    api_key_name: str | None = None


request_context: ContextVar[MCPRequestContext | None] = ContextVar("mcp_request_context", default=None)
