from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional

from app.database import get_db
from app.models.blog import BlogPost, FAQ, Testimonial
from app.schemas.blog import (
    BlogPostResponse, BlogPostDetail, PaginatedResponse,
    FAQResponse, TestimonialResponse,
)

router = APIRouter(prefix="/blog", tags=["Blog & Resources"])


@router.get("", response_model=PaginatedResponse)
async def list_posts(
    category: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(6, ge=1, le=30),
    db: AsyncSession = Depends(get_db),
):
    q = select(BlogPost).where(BlogPost.is_published == True)  # noqa: E712
    if category:
        q = q.where(BlogPost.category == category)
    if tag:
        q = q.where(BlogPost.tag == tag)

    total_result = await db.execute(select(func.count()).select_from(q.subquery()))
    total = total_result.scalar_one()

    q = q.order_by(BlogPost.published_at.desc()).offset((page - 1) * limit).limit(limit)
    result = await db.execute(q)
    posts = result.scalars().all()

    return PaginatedResponse(
        items=posts,
        total=total,
        page=page,
        limit=limit,
        pages=-(-total // limit),  # ceiling division
    )


@router.get("/categories")
async def list_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(BlogPost.category, func.count(BlogPost.id))
        .where(BlogPost.is_published == True)  # noqa: E712
        .group_by(BlogPost.category)
    )
    return [{"category": row[0], "count": row[1]} for row in result.all()]


@router.get("/{slug}", response_model=BlogPostDetail)
async def get_post(slug: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(BlogPost).where(BlogPost.slug == slug, BlogPost.is_published == True)  # noqa: E712
    )
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Blog post not found")
    # Increment view count
    post.views += 1
    db.add(post)
    return post


# ── FAQ ──────────────────────────────────────────────────────────────────────
faq_router = APIRouter(prefix="/faq", tags=["FAQ"])


@faq_router.get("", response_model=List[FAQResponse])
async def list_faqs(
    category: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    q = select(FAQ).where(FAQ.is_active == True).order_by(FAQ.sort_order)  # noqa: E712
    if category:
        q = q.where(FAQ.category == category)
    result = await db.execute(q)
    return result.scalars().all()


# ── Testimonials ─────────────────────────────────────────────────────────────
testimonial_router = APIRouter(prefix="/testimonials", tags=["Testimonials"])


@testimonial_router.get("", response_model=List[TestimonialResponse])
async def list_testimonials(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Testimonial).where(Testimonial.is_active == True).order_by(Testimonial.sort_order)  # noqa: E712
    )
    return result.scalars().all()
