import inspect

from fastapi import HTTPException, Request, status

from app.redis_client import redis_client


def rate_limit(limit: int, window: int):
    async def dependency(request: Request):
        ip = request.headers.get("x-real-ip") or request.headers.get("x-forwarded-for", "").split(",")[0].strip()
        ip = ip or (request.client.host if request.client else "unknown")
        key = f"rate_limit:{request.url.path}:{ip}"
        current = await redis_client.get(key)
        if current is not None and int(current) >= limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
            )
        pipe = redis_client.pipeline()
        if inspect.isawaitable(pipe):
            pipe = await pipe
        for operation in (pipe.incr(key), pipe.expire(key, window)):
            if inspect.isawaitable(operation):
                await operation
        result = pipe.execute()
        if inspect.isawaitable(result):
            await result

    return dependency
