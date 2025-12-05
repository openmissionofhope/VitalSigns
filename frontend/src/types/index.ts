// Region types
export interface Region {
  id: number;
  code: string;
  name: string;
  name_local?: string;
  level: string;
  parent_code?: string;
  latitude: number;
  longitude: number;
  population?: number;
  continent?: string;
  iso_code?: string;
  is_active: boolean;
  monitoring_priority: number;
  current_risk_level?: RiskLevel;
  current_vital_risk_index?: number;
}

export interface RegionDetail extends Region {
  area_km2?: number;
  population_density?: number;
  timezone?: string;
  bbox?: number[];
  created_at: string;
  updated_at: string;
  hunger_stress_index?: number;
  health_system_strain_index?: number;
  disease_outbreak_index?: number;
  active_alerts_count: number;
}

// Risk types
export type RiskLevel = 'minimal' | 'low' | 'moderate' | 'high' | 'critical';

export type DiseaseType =
  | 'malaria'
  | 'cholera'
  | 'measles'
  | 'dengue'
  | 'respiratory'
  | 'typhoid'
  | 'ebola'
  | 'covid';

export interface RiskIndex {
  region_id: number;
  region_code: string;
  region_name: string;
  hunger_stress_index: number;
  health_system_strain_index: number;
  disease_outbreak_index: number;
  vital_risk_index: number;
  risk_level: RiskLevel;
  confidence_score: number;
  data_completeness: number;
  calculation_date: string;
  valid_from: string;
  valid_until: string;
  model_version: string;
  contributing_factors?: Record<string, unknown>;
}

export interface DiseaseRisk {
  disease_type: DiseaseType;
  risk_score: number;
  risk_level: RiskLevel;
  is_high_season: boolean;
  seasonal_baseline?: number;
  deviation_from_seasonal?: number;
  trend_direction?: 'increasing' | 'stable' | 'decreasing';
  trend_velocity?: number;
  confidence_score: number;
  calculation_date: string;
  contributing_signals?: Record<string, unknown>;
}

export interface RegionRisks {
  region_id: number;
  region_code: string;
  region_name: string;
  composite_risk: RiskIndex;
  disease_risks: DiseaseRisk[];
  risk_trend?: Array<{
    date: string;
    vital_risk_index: number;
    risk_level: RiskLevel;
  }>;
}

export interface RiskSummary {
  total_regions: number;
  timestamp: string;
  critical_count: number;
  high_count: number;
  moderate_count: number;
  low_count: number;
  minimal_count: number;
  top_risk_regions: Array<{
    region_code: string;
    region_name: string;
    vital_risk_index: number;
    risk_level: RiskLevel;
  }>;
  disease_hotspots: Record<
    string,
    Array<{
      region_code: string;
      region_name: string;
      risk_score: number;
      risk_level: RiskLevel;
    }>
  >;
}

export interface MapRegion {
  code: string;
  name: string;
  lat: number;
  lng: number;
  iso_code?: string;
  vital_risk_index: number;
  risk_level: RiskLevel;
  hunger_stress: number;
  health_strain: number;
  disease_outbreak: number;
}

// Alert types
export type AlertType =
  | 'disease_outbreak'
  | 'hunger_crisis'
  | 'health_system_strain'
  | 'composite_risk'
  | 'anomaly_detected';

export type AlertSeverity = 'info' | 'warning' | 'urgent' | 'critical';

export type AlertStatus =
  | 'active'
  | 'acknowledged'
  | 'resolved'
  | 'expired'
  | 'false_positive';

export interface Alert {
  id: number;
  region_id: number;
  region_code: string;
  region_name: string;
  alert_type: AlertType;
  severity: AlertSeverity;
  status: AlertStatus;
  title: string;
  description?: string;
  risk_score: number;
  threshold_exceeded: number;
  disease_type?: DiseaseType;
  triggered_at: string;
  expires_at?: string;
  acknowledged_at?: string;
  resolved_at?: string;
  confidence_score: number;
  contributing_factors?: Record<string, unknown>;
}

// Signal types
export type SignalType =
  | 'weather'
  | 'food_price'
  | 'disease_report'
  | 'health_facility'
  | 'crop_indicator'
  | 'water_quality'
  | 'media_mention'
  | 'mobility'
  | 'pharmacy'
  | 'humanitarian';

export interface Signal {
  id: number;
  source_id: number;
  source_name: string;
  region_id: number;
  region_code: string;
  signal_type: SignalType;
  indicator_name: string;
  value: number;
  unit?: string;
  confidence: number;
  is_anomaly: boolean;
  quality_score: number;
  observation_date: string;
  reporting_date: string;
  created_at: string;
}

export interface SignalTimeSeries {
  region_id: number;
  region_code: string;
  signal_type: SignalType;
  indicator_name: string;
  unit?: string;
  data_points: Array<{
    date: string;
    value: number;
    confidence: number;
    is_anomaly: boolean;
  }>;
  mean?: number;
  std?: number;
  trend?: 'increasing' | 'stable' | 'decreasing';
}

// API response types
export interface PaginatedResponse<T> {
  total: number;
  items: T[];
}

export interface RegionListResponse {
  total: number;
  regions: Region[];
}

export interface AlertListResponse {
  total: number;
  active_count: number;
  alerts: Alert[];
}

export interface GlobalRiskMapResponse {
  timestamp: string;
  regions: MapRegion[];
}
