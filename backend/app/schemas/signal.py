"""
Signal schemas for VitalSigns API.
"""
from datetime import datetime
from typing import Dict, List, Optional, Any

from pydantic import BaseModel, Field


class SignalBase(BaseModel):
    """Base signal schema."""
    signal_type: str
    indicator_name: str
    value: float
    unit: Optional[str] = None
    observation_date: datetime


class SignalCreate(SignalBase):
    """Schema for creating a new signal."""
    source_id: int
    region_id: int
    reporting_date: datetime
    confidence: float = Field(1.0, ge=0, le=1)
    raw_data: Optional[Dict[str, Any]] = None
    processing_notes: Optional[str] = None


class SignalResponse(BaseModel):
    """Signal response schema."""
    id: int
    source_id: int
    source_name: str
    region_id: int
    region_code: str

    signal_type: str
    indicator_name: str
    value: float
    unit: Optional[str] = None

    confidence: float
    is_anomaly: bool
    quality_score: float

    observation_date: datetime
    reporting_date: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class SignalAggregationResponse(BaseModel):
    """Signal aggregation response schema."""
    region_id: int
    region_code: str
    signal_type: str
    indicator_name: str

    period_type: str
    period_start: datetime
    period_end: datetime

    value_mean: float
    value_median: Optional[float] = None
    value_min: Optional[float] = None
    value_max: Optional[float] = None
    value_std: Optional[float] = None
    sample_count: int

    baseline_value: Optional[float] = None
    deviation_from_baseline: Optional[float] = None
    z_score: Optional[float] = None

    class Config:
        from_attributes = True


class SignalTimeSeriesResponse(BaseModel):
    """Time series of signals for visualization."""
    region_id: int
    region_code: str
    signal_type: str
    indicator_name: str
    unit: Optional[str] = None

    data_points: List[Dict[str, Any]]  # [{date, value, confidence}, ...]

    # Statistics
    mean: Optional[float] = None
    std: Optional[float] = None
    trend: Optional[str] = None


class SignalTypeSummary(BaseModel):
    """Summary of available signal types."""
    signal_type: str
    indicator_count: int
    latest_observation: Optional[datetime] = None
    coverage_regions: int
