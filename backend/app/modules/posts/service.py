from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.posts.model import Category, Post, Tag, post_tags
from app.modules.posts.schema import PostCreate, PostUpdate
from app.utils.markdown import render_markdown
from app.utils.slug import generate_slug


async def get_posts(
    db: AsyncSession,
    offset: int = 0,
    limit: int = 10,
    category_slug: str | None = None,
    tag_slug: str | None = None,
    status: str | None = None,
):
    query = select(Post).options(selectinload(Post.category), selectinload(Post.tags))
    if status:
        query = query.where(Post.status == status)
    query = query.order_by(Post.is_top.desc(), Post.published_at.desc())

    if category_slug:
        query = query.join(Category).where(Category.slug == category_slug)
    if tag_slug:
        query = query.join(post_tags).join(Tag).where(Tag.slug == tag_slug)

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()

    result = await db.execute(query.offset(offset).limit(limit))
    posts = result.scalars().unique().all()
    return posts, total


async def get_post_by_slug(db: AsyncSession, slug: str) -> Post | None:
    result = await db.execute(
        select(Post)
        .options(selectinload(Post.category), selectinload(Post.tags))
        .where(Post.slug == slug)
    )
    return result.scalar_one_or_none()


async def get_post_by_id(db: AsyncSession, post_id: int) -> Post | None:
    result = await db.execute(
        select(Post)
        .options(selectinload(Post.category), selectinload(Post.tags))
        .where(Post.id == post_id)
    )
    return result.scalar_one_or_none()


async def increment_view_count(db: AsyncSession, post: Post) -> None:
    post.view_count += 1
    await db.flush()
    await db.refresh(post)


async def create_post(db: AsyncSession, data: PostCreate) -> Post:
    slug = data.slug or generate_slug(data.title)
    content_html = render_markdown(data.content_md) if data.content_md else ""
    excerpt = data.excerpt or (data.content_md[:200] if data.content_md else "")

    post = Post(
        title=data.title,
        slug=slug,
        content_md=data.content_md,
        content_html=content_html,
        excerpt=excerpt,
        cover_image=data.cover_image,
        category_id=data.category_id,
        is_top=data.is_top,
    )
    db.add(post)
    await db.flush()
    await db.refresh(post)

    if data.tag_ids:
        tags = (await db.execute(select(Tag).where(Tag.id.in_(data.tag_ids)))).scalars().all()
        post.tags = tags

    await db.refresh(post, ["category", "tags"])
    return post


async def update_post(db: AsyncSession, post_id: int, data: PostUpdate) -> Post | None:
    result = await db.execute(
        select(Post).options(selectinload(Post.category), selectinload(Post.tags)).where(Post.id == post_id)
    )
    post = result.scalar_one_or_none()
    if not post:
        return None

    update_data = data.model_dump(exclude_unset=True)
    tag_ids = update_data.pop("tag_ids", None)

    if "content_md" in update_data:
        update_data["content_html"] = render_markdown(update_data["content_md"])
        if "excerpt" not in update_data:
            update_data["excerpt"] = update_data["content_md"][:200]

    for key, value in update_data.items():
        setattr(post, key, value)

    if tag_ids is not None:
        tags = (await db.execute(select(Tag).where(Tag.id.in_(tag_ids)))).scalars().all()
        post.tags = tags

    await db.flush()
    await db.refresh(post)
    return post


async def delete_post(db: AsyncSession, post_id: int) -> bool:
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        return False
    await db.delete(post)
    await db.flush()
    return True


async def publish_post(db: AsyncSession, post_id: int) -> Post | None:
    result = await db.execute(
        select(Post).options(selectinload(Post.category), selectinload(Post.tags)).where(Post.id == post_id)
    )
    post = result.scalar_one_or_none()
    if not post:
        return None
    post.status = "published"
    post.published_at = datetime.now(timezone.utc)
    await db.flush()
    await db.refresh(post)
    return post


async def draft_post(db: AsyncSession, post_id: int) -> Post | None:
    result = await db.execute(
        select(Post).options(selectinload(Post.category), selectinload(Post.tags)).where(Post.id == post_id)
    )
    post = result.scalar_one_or_none()
    if not post:
        return None
    post.status = "draft"
    await db.flush()
    await db.refresh(post)
    return post


async def get_categories(db: AsyncSession) -> list[Category]:
    result = await db.execute(select(Category).order_by(Category.sort_order, Category.id))
    return list(result.scalars().all())


async def get_categories_page(db: AsyncSession, offset: int = 0, limit: int = 50):
    base = select(Category)
    total = (await db.execute(select(func.count()).select_from(base.subquery()))).scalar() or 0
    result = await db.execute(base.order_by(Category.sort_order, Category.id).offset(offset).limit(limit))
    return list(result.scalars().all()), total


async def create_category(db: AsyncSession, name: str, slug: str, description: str | None = None, sort_order: int = 0) -> Category:
    category = Category(name=name, slug=slug, description=description, sort_order=sort_order)
    db.add(category)
    await db.flush()
    await db.refresh(category)
    return category


async def update_category(db: AsyncSession, category_id: int, name: str, slug: str, description: str | None = None, sort_order: int = 0) -> Category | None:
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    if not category:
        return None
    category.name = name
    category.slug = slug
    category.description = description
    category.sort_order = sort_order
    await db.flush()
    await db.refresh(category)
    return category


async def delete_category(db: AsyncSession, category_id: int) -> bool:
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    if not category:
        return False
    await db.delete(category)
    await db.flush()
    return True


async def get_tags(db: AsyncSession) -> list[Tag]:
    result = await db.execute(select(Tag).order_by(Tag.id))
    return list(result.scalars().all())


async def get_tags_page(db: AsyncSession, offset: int = 0, limit: int = 50):
    base = select(Tag)
    total = (await db.execute(select(func.count()).select_from(base.subquery()))).scalar() or 0
    result = await db.execute(base.order_by(Tag.id).offset(offset).limit(limit))
    return list(result.scalars().all()), total


async def create_tag(db: AsyncSession, name: str, slug: str) -> Tag:
    tag = Tag(name=name, slug=slug)
    db.add(tag)
    await db.flush()
    await db.refresh(tag)
    return tag


async def update_tag(db: AsyncSession, tag_id: int, name: str, slug: str) -> Tag | None:
    result = await db.execute(select(Tag).where(Tag.id == tag_id))
    tag = result.scalar_one_or_none()
    if not tag:
        return None
    tag.name = name
    tag.slug = slug
    await db.flush()
    await db.refresh(tag)
    return tag


async def delete_tag(db: AsyncSession, tag_id: int) -> bool:
    result = await db.execute(select(Tag).where(Tag.id == tag_id))
    tag = result.scalar_one_or_none()
    if not tag:
        return False
    await db.delete(tag)
    await db.flush()
    return True
