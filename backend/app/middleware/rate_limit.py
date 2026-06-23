from fastapi import HTTPException, Request, status

from app.redis_client import redis_client


def rate_limit(limit: int, window: int):
    async def dependency(request: Request):
        ip = request.client.host if request.client else "unknown"
        key = f"rate_limit:{request.url.path}:{ip}"
        current = await redis_client.get(key)
        if current is not None and int(current) >= limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
            )
        pipe = redis_client.pipeline()
        pipe.incr(key)
        pipe.expire(key, window)
        await pipe.execute()

    return dependency
