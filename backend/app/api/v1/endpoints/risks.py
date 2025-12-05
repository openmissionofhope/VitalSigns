"""
Risk endpoints for VitalSigns API.
"""
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.region import Region
from app.models.risk import RiskIndex, DiseaseRisk, RiskLevel, DiseaseType
from app.schemas.risk import (
    RiskIndexResponse,
    DiseaseRiskResponse,
    RegionRisksResponse,
    RiskSummaryResponse,
    GlobalRiskMapResponse,
)

router = APIRouter()


@router.get("/summary", response_model=RiskSummaryResponse)
async def get_risk_summary(
    continent: Optional[str] = Query(None, description="Filter by continent"),
    level: str = Query("country", description="Region level to summarize"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get summary of risks across all regions.

    Returns:
        Risk distribution and top risk regions
    """
    # Get regions
    region_query = select(Region).where(
        Region.is_active == True,
        Region.level == level,
    )
    if continent:
        region_query = region_query.where(Region.continent == continent)

    region_result = await db.execute(region_query)
    regions = {r.id: r for r in region_result.scalars().all()}

    if not regions:
        return RiskSummaryResponse(
            total_regions=0,
            timestamp=datetime.utcnow(),
            top_risk_regions=[],
            disease_hotspots={},
        )

    # Get latest risk indices
    risk_query = (
        select(RiskIndex)
        .where(RiskIndex.region_id.in_(regions.keys()))
        .order_by(RiskIndex.region_id, RiskIndex.calculation_date.desc())
        .distinct(RiskIndex.region_id)
    )
    risk_result = await db.execute(risk_query)
    risks = list(risk_result.scalars().all())

    # Count by risk level
    level_counts = {
        "critical": 0,
        "high": 0,
        "moderate": 0,
        "low": 0,
        "minimal": 0,
    }
    for risk in risks:
        level_counts[risk.risk_level.value] += 1

    # Get top risk regions
    sorted_risks = sorted(risks, key=lambda r: r.vital_risk_index, reverse=True)[:10]
    top_regions = [
        {
            "region_code": regions[r.region_id].code,
            "region_name": regions[r.region_id].name,
            "vital_risk_index": r.vital_risk_index,
            "risk_level": r.risk_level.value,
        }
        for r in sorted_risks
    ]

    # Get disease hotspots
    disease_hotspots: Dict[str, List[Dict[str, Any]]] = {}
    for disease in DiseaseType:
        disease_query = (
            select(DiseaseRisk)
            .where(
                DiseaseRisk.region_id.in_(regions.keys()),
                DiseaseRisk.disease_type == disease,
                DiseaseRisk.risk_level.in_([RiskLevel.HIGH, RiskLevel.CRITICAL]),
            )
            .order_by(DiseaseRisk.risk_score.desc())
            .limit(5)
        )
        disease_result = await db.execute(disease_query)
        disease_risks = disease_result.scalars().all()

        if disease_risks:
            disease_hotspots[disease.value] = [
                {
                    "region_code": regions[dr.region_id].code,
                    "region_name": regions[dr.region_id].name,
                    "risk_score": dr.risk_score,
                    "risk_level": dr.risk_level.value,
                }
                for dr in disease_risks
            ]

    return RiskSummaryResponse(
        total_regions=len(regions),
        timestamp=datetime.utcnow(),
        critical_count=level_counts["critical"],
        high_count=level_counts["high"],
        moderate_count=level_counts["moderate"],
        low_count=level_counts["low"],
        minimal_count=level_counts["minimal"],
        top_risk_regions=top_regions,
        disease_hotspots=disease_hotspots,
    )


@router.get("/map", response_model=GlobalRiskMapResponse)
async def get_risk_map(
    level: str = Query("country", description="Region level for map"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get risk data formatted for global map visualization.

    Returns:
        Simplified region data with coordinates and risk scores
    """
    # Get regions
    region_query = select(Region).where(
        Region.is_active == True,
        Region.level == level,
    )
    region_result = await db.execute(region_query)
    regions = {r.id: r for r in region_result.scalars().all()}

    # Get latest risks
    risk_query = (
        select(RiskIndex)
        .where(RiskIndex.region_id.in_(regions.keys()))
        .order_by(RiskIndex.region_id, RiskIndex.calculation_date.desc())
        .distinct(RiskIndex.region_id)
    )
    risk_result = await db.execute(risk_query)
    risks = {r.region_id: r for r in risk_result.scalars().all()}

    # Build map data
    map_regions = []
    for region_id, region in regions.items():
        risk = risks.get(region_id)
        map_regions.append({
            "code": region.code,
            "name": region.name,
            "lat": region.latitude,
            "lng": region.longitude,
            "iso_code": region.iso_code,
            "vital_risk_index": risk.vital_risk_index if risk else 0,
            "risk_level": risk.risk_level.value if risk else "minimal",
            "hunger_stress": risk.hunger_stress_index if risk else 0,
            "health_strain": risk.health_system_strain_index if risk else 0,
            "disease_outbreak": risk.disease_outbreak_index if risk else 0,
        })

    return GlobalRiskMapResponse(
        timestamp=datetime.utcnow(),
        regions=map_regions,
    )


@router.get("/regions/{region_code}", response_model=RegionRisksResponse)
async def get_region_risks(
    region_code: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Get full risk breakdown for a specific region.

    Args:
        region_code: Region code

    Returns:
        Complete risk information including disease-specific risks
    """
    # Get region
    region_query = select(Region).where(Region.code == region_code)
    region_result = await db.execute(region_query)
    region = region_result.scalar_one_or_none()

    if not region:
        raise HTTPException(status_code=404, detail=f"Region '{region_code}' not found")

    # Get latest composite risk
    risk_query = (
        select(RiskIndex)
        .where(RiskIndex.region_id == region.id)
        .order_by(RiskIndex.calculation_date.desc())
        .limit(1)
    )
    risk_result = await db.execute(risk_query)
    risk = risk_result.scalar_one_or_none()

    if not risk:
        raise HTTPException(
            status_code=404,
            detail=f"No risk data available for region '{region_code}'"
        )

    # Get disease-specific risks
    disease_query = (
        select(DiseaseRisk)
        .where(DiseaseRisk.region_id == region.id)
        .order_by(DiseaseRisk.disease_type, DiseaseRisk.calculation_date.desc())
        .distinct(DiseaseRisk.disease_type)
    )
    disease_result = await db.execute(disease_query)
    disease_risks = disease_result.scalars().all()

    # Get 7-day trend
    trend_start = datetime.utcnow() - timedelta(days=7)
    trend_query = (
        select(RiskIndex)
        .where(
            RiskIndex.region_id == region.id,
            RiskIndex.calculation_date >= trend_start,
        )
        .order_by(RiskIndex.calculation_date)
    )
    trend_result = await db.execute(trend_query)
    trend_data = [
        {
            "date": r.calculation_date.isoformat(),
            "vital_risk_index": r.vital_risk_index,
            "risk_level": r.risk_level.value,
        }
        for r in trend_result.scalars().all()
    ]

    # Build response
    composite_response = RiskIndexResponse(
        region_id=region.id,
        region_code=region.code,
        region_name=region.name,
        hunger_stress_index=risk.hunger_stress_index,
        health_system_strain_index=risk.health_system_strain_index,
        disease_outbreak_index=risk.disease_outbreak_index,
        vital_risk_index=risk.vital_risk_index,
        risk_level=risk.risk_level.value,
        confidence_score=risk.confidence_score,
        data_completeness=risk.data_completeness,
        calculation_date=risk.calculation_date,
        valid_from=risk.valid_from,
        valid_until=risk.valid_until,
        model_version=risk.model_version,
        contributing_factors=risk.contributing_factors,
    )

    disease_responses = [
        DiseaseRiskResponse(
            disease_type=dr.disease_type.value,
            risk_score=dr.risk_score,
            risk_level=dr.risk_level.value,
            is_high_season=bool(dr.is_high_season),
            seasonal_baseline=dr.seasonal_baseline,
            deviation_from_seasonal=dr.deviation_from_seasonal,
            trend_direction=dr.trend_direction,
            trend_velocity=dr.trend_velocity,
            confidence_score=dr.confidence_score,
            calculation_date=dr.calculation_date,
            contributing_signals=dr.contributing_signals,
        )
        for dr in disease_risks
    ]

    return RegionRisksResponse(
        region_id=region.id,
        region_code=region.code,
        region_name=region.name,
        composite_risk=composite_response,
        disease_risks=disease_responses,
        risk_trend=trend_data,
    )


@router.get("/diseases/{disease_type}", response_model=List[DiseaseRiskResponse])
async def get_disease_risks(
    disease_type: str,
    risk_level: Optional[str] = Query(None, description="Filter by risk level"),
    limit: int = Query(50, ge=1, le=200, description="Maximum results"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get regions with high risk for a specific disease.

    Args:
        disease_type: Type of disease
        risk_level: Optional filter by risk level

    Returns:
        List of disease risk assessments across regions
    """
    # Validate disease type
    try:
        disease_enum = DiseaseType(disease_type)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid disease type: {disease_type}"
        )

    # Build query
    query = (
        select(DiseaseRisk, Region)
        .join(Region, DiseaseRisk.region_id == Region.id)
        .where(DiseaseRisk.disease_type == disease_enum)
        .order_by(DiseaseRisk.region_id, DiseaseRisk.calculation_date.desc())
        .distinct(DiseaseRisk.region_id)
    )

    if risk_level:
        try:
            level_enum = RiskLevel(risk_level)
            query = query.where(DiseaseRisk.risk_level == level_enum)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid risk level: {risk_level}"
            )

    query = query.order_by(DiseaseRisk.risk_score.desc()).limit(limit)
    result = await db.execute(query)
    rows = result.all()

    return [
        DiseaseRiskResponse(
            disease_type=dr.disease_type.value,
            risk_score=dr.risk_score,
            risk_level=dr.risk_level.value,
            is_high_season=bool(dr.is_high_season),
            seasonal_baseline=dr.seasonal_baseline,
            deviation_from_seasonal=dr.deviation_from_seasonal,
            trend_direction=dr.trend_direction,
            trend_velocity=dr.trend_velocity,
            confidence_score=dr.confidence_score,
            calculation_date=dr.calculation_date,
            contributing_signals=dr.contributing_signals,
        )
        for dr, region in rows
    ]
