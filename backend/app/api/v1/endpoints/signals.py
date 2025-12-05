"""
Signal endpoints for VitalSigns API.
"""
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.region import Region
from app.models.signal import Signal, SignalAggregation, SignalType
from app.models.source import DataSource
from app.schemas.signal import (
    SignalResponse,
    SignalAggregationResponse,
    SignalTimeSeriesResponse,
    SignalTypeSummary,
)

router = APIRouter()


@router.get("/types", response_model=List[SignalTypeSummary])
async def get_signal_types(
    db: AsyncSession = Depends(get_db),
):
    """
    Get summary of available signal types.

    Returns:
        List of signal types with metadata
    """
    summaries = []
    for signal_type in SignalType:
        # Count indicators and coverage
        indicator_query = (
            select(func.count(func.distinct(Signal.indicator_name)))
            .where(Signal.signal_type == signal_type)
        )
        indicator_count = await db.scalar(indicator_query) or 0

        coverage_query = (
            select(func.count(func.distinct(Signal.region_id)))
            .where(Signal.signal_type == signal_type)
        )
        coverage = await db.scalar(coverage_query) or 0

        latest_query = (
            select(func.max(Signal.observation_date))
            .where(Signal.signal_type == signal_type)
        )
        latest = await db.scalar(latest_query)

        summaries.append(SignalTypeSummary(
            signal_type=signal_type.value,
            indicator_count=indicator_count,
            latest_observation=latest,
            coverage_regions=coverage,
        ))

    return summaries


@router.get("/regions/{region_code}", response_model=List[SignalResponse])
async def get_region_signals(
    region_code: str,
    signal_type: Optional[str] = Query(None, description="Filter by signal type"),
    indicator: Optional[str] = Query(None, description="Filter by indicator name"),
    days: int = Query(30, ge=1, le=365, description="Days of history"),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
):
    """
    Get signals for a specific region.

    Args:
        region_code: Region code
        signal_type: Optional filter by signal type
        indicator: Optional filter by indicator name
        days: Number of days of history

    Returns:
        List of signals for the region
    """
    # Get region
    region_query = select(Region).where(Region.code == region_code)
    region_result = await db.execute(region_query)
    region = region_result.scalar_one_or_none()

    if not region:
        raise HTTPException(status_code=404, detail=f"Region '{region_code}' not found")

    # Build query
    start_date = datetime.utcnow() - timedelta(days=days)
    query = (
        select(Signal, DataSource)
        .join(DataSource, Signal.source_id == DataSource.id)
        .where(Signal.region_id == region.id)
        .where(Signal.observation_date >= start_date)
    )

    if signal_type:
        try:
            type_enum = SignalType(signal_type)
            query = query.where(Signal.signal_type == type_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid signal type: {signal_type}")

    if indicator:
        query = query.where(Signal.indicator_name.ilike(f"%{indicator}%"))

    query = query.order_by(Signal.observation_date.desc()).limit(limit)

    result = await db.execute(query)
    rows = result.all()

    return [
        SignalResponse(
            id=signal.id,
            source_id=signal.source_id,
            source_name=source.name,
            region_id=signal.region_id,
            region_code=region.code,
            signal_type=signal.signal_type.value,
            indicator_name=signal.indicator_name,
            value=signal.value,
            unit=signal.unit,
            confidence=signal.confidence,
            is_anomaly=signal.is_anomaly,
            quality_score=signal.quality_score,
            observation_date=signal.observation_date,
            reporting_date=signal.reporting_date,
            created_at=signal.created_at,
        )
        for signal, source in rows
    ]


@router.get("/regions/{region_code}/timeseries", response_model=SignalTimeSeriesResponse)
async def get_signal_timeseries(
    region_code: str,
    signal_type: str = Query(..., description="Signal type"),
    indicator: str = Query(..., description="Indicator name"),
    days: int = Query(90, ge=7, le=365, description="Days of history"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get time series data for a specific signal indicator.

    Args:
        region_code: Region code
        signal_type: Signal type
        indicator: Indicator name
        days: Number of days of history

    Returns:
        Time series data for visualization
    """
    # Get region
    region_query = select(Region).where(Region.code == region_code)
    region_result = await db.execute(region_query)
    region = region_result.scalar_one_or_none()

    if not region:
        raise HTTPException(status_code=404, detail=f"Region '{region_code}' not found")

    # Validate signal type
    try:
        type_enum = SignalType(signal_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid signal type: {signal_type}")

    # Get time series data
    start_date = datetime.utcnow() - timedelta(days=days)
    query = (
        select(Signal)
        .where(Signal.region_id == region.id)
        .where(Signal.signal_type == type_enum)
        .where(Signal.indicator_name == indicator)
        .where(Signal.observation_date >= start_date)
        .order_by(Signal.observation_date)
    )

    result = await db.execute(query)
    signals = result.scalars().all()

    if not signals:
        raise HTTPException(
            status_code=404,
            detail=f"No data found for indicator '{indicator}' in region '{region_code}'"
        )

    # Build data points
    data_points = [
        {
            "date": s.observation_date.isoformat(),
            "value": s.value,
            "confidence": s.confidence,
            "is_anomaly": s.is_anomaly,
        }
        for s in signals
    ]

    # Calculate statistics
    values = [s.value for s in signals]
    mean_val = sum(values) / len(values) if values else None
    std_val = None
    if len(values) > 1:
        variance = sum((x - mean_val) ** 2 for x in values) / len(values)
        std_val = variance ** 0.5

    # Determine trend (simple linear comparison)
    trend = None
    if len(values) >= 7:
        first_week = sum(values[:7]) / 7
        last_week = sum(values[-7:]) / 7
        if last_week > first_week * 1.1:
            trend = "increasing"
        elif last_week < first_week * 0.9:
            trend = "decreasing"
        else:
            trend = "stable"

    return SignalTimeSeriesResponse(
        region_id=region.id,
        region_code=region.code,
        signal_type=signal_type,
        indicator_name=indicator,
        unit=signals[0].unit if signals else None,
        data_points=data_points,
        mean=mean_val,
        std=std_val,
        trend=trend,
    )


@router.get("/aggregations/{region_code}", response_model=List[SignalAggregationResponse])
async def get_signal_aggregations(
    region_code: str,
    period_type: str = Query("daily", description="Aggregation period: daily, weekly, monthly"),
    signal_type: Optional[str] = Query(None, description="Filter by signal type"),
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
):
    """
    Get aggregated signal data for a region.

    Args:
        region_code: Region code
        period_type: Aggregation period
        signal_type: Optional filter
        days: History length

    Returns:
        List of signal aggregations
    """
    # Get region
    region_query = select(Region).where(Region.code == region_code)
    region_result = await db.execute(region_query)
    region = region_result.scalar_one_or_none()

    if not region:
        raise HTTPException(status_code=404, detail=f"Region '{region_code}' not found")

    # Build query
    start_date = datetime.utcnow() - timedelta(days=days)
    query = (
        select(SignalAggregation)
        .where(SignalAggregation.region_id == region.id)
        .where(SignalAggregation.period_type == period_type)
        .where(SignalAggregation.period_start >= start_date)
    )

    if signal_type:
        try:
            type_enum = SignalType(signal_type)
            query = query.where(SignalAggregation.signal_type == type_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid signal type: {signal_type}")

    query = query.order_by(SignalAggregation.period_start.desc())
    result = await db.execute(query)
    aggregations = result.scalars().all()

    return [
        SignalAggregationResponse(
            region_id=agg.region_id,
            region_code=region.code,
            signal_type=agg.signal_type.value,
            indicator_name=agg.indicator_name,
            period_type=agg.period_type,
            period_start=agg.period_start,
            period_end=agg.period_end,
            value_mean=agg.value_mean,
            value_median=agg.value_median,
            value_min=agg.value_min,
            value_max=agg.value_max,
            value_std=agg.value_std,
            sample_count=agg.sample_count,
            baseline_value=agg.baseline_value,
            deviation_from_baseline=agg.deviation_from_baseline,
            z_score=agg.z_score,
        )
        for agg in aggregations
    ]
