"""
Alert endpoints for VitalSigns API.
"""
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.region import Region
from app.models.alert import Alert, AlertStatus, AlertSeverity, AlertType
from app.schemas.alert import (
    AlertResponse,
    AlertListResponse,
    AlertCreate,
    AlertAcknowledgeRequest,
    AlertResolveRequest,
)

router = APIRouter()


@router.get("/", response_model=AlertListResponse)
async def get_alerts(
    status: Optional[str] = Query(None, description="Filter by status"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    alert_type: Optional[str] = Query(None, description="Filter by type"),
    region_code: Optional[str] = Query(None, description="Filter by region"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """
    Get list of alerts with optional filtering.

    Returns:
        List of alerts and counts
    """
    # Build base query
    query = (
        select(Alert, Region)
        .join(Region, Alert.region_id == Region.id)
    )

    # Apply filters
    if status:
        try:
            status_enum = AlertStatus(status)
            query = query.where(Alert.status == status_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")

    if severity:
        try:
            severity_enum = AlertSeverity(severity)
            query = query.where(Alert.severity == severity_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid severity: {severity}")

    if alert_type:
        try:
            type_enum = AlertType(alert_type)
            query = query.where(Alert.alert_type == type_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid alert type: {alert_type}")

    if region_code:
        query = query.where(Region.code == region_code)

    # Get counts
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query) or 0

    active_count_query = (
        select(func.count())
        .select_from(Alert)
        .where(Alert.status == AlertStatus.ACTIVE)
    )
    active_count = await db.scalar(active_count_query) or 0

    # Get alerts with pagination
    query = query.order_by(
        Alert.severity.desc(),
        Alert.triggered_at.desc()
    ).offset(skip).limit(limit)

    result = await db.execute(query)
    rows = result.all()

    alert_responses = [
        AlertResponse(
            id=alert.id,
            region_id=alert.region_id,
            region_code=region.code,
            region_name=region.name,
            alert_type=alert.alert_type.value,
            severity=alert.severity.value,
            status=alert.status.value,
            title=alert.title,
            description=alert.description,
            risk_score=alert.risk_score,
            threshold_exceeded=alert.threshold_exceeded,
            disease_type=alert.disease_type,
            triggered_at=alert.triggered_at,
            expires_at=alert.expires_at,
            acknowledged_at=alert.acknowledged_at,
            resolved_at=alert.resolved_at,
            confidence_score=alert.confidence_score,
            contributing_factors=alert.contributing_factors,
        )
        for alert, region in rows
    ]

    return AlertListResponse(
        total=total,
        active_count=active_count,
        alerts=alert_responses,
    )


@router.get("/active", response_model=AlertListResponse)
async def get_active_alerts(
    severity: Optional[str] = Query(None, description="Filter by minimum severity"),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all currently active alerts.

    Returns:
        List of active alerts sorted by severity
    """
    query = (
        select(Alert, Region)
        .join(Region, Alert.region_id == Region.id)
        .where(Alert.status == AlertStatus.ACTIVE)
        .where(or_(Alert.expires_at.is_(None), Alert.expires_at > datetime.utcnow()))
    )

    if severity:
        severity_order = {
            "critical": [AlertSeverity.CRITICAL],
            "urgent": [AlertSeverity.CRITICAL, AlertSeverity.URGENT],
            "warning": [AlertSeverity.CRITICAL, AlertSeverity.URGENT, AlertSeverity.WARNING],
        }
        if severity in severity_order:
            query = query.where(Alert.severity.in_(severity_order[severity]))

    query = query.order_by(
        Alert.severity.desc(),
        Alert.risk_score.desc(),
    ).limit(limit)

    result = await db.execute(query)
    rows = result.all()

    alert_responses = [
        AlertResponse(
            id=alert.id,
            region_id=alert.region_id,
            region_code=region.code,
            region_name=region.name,
            alert_type=alert.alert_type.value,
            severity=alert.severity.value,
            status=alert.status.value,
            title=alert.title,
            description=alert.description,
            risk_score=alert.risk_score,
            threshold_exceeded=alert.threshold_exceeded,
            disease_type=alert.disease_type,
            triggered_at=alert.triggered_at,
            expires_at=alert.expires_at,
            acknowledged_at=alert.acknowledged_at,
            resolved_at=alert.resolved_at,
            confidence_score=alert.confidence_score,
            contributing_factors=alert.contributing_factors,
        )
        for alert, region in rows
    ]

    return AlertListResponse(
        total=len(alert_responses),
        active_count=len(alert_responses),
        alerts=alert_responses,
    )


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Get a specific alert by ID.

    Args:
        alert_id: Alert ID

    Returns:
        Alert details
    """
    query = (
        select(Alert, Region)
        .join(Region, Alert.region_id == Region.id)
        .where(Alert.id == alert_id)
    )
    result = await db.execute(query)
    row = result.first()

    if not row:
        raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")

    alert, region = row
    return AlertResponse(
        id=alert.id,
        region_id=alert.region_id,
        region_code=region.code,
        region_name=region.name,
        alert_type=alert.alert_type.value,
        severity=alert.severity.value,
        status=alert.status.value,
        title=alert.title,
        description=alert.description,
        risk_score=alert.risk_score,
        threshold_exceeded=alert.threshold_exceeded,
        disease_type=alert.disease_type,
        triggered_at=alert.triggered_at,
        expires_at=alert.expires_at,
        acknowledged_at=alert.acknowledged_at,
        resolved_at=alert.resolved_at,
        confidence_score=alert.confidence_score,
        contributing_factors=alert.contributing_factors,
    )


@router.post("/{alert_id}/acknowledge", response_model=AlertResponse)
async def acknowledge_alert(
    alert_id: int,
    request: AlertAcknowledgeRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Acknowledge an alert.

    Args:
        alert_id: Alert ID
        request: Acknowledgement details

    Returns:
        Updated alert
    """
    query = select(Alert).where(Alert.id == alert_id)
    result = await db.execute(query)
    alert = result.scalar_one_or_none()

    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")

    if alert.status != AlertStatus.ACTIVE:
        raise HTTPException(
            status_code=400,
            detail=f"Alert {alert_id} is not active"
        )

    alert.status = AlertStatus.ACKNOWLEDGED
    alert.acknowledged_at = datetime.utcnow()
    if request.notes:
        alert.notes = request.notes

    await db.commit()
    await db.refresh(alert)

    # Get region for response
    region_query = select(Region).where(Region.id == alert.region_id)
    region_result = await db.execute(region_query)
    region = region_result.scalar_one()

    return AlertResponse(
        id=alert.id,
        region_id=alert.region_id,
        region_code=region.code,
        region_name=region.name,
        alert_type=alert.alert_type.value,
        severity=alert.severity.value,
        status=alert.status.value,
        title=alert.title,
        description=alert.description,
        risk_score=alert.risk_score,
        threshold_exceeded=alert.threshold_exceeded,
        disease_type=alert.disease_type,
        triggered_at=alert.triggered_at,
        expires_at=alert.expires_at,
        acknowledged_at=alert.acknowledged_at,
        resolved_at=alert.resolved_at,
        confidence_score=alert.confidence_score,
        contributing_factors=alert.contributing_factors,
    )


@router.post("/{alert_id}/resolve", response_model=AlertResponse)
async def resolve_alert(
    alert_id: int,
    request: AlertResolveRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Resolve an alert.

    Args:
        alert_id: Alert ID
        request: Resolution details

    Returns:
        Updated alert
    """
    query = select(Alert).where(Alert.id == alert_id)
    result = await db.execute(query)
    alert = result.scalar_one_or_none()

    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")

    if alert.status == AlertStatus.RESOLVED:
        raise HTTPException(
            status_code=400,
            detail=f"Alert {alert_id} is already resolved"
        )

    if request.was_false_positive:
        alert.status = AlertStatus.FALSE_POSITIVE
    else:
        alert.status = AlertStatus.RESOLVED

    alert.resolved_at = datetime.utcnow()
    if request.resolution_notes:
        alert.resolution_notes = request.resolution_notes

    await db.commit()
    await db.refresh(alert)

    # Get region for response
    region_query = select(Region).where(Region.id == alert.region_id)
    region_result = await db.execute(region_query)
    region = region_result.scalar_one()

    return AlertResponse(
        id=alert.id,
        region_id=alert.region_id,
        region_code=region.code,
        region_name=region.name,
        alert_type=alert.alert_type.value,
        severity=alert.severity.value,
        status=alert.status.value,
        title=alert.title,
        description=alert.description,
        risk_score=alert.risk_score,
        threshold_exceeded=alert.threshold_exceeded,
        disease_type=alert.disease_type,
        triggered_at=alert.triggered_at,
        expires_at=alert.expires_at,
        acknowledged_at=alert.acknowledged_at,
        resolved_at=alert.resolved_at,
        confidence_score=alert.confidence_score,
        contributing_factors=alert.contributing_factors,
    )
