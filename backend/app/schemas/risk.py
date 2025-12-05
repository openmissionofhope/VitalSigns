"""
Risk schemas for VitalSigns API.
"""
from datetime import datetime
from typing import Dict, List, Optional, Any

from pydantic import BaseModel, Field


class DiseaseRiskResponse(BaseModel):
    """Disease-specific risk response."""
    disease_type: str
    risk_score: float = Field(..., ge=0, le=100)
    risk_level: str
    is_high_season: bool = False
    seasonal_baseline: Optional[float] = None
    deviation_from_seasonal: Optional[float] = None
    trend_direction: Optional[str] = None
    trend_velocity: Optional[float] = None
    confidence_score: float = Field(..., ge=0, le=1)
    calculation_date: datetime
    contributing_signals: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class RiskIndexResponse(BaseModel):
    """Composite risk index response."""
    region_id: int
    region_code: str
    region_name: str

    # Core indices
    hunger_stress_index: float = Field(..., ge=0, le=100)
    health_system_strain_index: float = Field(..., ge=0, le=100)
    disease_outbreak_index: float = Field(..., ge=0, le=100)

    # Composite
    vital_risk_index: float = Field(..., ge=0, le=100)
    risk_level: str

    # Quality
    confidence_score: float = Field(..., ge=0, le=1)
    data_completeness: float = Field(..., ge=0, le=1)

    # Context
    calculation_date: datetime
    valid_from: datetime
    valid_until: datetime
    model_version: str

    # Breakdown
    contributing_factors: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class RegionRisksResponse(BaseModel):
    """Full risk response for a region."""
    region_id: int
    region_code: str
    region_name: str

    # Overall risk
    composite_risk: RiskIndexResponse

    # Disease-specific risks
    disease_risks: List[DiseaseRiskResponse]

    # Historical trend (last 7 days)
    risk_trend: Optional[List[Dict[str, Any]]] = None

    class Config:
        from_attributes = True


class RiskSummaryResponse(BaseModel):
    """Summary of risks across multiple regions."""
    total_regions: int
    timestamp: datetime

    # Risk distribution
    critical_count: int = 0
    high_count: int = 0
    moderate_count: int = 0
    low_count: int = 0
    minimal_count: int = 0

    # Top risk regions
    top_risk_regions: List[Dict[str, Any]]

    # Disease hotspots
    disease_hotspots: Dict[str, List[Dict[str, Any]]]

    class Config:
        from_attributes = True


class GlobalRiskMapResponse(BaseModel):
    """Response for global risk map visualization."""
    timestamp: datetime
    regions: List[Dict[str, Any]]  # Simplified region data for map rendering

    class Config:
        from_attributes = True
