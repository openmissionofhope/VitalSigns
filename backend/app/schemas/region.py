"""
Region schemas for VitalSigns API.
"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class RegionBase(BaseModel):
    """Base region schema."""
    code: str = Field(..., description="Unique region code")
    name: str = Field(..., description="Region name")
    name_local: Optional[str] = Field(None, description="Local name")
    level: str = Field(..., description="Region level (country, province, district)")
    parent_code: Optional[str] = Field(None, description="Parent region code")
    latitude: float = Field(..., description="Center latitude")
    longitude: float = Field(..., description="Center longitude")


class RegionCreate(RegionBase):
    """Schema for creating a new region."""
    population: Optional[int] = None
    population_density: Optional[float] = None
    area_km2: Optional[float] = None
    iso_code: Optional[str] = None
    continent: Optional[str] = None
    timezone: Optional[str] = None
    monitoring_priority: int = 5
    bbox: Optional[List[float]] = None


class RegionResponse(BaseModel):
    """Region response schema."""
    id: int
    code: str
    name: str
    name_local: Optional[str] = None
    level: str
    parent_code: Optional[str] = None
    latitude: float
    longitude: float
    population: Optional[int] = None
    continent: Optional[str] = None
    iso_code: Optional[str] = None
    is_active: bool
    monitoring_priority: int

    # Current risk summary
    current_risk_level: Optional[str] = None
    current_vital_risk_index: Optional[float] = None

    class Config:
        from_attributes = True


class RegionListResponse(BaseModel):
    """Response for list of regions."""
    total: int
    regions: List[RegionResponse]


class RegionDetailResponse(RegionResponse):
    """Detailed region response with additional data."""
    area_km2: Optional[float] = None
    population_density: Optional[float] = None
    timezone: Optional[str] = None
    bbox: Optional[List[float]] = None
    created_at: datetime
    updated_at: datetime

    # Risk breakdown
    hunger_stress_index: Optional[float] = None
    health_system_strain_index: Optional[float] = None
    disease_outbreak_index: Optional[float] = None

    # Active alerts count
    active_alerts_count: int = 0

    class Config:
        from_attributes = True
