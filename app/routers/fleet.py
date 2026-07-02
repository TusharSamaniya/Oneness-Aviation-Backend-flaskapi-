from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional, List

from app.database import get_db
from app.models.aircraft import Aircraft, AircraftCategory
from app.schemas.fleet import AircraftResponse, EstimateRequest, EstimateResponse
from app.services import fleet_service

router = APIRouter(prefix="/fleet", tags=["Fleet"])


@router.get("", response_model=List[AircraftResponse])
async def list_fleet(
    category: Optional[str] = Query(None),
    passengers_min: Optional[int] = Query(None),
    available_only: bool = Query(True),
    db: AsyncSession = Depends(get_db),
):
    return await fleet_service.list_aircraft(db, category, passengers_min, available_only)


@router.get("/categories")
async def list_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AircraftCategory).order_by(AircraftCategory.sort_order))
    categories = result.scalars().all()

    # Attach aircraft count per category
    count_result = await db.execute(
        select(Aircraft.category, func.count(Aircraft.id))
        .where(Aircraft.is_active == True)  # noqa: E712
        .group_by(Aircraft.category)
    )
    counts = dict(count_result.all())

    return [
        {"id": c.slug, "label": c.label, "icon": c.icon, "count": counts.get(c.slug, 0)}
        for c in categories
    ]


@router.get("/{slug}", response_model=AircraftResponse)
async def get_aircraft(slug: str, db: AsyncSession = Depends(get_db)):
    return await fleet_service.get_aircraft_by_slug(db, slug)


@router.post("/estimate", response_model=EstimateResponse)
async def estimate_cost(req: EstimateRequest, db: AsyncSession = Depends(get_db)):
    return await fleet_service.estimate_flight_cost(db, req)
