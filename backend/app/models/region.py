"""
Region model for VitalSigns.
Represents geographic regions being monitored.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.db.database import Base


class Region(Base):
    """
    Geographic region being monitored by VitalSigns.

    Regions can be countries, provinces, districts, or custom areas.
    Each region has associated risk indices and signals.
    """

    __tablename__ = "regions"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    name_local = Column(String(255), nullable=True)

    # Geographic hierarchy
    level = Column(String(50), nullable=False)  # country, province, district
    parent_code = Column(String(50), nullable=True, index=True)

    # Location data
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    bbox = Column(JSONB, nullable=True)  # Bounding box [minLon, minLat, maxLon, maxLat]

    # Demographics (aggregated, non-personal)
    population = Column(Integer, nullable=True)
    population_density = Column(Float, nullable=True)
    area_km2 = Column(Float, nullable=True)

    # Metadata
    iso_code = Column(String(10), nullable=True)  # ISO 3166 code
    continent = Column(String(50), nullable=True)
    timezone = Column(String(50), nullable=True)

    # Status
    is_active = Column(Boolean, default=True)
    monitoring_priority = Column(Integer, default=5)  # 1-10, higher = more priority

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    risk_indices = relationship("RiskIndex", back_populates="region", lazy="dynamic")
    disease_risks = relationship("DiseaseRisk", back_populates="region", lazy="dynamic")
    signals = relationship("Signal", back_populates="region", lazy="dynamic")
    alerts = relationship("Alert", back_populates="region", lazy="dynamic")

    # Indexes
    __table_args__ = (
        Index("ix_regions_level_active", "level", "is_active"),
        Index("ix_regions_continent", "continent"),
        Index("ix_regions_location", "latitude", "longitude"),
    )

    def __repr__(self) -> str:
        return f"<Region(code={self.code}, name={self.name}, level={self.level})>"
