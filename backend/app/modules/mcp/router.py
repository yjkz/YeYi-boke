from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import Pagination, require_admin
from app.modules.mcp import service
from app.modules.mcp.model import MCPRequestLog
from app.modules.mcp.schema import (
    MCPApiKeyCreate,
    MCPApiKeyExportResponse,
    MCPApiKeyListResponse,
    MCPApiKeyResponse,
    MCPApiKeyUpdate,
    MCPLogCleanupResponse,
    MCPOverviewResponse,
    MCPRequestLogListResponse,
    MCPRequestLogResponse,
    MCPSettingsResponse,
    MCPSettingsUpdate,
)
from app.modules.users.model import User

router = APIRouter(prefix="/admin/mcp", tags=["mcp-admin"])


@router.get("/overview", response_model=MCPOverviewResponse)
async def get_mcp_overview(db: AsyncSession = Depends(get_db), _user: User = Depends(require_admin)):
    record, total, successful, failed = await service.get_overview(db)
    return MCPOverviewResponse(
        settings=service.serialize_settings(record),
        last_24h_total=total,
        last_24h_success=successful,
        last_24h_failure=failed,
    )


@router.get("/settings", response_model=MCPSettingsResponse)
async def get_mcp_settings(db: AsyncSession = Depends(get_db), _user: User = Depends(require_admin)):
    return service.serialize_settings(await service.get_or_create_settings(db))


@router.put("/settings", response_model=MCPSettingsResponse)
async def update_mcp_settings(
    body: MCPSettingsUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin),
):
    try:
        record = await service.update_settings(db, body, user.id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    # Commit before cache invalidation so a concurrent MCP process never caches the old row again.
    await db.commit()
    await service.invalidate_runtime_settings_cache()
    return service.serialize_settings(record)


@router.get("/keys", response_model=MCPApiKeyListResponse)
async def get_mcp_api_keys(db: AsyncSession = Depends(get_db), _user: User = Depends(require_admin)):
    items = await service.list_api_keys(db)
    return MCPApiKeyListResponse(items=items, total=len(items))


@router.post("/keys", response_model=MCPApiKeyResponse, status_code=201)
async def create_mcp_api_key(
    body: MCPApiKeyCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin),
):
    try:
        record = await service.create_api_key(db, body, user.id)
        await db.commit()
        await service.invalidate_runtime_settings_cache()
        return record
    except ValueError as exc:
        await db.rollback()
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.patch("/keys/{key_id}", response_model=MCPApiKeyResponse)
async def update_mcp_api_key(
    key_id: int,
    body: MCPApiKeyUpdate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_admin),
):
    try:
        record = await service.update_api_key(db, key_id, body)
        await db.commit()
        await service.invalidate_runtime_settings_cache()
        return record
    except ValueError as exc:
        await db.rollback()
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/keys/{key_id}/export-url", response_model=MCPApiKeyExportResponse)
async def export_mcp_api_key_url(
    key_id: int,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_admin),
):
    try:
        return MCPApiKeyExportResponse(url=await service.export_api_key_url(db, key_id))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.delete("/keys/{key_id}", status_code=204)
async def delete_mcp_api_key(
    key_id: int,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_admin),
):
    try:
        await service.delete_api_key(db, key_id)
        await db.commit()
        await service.invalidate_runtime_settings_cache()
    except ValueError as exc:
        await db.rollback()
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/logs", response_model=MCPRequestLogListResponse)
async def get_mcp_logs(
    pagination: Pagination = Depends(),
    tool_name: str | None = Query(None, max_length=120),
    success: bool | None = Query(None),
    client_ip: str | None = Query(None, max_length=45),
    api_key_id: int | None = Query(None, ge=1),
    start_at: datetime | None = Query(None),
    end_at: datetime | None = Query(None),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_admin),
):
    items, total = await service.list_request_logs(
        db,
        offset=pagination.offset,
        limit=pagination.page_size,
        tool_name=tool_name,
        success=success,
        client_ip=client_ip,
        api_key_id=api_key_id,
        start_at=start_at,
        end_at=end_at,
    )
    return MCPRequestLogListResponse(items=items, total=total, page=pagination.page, page_size=pagination.page_size)


@router.post("/logs/cleanup", response_model=MCPLogCleanupResponse)
async def cleanup_mcp_logs(db: AsyncSession = Depends(get_db), _user: User = Depends(require_admin)):
    return MCPLogCleanupResponse(deleted_count=await service.cleanup_expired_logs(db))


@router.get("/logs/{log_id}", response_model=MCPRequestLogResponse)
async def get_mcp_log(log_id: int, db: AsyncSession = Depends(get_db), _user: User = Depends(require_admin)):
    log = await db.get(MCPRequestLog, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="MCP request log not found")
    return log
