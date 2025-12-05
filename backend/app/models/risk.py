"""
Risk index models for VitalSigns.
Represents computed risk indices for regions.
"""
from datetime import datetime
from enum import Enum

from sqlalchemy import (
    Column, DateTime, Enum as SQLEnum, Float, ForeignKey,
    Integer, String, Text, Index
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.db.database import Base


class DiseaseType(str, Enum):
    """Disease types tracked by VitalSigns."""
    MALARIA = "malaria"
    CHOLERA = "cholera"
    MEASLES = "measles"
    DENGUE = "dengue"
    RESPIRATORY = "respiratory"
    TYPHOID = "typhoid"
    EBOLA = "ebola"
    COVID = "covid"


class RiskLevel(str, Enum):
    """Risk severity levels."""
    MINIMAL = "minimal"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class RiskIndex(Base):
    """
    Composite risk index for a region.

    Combines multiple risk factors into overall health/humanitarian risk scores.
    """

    __tablename__ = "risk_indices"

    id = Column(Integer, primary_key=True, index=True)

    # Region
    region_id = Column(Integer, ForeignKey("regions.id"), nullable=False)

    # Calculated date
    calculation_date = Column(DateTime, nullable=False)
    valid_from = Column(DateTime, nullable=False)
    valid_until = Column(DateTime, nullable=False)

    # Core indices (0-100 scale)
    hunger_stress_index = Column(Float, nullable=False, default=0)
    health_system_strain_index = Column(Float, nullable=False, default=0)
    disease_outbreak_index = Column(Float, nullable=False, default=0)

    # Composite score
    vital_risk_index = Column(Float, nullable=False, default=0)
    risk_level = Column(SQLEnum(RiskLevel), nullable=False, default=RiskLevel.MINIMAL)

    # Confidence and quality
    confidence_score = Column(Float, default=0.5)  # 0-1
    data_completeness = Column(Float, default=0.5)  # 0-1

    # Component weights used
    weights = Column(JSONB, nullable=True)

    # Contributing factors breakdown
    contributing_factors = Column(JSONB, nullable=True)

    # Model version
    model_version = Column(String(50), nullable=False, default="v1.0")

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    region = relationship("Region", back_populates="risk_indices")

    # Indexes
    __table_args__ = (
        Index("ix_risk_region_date", "region_id", "calculation_date"),
        Index("ix_risk_level_date", "risk_level", "calculation_date"),
        Index("ix_risk_vital_index", "vital_risk_index"),
    )

    def __repr__(self) -> str:
        return f"<RiskIndex(region={self.region_id}, vital_risk={self.vital_risk_index}, level={self.risk_level})>"


class DiseaseRisk(Base):
    """
    Disease-specific risk index for a region.

    Tracks individual disease outbreak risks.
    """

    __tablename__ = "disease_risks"

    id = Column(Integer, primary_key=True, index=True)

    # Region and disease
    region_id = Column(Integer, ForeignKey("regions.id"), nullable=False)
    disease_type = Column(SQLEnum(DiseaseType), nullable=False)

    # Calculated date
    calculation_date = Column(DateTime, nullable=False)
    valid_from = Column(DateTime, nullable=False)
    valid_until = Column(DateTime, nullable=False)

    # Risk metrics (0-100 scale)
    risk_score = Column(Float, nullable=False, default=0)
    risk_level = Column(SQLEnum(RiskLevel), nullable=False, default=RiskLevel.MINIMAL)

    # Seasonal context
    is_high_season = Column(Integer, default=0)  # 0 or 1
    seasonal_baseline = Column(Float, nullable=True)
    deviation_from_seasonal = Column(Float, nullable=True)

    # Trend
    trend_direction = Column(String(20), nullable=True)  # increasing, stable, decreasing
    trend_velocity = Column(Float, nullable=True)  # rate of change

    # Confidence
    confidence_score = Column(Float, default=0.5)

    # Contributing signals
    contributing_signals = Column(JSONB, nullable=True)

    # Model version
    model_version = Column(String(50), nullable=False, default="v1.0")

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    region = relationship("Region", back_populates="disease_risks")

    # Indexes
    __table_args__ = (
        Index("ix_disease_region_type_date", "region_id", "disease_type", "calculation_date"),
        Index("ix_disease_type_level", "disease_type", "risk_level"),
        Index("ix_disease_score", "risk_score"),
    )

    def __repr__(self) -> str:
        return f"<DiseaseRisk(region={self.region_id}, disease={self.disease_type}, score={self.risk_score})>"
