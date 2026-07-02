from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class BlogPostResponse(BaseModel):
    id: int
    slug: str
    title: str
    excerpt: str
    category: str
    tag: Optional[str]
    author: str
    image_url: Optional[str]
    read_time: Optional[str]
    is_published: bool
    views: int
    published_at: Optional[datetime]

    class Config:
        from_attributes = True


class BlogPostDetail(BlogPostResponse):
    content: Optional[str]


class BlogPostCreate(BaseModel):
    slug: str
    title: str
    excerpt: str
    content: Optional[str] = None
    category: str
    tag: Optional[str] = None
    author: str = "Oneness Aviation Team"
    image_url: Optional[str] = None
    read_time: Optional[str] = None


class BlogPostUpdate(BaseModel):
    title: Optional[str] = None
    excerpt: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    tag: Optional[str] = None
    image_url: Optional[str] = None
    read_time: Optional[str] = None


class FAQResponse(BaseModel):
    id: int
    question: str
    answer: str
    category: str

    class Config:
        from_attributes = True


class TestimonialResponse(BaseModel):
    id: int
    name: str
    role: str
    company: Optional[str]
    quote: str
    rating: int
    plan: Optional[str]
    initials: Optional[str]
    avatar_url: Optional[str]

    class Config:
        from_attributes = True


class PaginatedResponse(BaseModel):
    items: List[BlogPostResponse]
    total: int
    page: int
    limit: int
    pages: int
