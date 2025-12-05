"""
Data source model for VitalSigns.
Tracks external data sources used for signal ingestion.
"""
from datetime import datetime
from enum import Enum

from sqlalchemy import (
    Boolean, Column, DateTime, Enum as SQLEnum, Float, Integer, String, Text, Index
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.db.database import Base


class SourceType(str, Enum):
    """Types of data sources."""
    API = "api"
    FILE = "file"
    SCRAPER = "scraper"
    MANUAL = "manual"
    STREAMING = "streaming"


class SourceCategory(str, Enum):
    """Categories of data sources."""
    WEATHER = "weather"
    HEALTH = "health"
    FOOD_SECURITY = "food_security"
    ECONOMIC = "economic"
    DEMOGRAPHIC = "demographic"
    HUMANITARIAN = "humanitarian"
    MEDIA = "media"


class DataSource(Base):
    """
    External data source configuration.

    All data sources must be:
    - Privacy-preserving (no individual data)
    - Aggregated or anonymized
    - From reputable organizations
    """

    __tablename__ = "data_sources"

    id = Column(Integer, primary_key=True, index=True)

    # Identification
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Classification
    source_type = Column(SQLEnum(SourceType), nullable=False)
    category = Column(SQLEnum(SourceCategory), nullable=False)

    # Provider information
    provider_name = Column(String(255), nullable=False)
    provider_url = Column(String(500), nullable=True)
    license_type = Column(String(100), nullable=True)

    # Data access
    endpoint_url = Column(String(500), nullable=True)
    api_version = Column(String(50), nullable=True)
    authentication_required = Column(Boolean, default=False)

    # Data characteristics
    update_frequency = Column(String(50), nullable=True)  # hourly, daily, weekly, etc.
    data_format = Column(String(50), nullable=True)  # json, csv, xml, etc.
    geographic_coverage = Column(JSONB, nullable=True)  # list of region codes
    temporal_coverage_start = Column(DateTime, nullable=True)

    # Quality metrics
    reliability_score = Column(Float, default=0.5)  # 0-1
    timeliness_score = Column(Float, default=0.5)  # 0-1
    completeness_score = Column(Float, default=0.5)  # 0-1

    # Status
    is_active = Column(Boolean, default=True)
    last_fetch_at = Column(DateTime, nullable=True)
    last_fetch_status = Column(String(50), nullable=True)
    last_fetch_records = Column(Integer, nullable=True)

    # Configuration
    config = Column(JSONB, nullable=True)  # source-specific configuration
    field_mappings = Column(JSONB, nullable=True)  # maps source fields to signals

    # Privacy compliance
    privacy_certified = Column(Boolean, default=False)
    privacy_notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    signals = relationship("Signal", back_populates="source", lazy="dynamic")

    # Indexes
    __table_args__ = (
        Index("ix_sources_category_active", "category", "is_active"),
        Index("ix_sources_type", "source_type"),
    )

    def __repr__(self) -> str:
        return f"<DataSource(code={self.code}, name={self.name}, category={self.category})>"
