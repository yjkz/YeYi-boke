import os
import uuid

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.modules.users.model import User
from app.utils.security import create_access_token, create_refresh_token, decode_token, hash_password, verify_password
from app.redis_client import redis_client


async def authenticate_user(db: AsyncSession, username: str, password: str) -> User | None:
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if user and verify_password(password, user.password_hash):
        return user
    return None


def create_tokens(user: User) -> dict:
    payload = {"sub": str(user.id), "username": user.username, "role": user.role}
    return {
        "access_token": create_access_token(payload),
        "refresh_token": create_refresh_token(payload),
    }


async def store_refresh_token(user_id: int, token: str) -> None:
    from app.config import settings
    ttl = settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 86400
    await redis_client.set(f"refresh_token:{user_id}", token, ex=ttl)


async def invalidate_refresh_token(user_id: int) -> None:
    await redis_client.delete(f"refresh_token:{user_id}")


async def refresh_access_token(db: AsyncSession, token: str) -> dict:
    try:
        payload = decode_token(token)
        if payload.get("type") != "refresh":
            raise ValueError("Not a refresh token")
    except Exception:
        raise ValueError("Invalid refresh token")

    user_id = payload.get("sub")
    stored = await redis_client.get(f"refresh_token:{user_id}")
    if stored != token:
        raise ValueError("Refresh token revoked")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise ValueError("User not found")

    tokens = create_tokens(user)
    await store_refresh_token(user_id, tokens["refresh_token"])
    return tokens


async def upload_image(file: UploadFile) -> str:
    ext = os.path.splitext(file.filename)[1] if file.filename else ".png"
    filename = f"{uuid.uuid4().hex}{ext}"
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    filepath = os.path.join(settings.UPLOAD_DIR, filename)

    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise ValueError("File too large")

    with open(filepath, "wb") as f:
        f.write(content)

    return f"/uploads/{filename}"
