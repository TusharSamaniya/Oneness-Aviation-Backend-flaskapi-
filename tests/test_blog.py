"""Tests for blog, FAQ, and testimonials endpoints."""
import pytest


@pytest.mark.asyncio
async def test_list_blog_posts_empty(client):
    response = await client.get("/api/blog")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data


@pytest.mark.asyncio
async def test_blog_pagination(client):
    response = await client.get("/api/blog?page=1&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert data["limit"] == 5
    assert data["page"] == 1


@pytest.mark.asyncio
async def test_blog_category_filter(client):
    response = await client.get("/api/blog?category=Aviation+News")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_nonexistent_blog_post(client):
    response = await client.get("/api/blog/this-slug-does-not-exist")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_faqs(client):
    response = await client.get("/api/faq")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_list_testimonials(client):
    response = await client.get("/api/testimonials")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
