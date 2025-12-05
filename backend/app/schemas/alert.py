"""
Alert schemas for VitalSigns API.
"""
from datetime import datetime
from typing import Dict, List, Optional, Any

from pydantic import BaseModel, Field


class AlertBase(BaseModel):
    """Base alert schema."""
    alert_type: str
    severity: str
    title: str
    description: Optional[str] = None
    risk_score: float = Field(..., ge=0, le=100)
    threshold_exceeded: float
    disease_type: Optional[str] = None


class AlertCreate(AlertBase):
    """Schema for creating a new alert."""
    region_id: int
    expires_at: Optional[datetime] = None
    contributing_factors: Optional[Dict[str, Any]] = None
    supporting_signals: Optional[Dict[str, Any]] = None
    confidence_score: float = 0.5


class AlertResponse(BaseModel):
    """Alert response schema."""
    id: int
    region_id: int
    region_code: str
    region_name: str

    alert_type: str
    severity: str
    status: str
    title: str
    description: Optional[str] = None

    risk_score: float
    threshold_exceeded: float
    disease_type: Optional[str] = None

    triggered_at: datetime
    expires_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None

    confidence_score: float
    contributing_factors: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class AlertListResponse(BaseModel):
    """Response for list of alerts."""
    total: int
    active_count: int
    alerts: List[AlertResponse]


class AlertAcknowledgeRequest(BaseModel):
    """Request to acknowledge an alert."""
    notes: Optional[str] = None


class AlertResolveRequest(BaseModel):
    """Request to resolve an alert."""
    resolution_notes: Optional[str] = None
    was_false_positive: bool = False
