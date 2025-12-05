"""
Signal models for VitalSigns.
Represents raw and aggregated data signals from various sources.
"""
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import (
    Boolean, Column, DateTime, Enum as SQLEnum, Float, ForeignKey,
    Integer, String, Text, Index
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.db.database import Base


class SignalType(str, Enum):
    """Types of signals that can be ingested."""
    WEATHER = "weather"
    FOOD_PRICE = "food_price"
    DISEASE_REPORT = "disease_report"
    HEALTH_FACILITY = "health_facility"
    CROP_INDICATOR = "crop_indicator"
    WATER_QUALITY = "water_quality"
    MEDIA_MENTION = "media_mention"
    MOBILITY = "mobility"
    PHARMACY = "pharmacy"
    HUMANITARIAN = "humanitarian"


class Signal(Base):
    """
    Raw signal data ingested from various sources.

    Signals are privacy-preserving, aggregated data points that
    contribute to risk calculations.
    """

    __tablename__ = "signals"

    id = Column(Integer, primary_key=True, index=True)

    # Source information
    source_id = Column(Integer, ForeignKey("data_sources.id"), nullable=False)
    signal_type = Column(SQLEnum(SignalType), nullable=False)

    # Region association
    region_id = Column(Integer, ForeignKey("regions.id"), nullable=False)

    # Signal data
    indicator_name = Column(String(255), nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String(50), nullable=True)

    # Quality metrics
    confidence = Column(Float, default=1.0)  # 0-1
    is_anomaly = Column(Boolean, default=False)
    quality_score = Column(Float, default=1.0)  # 0-1

    # Time context
    observation_date = Column(DateTime, nullable=False)
    reporting_date = Column(DateTime, nullable=False)

    # Metadata
    raw_data = Column(JSONB, nullable=True)
    processing_notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    region = relationship("Region", back_populates="signals")
    source = relationship("DataSource", back_populates="signals")

    # Indexes
    __table_args__ = (
        Index("ix_signals_region_type_date", "region_id", "signal_type", "observation_date"),
        Index("ix_signals_observation_date", "observation_date"),
        Index("ix_signals_indicator", "indicator_name"),
    )

    def __repr__(self) -> str:
        return f"<Signal(type={self.signal_type}, indicator={self.indicator_name}, value={self.value})>"


class SignalAggregation(Base):
    """
    Pre-computed aggregations of signals for faster querying.

    Stores daily, weekly, and monthly aggregations.
    """

    __tablename__ = "signal_aggregations"

    id = Column(Integer, primary_key=True, index=True)

    # Region and signal type
    region_id = Column(Integer, ForeignKey("regions.id"), nullable=False)
    signal_type = Column(SQLEnum(SignalType), nullable=False)
    indicator_name = Column(String(255), nullable=False)

    # Aggregation period
    period_type = Column(String(20), nullable=False)  # daily, weekly, monthly
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)

    # Aggregated values
    value_mean = Column(Float, nullable=False)
    value_median = Column(Float, nullable=True)
    value_min = Column(Float, nullable=True)
    value_max = Column(Float, nullable=True)
    value_std = Column(Float, nullable=True)
    sample_count = Column(Integer, nullable=False)

    # Comparison to baseline
    baseline_value = Column(Float, nullable=True)
    deviation_from_baseline = Column(Float, nullable=True)
    z_score = Column(Float, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Indexes
    __table_args__ = (
        Index("ix_agg_region_type_period", "region_id", "signal_type", "period_type", "period_start"),
        Index("ix_agg_indicator_period", "indicator_name", "period_start"),
    )

    def __repr__(self) -> str:
        return f"<SignalAggregation(region={self.region_id}, type={self.signal_type}, period={self.period_type})>"
