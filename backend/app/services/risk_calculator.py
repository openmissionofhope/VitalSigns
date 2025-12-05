"""
Risk Calculator Service for VitalSigns.

Computes risk indices from aggregated signals using weighted algorithms.
All calculations use privacy-preserving, aggregated data only.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

import numpy as np
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.region import Region
from app.models.signal import Signal, SignalAggregation, SignalType
from app.models.risk import RiskIndex, DiseaseRisk, RiskLevel, DiseaseType
from app.models.alert import Alert, AlertType, AlertSeverity, AlertStatus
from app.core.config import settings


@dataclass
class SignalWeight:
    """Weight configuration for a signal in risk calculation."""
    signal_type: SignalType
    indicator: str
    weight: float
    invert: bool = False  # True if lower values indicate higher risk


class RiskCalculator:
    """
    Calculates risk indices for regions based on aggregated signals.

    The calculator uses weighted combinations of various signals to produce:
    1. Disease-specific risk indices (malaria, cholera, etc.)
    2. Hunger stress index
    3. Health system strain index
    4. Composite vital risk index
    """

    # Disease risk signal weights
    DISEASE_WEIGHTS: Dict[DiseaseType, List[SignalWeight]] = {
        DiseaseType.MALARIA: [
            SignalWeight(SignalType.WEATHER, "rainfall_mm", 0.25),
            SignalWeight(SignalType.WEATHER, "temperature_avg", 0.20),
            SignalWeight(SignalType.WEATHER, "humidity_pct", 0.15),
            SignalWeight(SignalType.DISEASE_REPORT, "malaria_cases", 0.25),
            SignalWeight(SignalType.HEALTH_FACILITY, "bed_occupancy_pct", 0.15),
        ],
        DiseaseType.CHOLERA: [
            SignalWeight(SignalType.WATER_QUALITY, "contamination_index", 0.30),
            SignalWeight(SignalType.WEATHER, "flooding_risk", 0.20),
            SignalWeight(SignalType.DISEASE_REPORT, "cholera_cases", 0.30),
            SignalWeight(SignalType.HEALTH_FACILITY, "ors_availability", 0.20, invert=True),
        ],
        DiseaseType.MEASLES: [
            SignalWeight(SignalType.DISEASE_REPORT, "measles_cases", 0.35),
            SignalWeight(SignalType.HEALTH_FACILITY, "vaccination_coverage", 0.35, invert=True),
            SignalWeight(SignalType.HUMANITARIAN, "displacement_index", 0.30),
        ],
        DiseaseType.DENGUE: [
            SignalWeight(SignalType.WEATHER, "rainfall_mm", 0.20),
            SignalWeight(SignalType.WEATHER, "temperature_avg", 0.20),
            SignalWeight(SignalType.DISEASE_REPORT, "dengue_cases", 0.35),
            SignalWeight(SignalType.HEALTH_FACILITY, "vector_control_index", 0.25, invert=True),
        ],
        DiseaseType.RESPIRATORY: [
            SignalWeight(SignalType.WEATHER, "temperature_avg", 0.15, invert=True),
            SignalWeight(SignalType.DISEASE_REPORT, "respiratory_cases", 0.40),
            SignalWeight(SignalType.HEALTH_FACILITY, "oxygen_availability", 0.25, invert=True),
            SignalWeight(SignalType.MOBILITY, "crowding_index", 0.20),
        ],
    }

    # Hunger stress signal weights
    HUNGER_WEIGHTS: List[SignalWeight] = [
        SignalWeight(SignalType.FOOD_PRICE, "staple_price_index", 0.30),
        SignalWeight(SignalType.CROP_INDICATOR, "harvest_index", 0.25, invert=True),
        SignalWeight(SignalType.WEATHER, "drought_index", 0.20),
        SignalWeight(SignalType.HUMANITARIAN, "food_insecurity_phase", 0.25),
    ]

    # Health system strain signal weights
    HEALTH_STRAIN_WEIGHTS: List[SignalWeight] = [
        SignalWeight(SignalType.HEALTH_FACILITY, "bed_occupancy_pct", 0.25),
        SignalWeight(SignalType.HEALTH_FACILITY, "staff_availability", 0.20, invert=True),
        SignalWeight(SignalType.PHARMACY, "essential_medicine_stock", 0.20, invert=True),
        SignalWeight(SignalType.HEALTH_FACILITY, "patient_wait_time", 0.20),
        SignalWeight(SignalType.HUMANITARIAN, "healthcare_access_index", 0.15, invert=True),
    ]

    # Composite weights
    COMPOSITE_WEIGHTS = {
        "hunger_stress": 0.30,
        "health_strain": 0.25,
        "disease_outbreak": 0.45,
    }

    # Risk level thresholds
    RISK_THRESHOLDS = {
        RiskLevel.CRITICAL: 80,
        RiskLevel.HIGH: 60,
        RiskLevel.MODERATE: 40,
        RiskLevel.LOW: 20,
        RiskLevel.MINIMAL: 0,
    }

    # Seasonal baselines for diseases (month -> expected index)
    SEASONAL_BASELINES: Dict[DiseaseType, Dict[int, float]] = {
        DiseaseType.MALARIA: {
            1: 30, 2: 35, 3: 45, 4: 55, 5: 60, 6: 50,
            7: 40, 8: 35, 9: 40, 10: 50, 11: 45, 12: 35,
        },
        DiseaseType.CHOLERA: {
            1: 25, 2: 30, 3: 40, 4: 50, 5: 55, 6: 45,
            7: 35, 8: 30, 9: 35, 10: 45, 11: 40, 12: 30,
        },
    }

    def __init__(self, db: AsyncSession):
        self.db = db

    async def calculate_all_risks(
        self,
        region_ids: Optional[List[int]] = None,
    ) -> Dict[int, RiskIndex]:
        """
        Calculate risk indices for all active regions or specified regions.

        Args:
            region_ids: Optional list of specific region IDs to calculate

        Returns:
            Dictionary mapping region IDs to their risk indices
        """
        # Get regions
        if region_ids:
            query = select(Region).where(
                Region.id.in_(region_ids),
                Region.is_active == True,
            )
        else:
            query = select(Region).where(Region.is_active == True)

        result = await self.db.execute(query)
        regions = result.scalars().all()

        risk_indices = {}
        for region in regions:
            risk_index = await self.calculate_region_risks(region)
            if risk_index:
                risk_indices[region.id] = risk_index

        return risk_indices

    async def calculate_region_risks(self, region: Region) -> Optional[RiskIndex]:
        """
        Calculate all risk indices for a single region.

        Args:
            region: Region to calculate risks for

        Returns:
            RiskIndex with computed values
        """
        now = datetime.utcnow()

        # Get recent signals for the region
        signals = await self._get_region_signals(region.id, days=30)

        if not signals:
            return None

        # Calculate disease risks
        disease_scores = {}
        for disease_type in DiseaseType:
            score, confidence = await self._calculate_disease_risk(
                region, disease_type, signals
            )
            disease_scores[disease_type] = (score, confidence)

            # Save disease risk
            await self._save_disease_risk(region, disease_type, score, confidence, now)

        # Calculate hunger stress
        hunger_score, hunger_confidence = await self._calculate_index(
            signals, self.HUNGER_WEIGHTS
        )

        # Calculate health system strain
        strain_score, strain_confidence = await self._calculate_index(
            signals, self.HEALTH_STRAIN_WEIGHTS
        )

        # Calculate disease outbreak index (max of disease scores)
        disease_values = [s[0] for s in disease_scores.values() if s[0] is not None]
        outbreak_score = max(disease_values) if disease_values else 0

        # Calculate composite vital risk index
        vital_risk = (
            self.COMPOSITE_WEIGHTS["hunger_stress"] * (hunger_score or 0) +
            self.COMPOSITE_WEIGHTS["health_strain"] * (strain_score or 0) +
            self.COMPOSITE_WEIGHTS["disease_outbreak"] * outbreak_score
        )

        # Determine risk level
        risk_level = self._get_risk_level(vital_risk)

        # Calculate data completeness
        total_signals = len(signals)
        expected_signals = 20  # Expected minimum signals for full coverage
        data_completeness = min(1.0, total_signals / expected_signals)

        # Average confidence
        all_confidences = [hunger_confidence, strain_confidence] + [
            s[1] for s in disease_scores.values() if s[1] is not None
        ]
        avg_confidence = sum(all_confidences) / len(all_confidences) if all_confidences else 0.5

        # Create risk index
        risk_index = RiskIndex(
            region_id=region.id,
            calculation_date=now,
            valid_from=now,
            valid_until=now + timedelta(hours=24),
            hunger_stress_index=hunger_score or 0,
            health_system_strain_index=strain_score or 0,
            disease_outbreak_index=outbreak_score,
            vital_risk_index=vital_risk,
            risk_level=risk_level,
            confidence_score=avg_confidence,
            data_completeness=data_completeness,
            weights=self.COMPOSITE_WEIGHTS,
            contributing_factors={
                "hunger_components": self._weight_list_to_dict(self.HUNGER_WEIGHTS),
                "health_strain_components": self._weight_list_to_dict(self.HEALTH_STRAIN_WEIGHTS),
                "disease_scores": {
                    k.value: v[0] for k, v in disease_scores.items() if v[0] is not None
                },
            },
        )

        self.db.add(risk_index)

        # Check for alerts
        await self._check_and_create_alerts(region, risk_index, disease_scores)

        return risk_index

    async def _get_region_signals(
        self,
        region_id: int,
        days: int = 30,
    ) -> Dict[Tuple[SignalType, str], List[Signal]]:
        """Get signals for a region grouped by type and indicator."""
        start_date = datetime.utcnow() - timedelta(days=days)

        query = (
            select(Signal)
            .where(Signal.region_id == region_id)
            .where(Signal.observation_date >= start_date)
            .order_by(Signal.observation_date.desc())
        )

        result = await self.db.execute(query)
        signals = result.scalars().all()

        # Group by type and indicator
        grouped: Dict[Tuple[SignalType, str], List[Signal]] = {}
        for signal in signals:
            key = (signal.signal_type, signal.indicator_name)
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(signal)

        return grouped

    async def _calculate_disease_risk(
        self,
        region: Region,
        disease_type: DiseaseType,
        signals: Dict[Tuple[SignalType, str], List[Signal]],
    ) -> Tuple[Optional[float], Optional[float]]:
        """Calculate risk score for a specific disease."""
        weights = self.DISEASE_WEIGHTS.get(disease_type, [])
        if not weights:
            return None, None

        return await self._calculate_index(signals, weights)

    async def _calculate_index(
        self,
        signals: Dict[Tuple[SignalType, str], List[Signal]],
        weights: List[SignalWeight],
    ) -> Tuple[Optional[float], Optional[float]]:
        """
        Calculate a weighted index from signals.

        Returns:
            Tuple of (score, confidence)
        """
        weighted_sum = 0.0
        total_weight = 0.0
        confidences = []

        for weight_config in weights:
            key = (weight_config.signal_type, weight_config.indicator)
            signal_list = signals.get(key, [])

            if not signal_list:
                continue

            # Use most recent signal
            signal = signal_list[0]

            # Normalize value to 0-100 scale
            normalized = self._normalize_value(
                signal.value,
                weight_config.signal_type,
                weight_config.indicator,
            )

            if weight_config.invert:
                normalized = 100 - normalized

            weighted_sum += normalized * weight_config.weight
            total_weight += weight_config.weight
            confidences.append(signal.confidence)

        if total_weight == 0:
            return None, None

        score = weighted_sum / total_weight
        confidence = sum(confidences) / len(confidences) if confidences else 0.5

        return score, confidence

    def _normalize_value(
        self,
        value: float,
        signal_type: SignalType,
        indicator: str,
    ) -> float:
        """
        Normalize a signal value to 0-100 scale.

        Uses indicator-specific ranges for normalization.
        """
        # Define typical ranges for different indicators
        ranges = {
            ("weather", "rainfall_mm"): (0, 500),
            ("weather", "temperature_avg"): (15, 40),
            ("weather", "humidity_pct"): (0, 100),
            ("food_price", "staple_price_index"): (80, 200),
            ("health_facility", "bed_occupancy_pct"): (0, 100),
            ("disease_report", "malaria_cases"): (0, 1000),
            ("disease_report", "cholera_cases"): (0, 500),
            ("disease_report", "measles_cases"): (0, 200),
            ("disease_report", "dengue_cases"): (0, 300),
            ("disease_report", "respiratory_cases"): (0, 500),
        }

        key = (signal_type.value, indicator)
        min_val, max_val = ranges.get(key, (0, 100))

        # Clamp and normalize
        clamped = max(min_val, min(max_val, value))
        normalized = ((clamped - min_val) / (max_val - min_val)) * 100

        return normalized

    def _get_risk_level(self, score: float) -> RiskLevel:
        """Determine risk level from score."""
        if score >= self.RISK_THRESHOLDS[RiskLevel.CRITICAL]:
            return RiskLevel.CRITICAL
        elif score >= self.RISK_THRESHOLDS[RiskLevel.HIGH]:
            return RiskLevel.HIGH
        elif score >= self.RISK_THRESHOLDS[RiskLevel.MODERATE]:
            return RiskLevel.MODERATE
        elif score >= self.RISK_THRESHOLDS[RiskLevel.LOW]:
            return RiskLevel.LOW
        else:
            return RiskLevel.MINIMAL

    async def _save_disease_risk(
        self,
        region: Region,
        disease_type: DiseaseType,
        score: Optional[float],
        confidence: Optional[float],
        calculation_date: datetime,
    ):
        """Save disease-specific risk to database."""
        if score is None:
            return

        # Get seasonal baseline
        month = calculation_date.month
        baselines = self.SEASONAL_BASELINES.get(disease_type, {})
        baseline = baselines.get(month, 30)

        deviation = score - baseline
        is_high_season = baseline > 40

        disease_risk = DiseaseRisk(
            region_id=region.id,
            disease_type=disease_type,
            calculation_date=calculation_date,
            valid_from=calculation_date,
            valid_until=calculation_date + timedelta(hours=24),
            risk_score=score,
            risk_level=self._get_risk_level(score),
            is_high_season=1 if is_high_season else 0,
            seasonal_baseline=baseline,
            deviation_from_seasonal=deviation,
            confidence_score=confidence or 0.5,
        )

        self.db.add(disease_risk)

    async def _check_and_create_alerts(
        self,
        region: Region,
        risk_index: RiskIndex,
        disease_scores: Dict[DiseaseType, Tuple[Optional[float], Optional[float]]],
    ):
        """Check thresholds and create alerts if needed."""
        now = datetime.utcnow()

        # Check composite risk
        if risk_index.vital_risk_index >= settings.ALERT_THRESHOLD * 100:
            severity = (
                AlertSeverity.CRITICAL
                if risk_index.risk_level == RiskLevel.CRITICAL
                else AlertSeverity.URGENT
            )

            alert = Alert(
                region_id=region.id,
                alert_type=AlertType.COMPOSITE_RISK,
                severity=severity,
                title=f"High Vital Risk Index in {region.name}",
                description=(
                    f"The composite vital risk index has reached {risk_index.vital_risk_index:.1f}, "
                    f"exceeding the alert threshold. Components: "
                    f"Hunger: {risk_index.hunger_stress_index:.1f}, "
                    f"Health Strain: {risk_index.health_system_strain_index:.1f}, "
                    f"Disease: {risk_index.disease_outbreak_index:.1f}."
                ),
                risk_score=risk_index.vital_risk_index,
                threshold_exceeded=settings.ALERT_THRESHOLD * 100,
                triggered_at=now,
                expires_at=now + timedelta(hours=48),
                confidence_score=risk_index.confidence_score,
                contributing_factors=risk_index.contributing_factors,
            )
            self.db.add(alert)

        # Check individual disease risks
        for disease_type, (score, confidence) in disease_scores.items():
            if score and score >= settings.ALERT_THRESHOLD * 100:
                alert = Alert(
                    region_id=region.id,
                    alert_type=AlertType.DISEASE_OUTBREAK,
                    severity=AlertSeverity.URGENT,
                    title=f"High {disease_type.value.title()} Risk in {region.name}",
                    description=(
                        f"{disease_type.value.title()} risk score has reached {score:.1f}, "
                        f"indicating potential outbreak conditions."
                    ),
                    risk_score=score,
                    threshold_exceeded=settings.ALERT_THRESHOLD * 100,
                    disease_type=disease_type.value,
                    triggered_at=now,
                    expires_at=now + timedelta(hours=48),
                    confidence_score=confidence or 0.5,
                )
                self.db.add(alert)

        # Check hunger stress
        if risk_index.hunger_stress_index >= settings.ALERT_THRESHOLD * 100:
            alert = Alert(
                region_id=region.id,
                alert_type=AlertType.HUNGER_CRISIS,
                severity=AlertSeverity.URGENT,
                title=f"High Hunger Stress in {region.name}",
                description=(
                    f"Hunger stress index has reached {risk_index.hunger_stress_index:.1f}, "
                    f"indicating significant food security concerns."
                ),
                risk_score=risk_index.hunger_stress_index,
                threshold_exceeded=settings.ALERT_THRESHOLD * 100,
                triggered_at=now,
                expires_at=now + timedelta(hours=48),
                confidence_score=risk_index.confidence_score,
            )
            self.db.add(alert)

    def _weight_list_to_dict(self, weights: List[SignalWeight]) -> Dict[str, Any]:
        """Convert weight list to dictionary for storage."""
        return {
            f"{w.signal_type.value}:{w.indicator}": {
                "weight": w.weight,
                "invert": w.invert,
            }
            for w in weights
        }
