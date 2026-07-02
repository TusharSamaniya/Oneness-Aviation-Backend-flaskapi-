from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import Optional

from app.models.aircraft import Aircraft, AircraftCategory, AirportDistance
from app.schemas.fleet import AircraftCreate, AircraftUpdate, EstimateRequest, EstimateResponse, PriceBreakdown

# Cruise speeds per tier (km/h)
CRUISE_SPEEDS = {
    "turboprop":    480,
    "light-jet":    720,
    "midsize-jet":  820,
    "heavy-jet":    900,
    "ulr":          950,
    "helicopter":   240,
}

# Default price per hour per tier (INR) — used as fallback if no aircraft found
TIER_BASE_PRICE = {
    "turboprop":    180_000,
    "light-jet":    220_000,
    "midsize-jet":  380_000,
    "heavy-jet":    600_000,
    "ulr":          900_000,
}


async def list_aircraft(
    db: AsyncSession,
    category: Optional[str] = None,
    passengers_min: Optional[int] = None,
    available_only: bool = True,
) -> list[Aircraft]:
    q = select(Aircraft).where(Aircraft.is_active == True)  # noqa: E712
    if category:
        q = q.where(Aircraft.category == category)
    if passengers_min:
        q = q.where(Aircraft.passengers >= passengers_min)
    if available_only:
        q = q.where(Aircraft.is_available == True)  # noqa: E712
    result = await db.execute(q)
    return result.scalars().all()


async def get_aircraft_by_slug(db: AsyncSession, slug: str) -> Aircraft:
    result = await db.execute(
        select(Aircraft).where(and_(Aircraft.slug == slug, Aircraft.is_active == True))  # noqa: E712
    )
    aircraft = result.scalar_one_or_none()
    if not aircraft:
        raise HTTPException(status_code=404, detail=f"Aircraft '{slug}' not found")
    return aircraft


async def create_aircraft(db: AsyncSession, data: AircraftCreate) -> Aircraft:
    aircraft = Aircraft(**data.model_dump())
    db.add(aircraft)
    await db.flush()
    await db.refresh(aircraft)
    return aircraft


async def update_aircraft(db: AsyncSession, aircraft_id: int, data: AircraftUpdate) -> Aircraft:
    result = await db.execute(select(Aircraft).where(Aircraft.id == aircraft_id))
    aircraft = result.scalar_one_or_none()
    if not aircraft:
        raise HTTPException(status_code=404, detail="Aircraft not found")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(aircraft, field, value)
    db.add(aircraft)
    return aircraft


async def estimate_flight_cost(db: AsyncSession, req: EstimateRequest) -> EstimateResponse:
    # Lookup distance
    result = await db.execute(
        select(AirportDistance).where(
            and_(
                AirportDistance.from_code == req.from_code.upper(),
                AirportDistance.to_code == req.to_code.upper(),
            )
        )
    )
    route = result.scalar_one_or_none()
    if not route:
        raise HTTPException(
            status_code=404,
            detail=f"Route {req.from_code.upper()}–{req.to_code.upper()} not found. Please contact us for a custom quote.",
        )

    speed = CRUISE_SPEEDS.get(req.aircraft_tier, 700)
    flight_hours = route.distance_km / speed + 0.25  # +15 min for taxi/approach

    # Get price per hour from aircraft or use tier default
    result2 = await db.execute(
        select(Aircraft).where(
            and_(Aircraft.category == req.aircraft_tier, Aircraft.is_active == True)  # noqa: E712
        )
    )
    aircraft_list = result2.scalars().all()
    if aircraft_list:
        avg_price = sum(a.price_per_hour for a in aircraft_list) // len(aircraft_list)
    else:
        avg_price = TIER_BASE_PRICE.get(req.aircraft_tier, 300_000)

    base = int(flight_hours * avg_price)
    landing = 15_000
    handling = 8_000
    taxes = int(base * 0.05)
    total = base + landing + handling + taxes
    total_with_return = int(total * 1.85)

    return EstimateResponse(
        from_city=route.from_city,
        to_city=route.to_city,
        distance_km=route.distance_km,
        flight_time_hrs=round(flight_hours, 2),
        aircraft_tier=req.aircraft_tier,
        breakdown=PriceBreakdown(
            base=base,
            landing=landing,
            handling=handling,
            taxes=taxes,
            total=total,
            total_with_return=total_with_return if req.journey_type == "Round Trip" else None,
        ),
    )
