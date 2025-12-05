"""
VitalSigns API Schemas (Pydantic models)
"""
from app.schemas.region import (
    RegionBase,
    RegionCreate,
    RegionResponse,
    RegionListResponse,
    RegionDetailResponse,
)
from app.schemas.risk import (
    RiskIndexResponse,
    DiseaseRiskResponse,
    RegionRisksResponse,
    RiskSummaryResponse,
)
from app.schemas.alert import (
    AlertBase,
    AlertCreate,
    AlertResponse,
    AlertListResponse,
)
from app.schemas.signal import (
    SignalBase,
    SignalCreate,
    SignalResponse,
    SignalAggregationResponse,
)

__all__ = [
    "RegionBase",
    "RegionCreate",
    "RegionResponse",
    "RegionListResponse",
    "RegionDetailResponse",
    "RiskIndexResponse",
    "DiseaseRiskResponse",
    "RegionRisksResponse",
    "RiskSummaryResponse",
    "AlertBase",
    "AlertCreate",
    "AlertResponse",
    "AlertListResponse",
    "SignalBase",
    "SignalCreate",
    "SignalResponse",
    "SignalAggregationResponse",
]
