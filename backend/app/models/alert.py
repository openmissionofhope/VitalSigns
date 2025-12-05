"""
Alert model for VitalSigns.
Represents generated alerts when risk thresholds are exceeded.
"""
from datetime import datetime
from enum import Enum

from sqlalchemy import (
    Boolean, Column, DateTime, Enum as SQLEnum, Float, ForeignKey,
    Integer, String, Text, Index
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.db.database import Base


class AlertType(str, Enum):
    """Types of alerts."""
    DISEASE_OUTBREAK = "disease_outbreak"
    HUNGER_CRISIS = "hunger_crisis"
    HEALTH_SYSTEM_STRAIN = "health_system_strain"
    COMPOSITE_RISK = "composite_risk"
    ANOMALY_DETECTED = "anomaly_detected"


class AlertSeverity(str, Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    URGENT = "urgent"
    CRITICAL = "critical"


class AlertStatus(str, Enum):
    """Alert lifecycle status."""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    EXPIRED = "expired"
    FALSE_POSITIVE = "false_positive"


class Alert(Base):
    """
    Alert generated when risk thresholds are exceeded.

    Alerts are informational only - VitalSigns does not provide
    medical advice or replace professional assessment.
    """

    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)

    # Region
    region_id = Column(Integer, ForeignKey("regions.id"), nullable=False)

    # Alert classification
    alert_type = Column(SQLEnum(AlertType), nullable=False)
    severity = Column(SQLEnum(AlertSeverity), nullable=False)
    status = Column(SQLEnum(AlertStatus), default=AlertStatus.ACTIVE)

    # Alert content
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)

    # Risk context
    risk_score = Column(Float, nullable=False)
    threshold_exceeded = Column(Float, nullable=False)
    disease_type = Column(String(50), nullable=True)

    # Timing
    triggered_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)

    # Data evidence
    contributing_factors = Column(JSONB, nullable=True)
    supporting_signals = Column(JSONB, nullable=True)

    # Confidence
    confidence_score = Column(Float, default=0.5)

    # Notes
    notes = Column(Text, nullable=True)
    resolution_notes = Column(Text, nullable=True)

    # Notification tracking
    notifications_sent = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    region = relationship("Region", back_populates="alerts")

    # Indexes
    __table_args__ = (
        Index("ix_alerts_region_status", "region_id", "status"),
        Index("ix_alerts_type_severity", "alert_type", "severity"),
        Index("ix_alerts_triggered", "triggered_at"),
        Index("ix_alerts_status_severity", "status", "severity"),
    )

    def __repr__(self) -> str:
        return f"<Alert(region={self.region_id}, type={self.alert_type}, severity={self.severity})>"
