"""
Signal Processor Service for VitalSigns.

Handles ingestion, validation, and processing of signals from various data sources.
All data must be aggregated and privacy-preserving.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

import numpy as np
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.region import Region
from app.models.signal import Signal, SignalAggregation, SignalType
from app.models.source import DataSource
import structlog

logger = structlog.get_logger(__name__)


@dataclass
class SignalInput:
    """Input format for signal data."""
    source_code: str
    region_code: str
    signal_type: str
    indicator_name: str
    value: float
    unit: Optional[str] = None
    observation_date: Optional[datetime] = None
    confidence: float = 1.0
    raw_data: Optional[Dict[str, Any]] = None


class SignalProcessor:
    """
    Processes and validates incoming signals.

    Features:
    - Signal validation and normalization
    - Anomaly detection
    - Quality scoring
    - Aggregation computation
    """

    # Expected value ranges for anomaly detection
    EXPECTED_RANGES: Dict[str, Dict[str, tuple]] = {
        SignalType.WEATHER.value: {
            "temperature_avg": (-20, 50),
            "rainfall_mm": (0, 1000),
            "humidity_pct": (0, 100),
            "wind_speed_kmh": (0, 200),
            "drought_index": (0, 100),
            "flooding_risk": (0, 100),
        },
        SignalType.FOOD_PRICE.value: {
            "staple_price_index": (50, 300),
            "maize_price_usd": (0, 500),
            "rice_price_usd": (0, 500),
            "wheat_price_usd": (0, 500),
        },
        SignalType.DISEASE_REPORT.value: {
            "malaria_cases": (0, 10000),
            "cholera_cases": (0, 5000),
            "measles_cases": (0, 2000),
            "dengue_cases": (0, 3000),
            "respiratory_cases": (0, 5000),
        },
        SignalType.HEALTH_FACILITY.value: {
            "bed_occupancy_pct": (0, 100),
            "staff_availability": (0, 100),
            "oxygen_availability": (0, 100),
            "ors_availability": (0, 100),
            "vaccination_coverage": (0, 100),
            "patient_wait_time": (0, 480),  # minutes
        },
    }

    def __init__(self, db: AsyncSession):
        self.db = db

    async def process_signals(
        self,
        signals: List[SignalInput],
    ) -> Dict[str, Any]:
        """
        Process a batch of signals.

        Args:
            signals: List of signal inputs

        Returns:
            Processing results summary
        """
        results = {
            "total": len(signals),
            "processed": 0,
            "rejected": 0,
            "anomalies": 0,
            "errors": [],
        }

        for signal_input in signals:
            try:
                signal = await self.process_single_signal(signal_input)
                if signal:
                    results["processed"] += 1
                    if signal.is_anomaly:
                        results["anomalies"] += 1
                else:
                    results["rejected"] += 1
            except Exception as e:
                results["errors"].append({
                    "signal": signal_input.indicator_name,
                    "error": str(e),
                })
                results["rejected"] += 1

        return results

    async def process_single_signal(
        self,
        signal_input: SignalInput,
    ) -> Optional[Signal]:
        """
        Process a single signal.

        Args:
            signal_input: Signal input data

        Returns:
            Processed Signal or None if rejected
        """
        # Validate and get source
        source = await self._get_source(signal_input.source_code)
        if not source:
            logger.warning(
                "Unknown source",
                source_code=signal_input.source_code,
            )
            return None

        # Validate and get region
        region = await self._get_region(signal_input.region_code)
        if not region:
            logger.warning(
                "Unknown region",
                region_code=signal_input.region_code,
            )
            return None

        # Validate signal type
        try:
            signal_type = SignalType(signal_input.signal_type)
        except ValueError:
            logger.warning(
                "Invalid signal type",
                signal_type=signal_input.signal_type,
            )
            return None

        # Check for anomalies
        is_anomaly = self._detect_anomaly(
            signal_type.value,
            signal_input.indicator_name,
            signal_input.value,
        )

        # Calculate quality score
        quality_score = self._calculate_quality_score(
            signal_input,
            source,
            is_anomaly,
        )

        # Create signal
        now = datetime.utcnow()
        signal = Signal(
            source_id=source.id,
            signal_type=signal_type,
            region_id=region.id,
            indicator_name=signal_input.indicator_name,
            value=signal_input.value,
            unit=signal_input.unit,
            confidence=signal_input.confidence,
            is_anomaly=is_anomaly,
            quality_score=quality_score,
            observation_date=signal_input.observation_date or now,
            reporting_date=now,
            raw_data=signal_input.raw_data,
        )

        self.db.add(signal)

        if is_anomaly:
            logger.info(
                "Anomaly detected",
                region=region.code,
                indicator=signal_input.indicator_name,
                value=signal_input.value,
            )

        return signal

    async def _get_source(self, code: str) -> Optional[DataSource]:
        """Get data source by code."""
        query = select(DataSource).where(
            DataSource.code == code,
            DataSource.is_active == True,
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def _get_region(self, code: str) -> Optional[Region]:
        """Get region by code."""
        query = select(Region).where(
            Region.code == code,
            Region.is_active == True,
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    def _detect_anomaly(
        self,
        signal_type: str,
        indicator: str,
        value: float,
    ) -> bool:
        """
        Detect if a value is anomalous based on expected ranges.

        Returns:
            True if the value is outside expected ranges
        """
        type_ranges = self.EXPECTED_RANGES.get(signal_type, {})
        expected_range = type_ranges.get(indicator)

        if not expected_range:
            return False

        min_val, max_val = expected_range
        return value < min_val or value > max_val

    def _calculate_quality_score(
        self,
        signal_input: SignalInput,
        source: DataSource,
        is_anomaly: bool,
    ) -> float:
        """
        Calculate quality score for a signal.

        Factors:
        - Source reliability
        - Signal confidence
        - Anomaly status
        - Data freshness
        """
        base_score = 1.0

        # Source reliability factor
        base_score *= source.reliability_score

        # Signal confidence factor
        base_score *= signal_input.confidence

        # Anomaly penalty
        if is_anomaly:
            base_score *= 0.7

        # Freshness factor
        if signal_input.observation_date:
            age_hours = (datetime.utcnow() - signal_input.observation_date).total_seconds() / 3600
            if age_hours > 24:
                base_score *= max(0.5, 1.0 - (age_hours - 24) / 168)  # Decay over a week

        return min(1.0, max(0.0, base_score))

    async def compute_aggregations(
        self,
        region_id: int,
        period_type: str = "daily",
        days_back: int = 7,
    ) -> int:
        """
        Compute signal aggregations for a region.

        Args:
            region_id: Region to compute aggregations for
            period_type: Aggregation period (daily, weekly, monthly)
            days_back: How many days back to compute

        Returns:
            Number of aggregations created
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days_back)

        # Get distinct signal types and indicators for the region
        distinct_query = (
            select(Signal.signal_type, Signal.indicator_name)
            .where(Signal.region_id == region_id)
            .where(Signal.observation_date >= start_date)
            .distinct()
        )
        result = await self.db.execute(distinct_query)
        distinct_signals = result.all()

        aggregation_count = 0

        for signal_type, indicator_name in distinct_signals:
            # Get signals for this type/indicator
            signals_query = (
                select(Signal)
                .where(Signal.region_id == region_id)
                .where(Signal.signal_type == signal_type)
                .where(Signal.indicator_name == indicator_name)
                .where(Signal.observation_date >= start_date)
                .order_by(Signal.observation_date)
            )
            signals_result = await self.db.execute(signals_query)
            signals = signals_result.scalars().all()

            if not signals:
                continue

            # Group by period
            periods = self._group_by_period(signals, period_type)

            for period_start, period_signals in periods.items():
                if not period_signals:
                    continue

                values = [s.value for s in period_signals]

                # Calculate period end
                if period_type == "daily":
                    period_end = period_start + timedelta(days=1)
                elif period_type == "weekly":
                    period_end = period_start + timedelta(weeks=1)
                else:  # monthly
                    period_end = period_start + timedelta(days=30)

                # Calculate statistics
                aggregation = SignalAggregation(
                    region_id=region_id,
                    signal_type=signal_type,
                    indicator_name=indicator_name,
                    period_type=period_type,
                    period_start=period_start,
                    period_end=period_end,
                    value_mean=float(np.mean(values)),
                    value_median=float(np.median(values)),
                    value_min=float(np.min(values)),
                    value_max=float(np.max(values)),
                    value_std=float(np.std(values)) if len(values) > 1 else 0,
                    sample_count=len(values),
                )

                # Calculate baseline comparison if we have historical data
                baseline = await self._get_baseline(
                    region_id,
                    signal_type,
                    indicator_name,
                    period_start,
                )
                if baseline:
                    aggregation.baseline_value = baseline
                    aggregation.deviation_from_baseline = aggregation.value_mean - baseline
                    if baseline > 0:
                        aggregation.z_score = (aggregation.value_mean - baseline) / max(baseline * 0.1, 1)

                self.db.add(aggregation)
                aggregation_count += 1

        return aggregation_count

    def _group_by_period(
        self,
        signals: List[Signal],
        period_type: str,
    ) -> Dict[datetime, List[Signal]]:
        """Group signals by time period."""
        groups: Dict[datetime, List[Signal]] = {}

        for signal in signals:
            if period_type == "daily":
                period_start = signal.observation_date.replace(
                    hour=0, minute=0, second=0, microsecond=0
                )
            elif period_type == "weekly":
                # Start of week (Monday)
                days_since_monday = signal.observation_date.weekday()
                period_start = (
                    signal.observation_date - timedelta(days=days_since_monday)
                ).replace(hour=0, minute=0, second=0, microsecond=0)
            else:  # monthly
                period_start = signal.observation_date.replace(
                    day=1, hour=0, minute=0, second=0, microsecond=0
                )

            if period_start not in groups:
                groups[period_start] = []
            groups[period_start].append(signal)

        return groups

    async def _get_baseline(
        self,
        region_id: int,
        signal_type: SignalType,
        indicator_name: str,
        reference_date: datetime,
    ) -> Optional[float]:
        """
        Get historical baseline for comparison.

        Uses same period from previous year.
        """
        # Look for same period last year
        year_ago = reference_date - timedelta(days=365)
        window_start = year_ago - timedelta(days=15)
        window_end = year_ago + timedelta(days=15)

        query = (
            select(func.avg(Signal.value))
            .where(Signal.region_id == region_id)
            .where(Signal.signal_type == signal_type)
            .where(Signal.indicator_name == indicator_name)
            .where(Signal.observation_date >= window_start)
            .where(Signal.observation_date <= window_end)
        )

        result = await self.db.scalar(query)
        return float(result) if result else None
