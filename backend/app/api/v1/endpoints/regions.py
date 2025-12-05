"""
Region endpoints for VitalSigns API.
"""
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.database import get_db
from app.models.region import Region
from app.models.risk import RiskIndex, RiskLevel
from app.models.alert import Alert, AlertStatus
from app.schemas.region import (
    RegionResponse,
    RegionListResponse,
    RegionDetailResponse,
    RegionCreate,
)

router = APIRouter()


@router.get("/", response_model=RegionListResponse)
async def get_regions(
    level: Optional[str] = Query(None, description="Filter by region level"),
    continent: Optional[str] = Query(None, description="Filter by continent"),
    parent_code: Optional[str] = Query(None, description="Filter by parent region"),
    is_active: bool = Query(True, description="Filter by active status"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum records to return"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get list of regions with optional filtering.

    Returns:
        List of regions with basic risk information
    """
    # Build query
    query = select(Region).where(Region.is_active == is_active)

    if level:
        query = query.where(Region.level == level)
    if continent:
        query = query.where(Region.continent == continent)
    if parent_code:
        query = query.where(Region.parent_code == parent_code)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    # Get regions with pagination
    query = query.order_by(Region.name).offset(skip).limit(limit)
    result = await db.execute(query)
    regions = result.scalars().all()

    # Get latest risk indices for regions
    region_ids = [r.id for r in regions]
    if region_ids:
        risk_query = (
            select(RiskIndex)
            .where(RiskIndex.region_id.in_(region_ids))
            .order_by(RiskIndex.region_id, RiskIndex.calculation_date.desc())
            .distinct(RiskIndex.region_id)
        )
        risk_result = await db.execute(risk_query)
        risks = {r.region_id: r for r in risk_result.scalars().all()}
    else:
        risks = {}

    # Build response
    region_responses = []
    for region in regions:
        risk = risks.get(region.id)
        region_responses.append(
            RegionResponse(
                id=region.id,
                code=region.code,
                name=region.name,
                name_local=region.name_local,
                level=region.level,
                parent_code=region.parent_code,
                latitude=region.latitude,
                longitude=region.longitude,
                population=region.population,
                continent=region.continent,
                iso_code=region.iso_code,
                is_active=region.is_active,
                monitoring_priority=region.monitoring_priority,
                current_risk_level=risk.risk_level.value if risk else None,
                current_vital_risk_index=risk.vital_risk_index if risk else None,
            )
        )

    return RegionListResponse(total=total or 0, regions=region_responses)


@router.get("/{region_code}", response_model=RegionDetailResponse)
async def get_region(
    region_code: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Get detailed information for a specific region.

    Args:
        region_code: Unique region code

    Returns:
        Detailed region information including risk breakdown
    """
    # Get region
    query = select(Region).where(Region.code == region_code)
    result = await db.execute(query)
    region = result.scalar_one_or_none()

    if not region:
        raise HTTPException(status_code=404, detail=f"Region '{region_code}' not found")

    # Get latest risk index
    risk_query = (
        select(RiskIndex)
        .where(RiskIndex.region_id == region.id)
        .order_by(RiskIndex.calculation_date.desc())
        .limit(1)
    )
    risk_result = await db.execute(risk_query)
    risk = risk_result.scalar_one_or_none()

    # Get active alerts count
    alerts_query = (
        select(func.count())
        .select_from(Alert)
        .where(Alert.region_id == region.id)
        .where(Alert.status == AlertStatus.ACTIVE)
    )
    active_alerts = await db.scalar(alerts_query) or 0

    return RegionDetailResponse(
        id=region.id,
        code=region.code,
        name=region.name,
        name_local=region.name_local,
        level=region.level,
        parent_code=region.parent_code,
        latitude=region.latitude,
        longitude=region.longitude,
        population=region.population,
        population_density=region.population_density,
        area_km2=region.area_km2,
        continent=region.continent,
        iso_code=region.iso_code,
        timezone=region.timezone,
        bbox=region.bbox,
        is_active=region.is_active,
        monitoring_priority=region.monitoring_priority,
        created_at=region.created_at,
        updated_at=region.updated_at,
        current_risk_level=risk.risk_level.value if risk else None,
        current_vital_risk_index=risk.vital_risk_index if risk else None,
        hunger_stress_index=risk.hunger_stress_index if risk else None,
        health_system_strain_index=risk.health_system_strain_index if risk else None,
        disease_outbreak_index=risk.disease_outbreak_index if risk else None,
        active_alerts_count=active_alerts,
    )


@router.get("/{region_code}/children", response_model=RegionListResponse)
async def get_region_children(
    region_code: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Get child regions of a parent region.

    Args:
        region_code: Parent region code

    Returns:
        List of child regions
    """
    query = select(Region).where(
        Region.parent_code == region_code,
        Region.is_active == True,
    ).order_by(Region.name)

    result = await db.execute(query)
    regions = result.scalars().all()

    region_responses = [
        RegionResponse(
            id=r.id,
            code=r.code,
            name=r.name,
            name_local=r.name_local,
            level=r.level,
            parent_code=r.parent_code,
            latitude=r.latitude,
            longitude=r.longitude,
            population=r.population,
            continent=r.continent,
            iso_code=r.iso_code,
            is_active=r.is_active,
            monitoring_priority=r.monitoring_priority,
        )
        for r in regions
    ]

    return RegionListResponse(total=len(region_responses), regions=region_responses)


@router.post("/", response_model=RegionResponse, status_code=201)
async def create_region(
    region: RegionCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new region.

    Args:
        region: Region data

    Returns:
        Created region
    """
    # Check if region code already exists
    existing_query = select(Region).where(Region.code == region.code)
    existing = await db.execute(existing_query)
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail=f"Region with code '{region.code}' already exists"
        )

    # Create region
    db_region = Region(
        code=region.code,
        name=region.name,
        name_local=region.name_local,
        level=region.level,
        parent_code=region.parent_code,
        latitude=region.latitude,
        longitude=region.longitude,
        population=region.population,
        population_density=region.population_density,
        area_km2=region.area_km2,
        iso_code=region.iso_code,
        continent=region.continent,
        timezone=region.timezone,
        bbox=region.bbox,
        monitoring_priority=region.monitoring_priority,
    )

    db.add(db_region)
    await db.commit()
    await db.refresh(db_region)

    return RegionResponse(
        id=db_region.id,
        code=db_region.code,
        name=db_region.name,
        name_local=db_region.name_local,
        level=db_region.level,
        parent_code=db_region.parent_code,
        latitude=db_region.latitude,
        longitude=db_region.longitude,
        population=db_region.population,
        continent=db_region.continent,
        iso_code=db_region.iso_code,
        is_active=db_region.is_active,
        monitoring_priority=db_region.monitoring_priority,
    )
