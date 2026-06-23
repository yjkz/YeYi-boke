from datetime import datetime

from pydantic import BaseModel, Field


class CommentCreate(BaseModel):
    post_slug: str
    parent_id: int | None = None
    nickname: str = Field(..., min_length=1, max_length=50)
    email: str | None = Field(None, max_length=100)
    website: str | None = Field(None, max_length=200)
    content: str = Field(..., min_length=1, max_length=2000)


class CommentUpdate(BaseModel):
    status: str = Field(..., pattern="^(approved|rejected)$")


class CommentResponse(BaseModel):
    id: int
    post_id: int
    parent_id: int | None
    nickname: str
    website: str | None
    content: str
    status: str
    created_at: datetime
    replies: list["CommentResponse"] = []

    model_config = {"from_attributes": True}


class AdminCommentResponse(BaseModel):
    id: int
    post_id: int
    parent_id: int | None
    nickname: str
    email: str | None
    website: str | None
    content: str
    status: str
    visitor_ip: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class AdminCommentListResponse(BaseModel):
    items: list[AdminCommentResponse]
    total: int
    page: int
    page_size: int
