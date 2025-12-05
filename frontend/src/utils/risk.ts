import type { RiskLevel, AlertSeverity } from '../types';

export const RISK_COLORS: Record<RiskLevel, string> = {
  minimal: '#10B981',
  low: '#84CC16',
  moderate: '#F59E0B',
  high: '#F97316',
  critical: '#EF4444',
};

export const RISK_BG_COLORS: Record<RiskLevel, string> = {
  minimal: 'rgba(16, 185, 129, 0.2)',
  low: 'rgba(132, 204, 22, 0.2)',
  moderate: 'rgba(245, 158, 11, 0.2)',
  high: 'rgba(249, 115, 22, 0.2)',
  critical: 'rgba(239, 68, 68, 0.2)',
};

export const SEVERITY_COLORS: Record<AlertSeverity, string> = {
  info: '#3B82F6',
  warning: '#F59E0B',
  urgent: '#F97316',
  critical: '#EF4444',
};

export const DISEASE_COLORS: Record<string, string> = {
  malaria: '#8B5CF6',
  cholera: '#06B6D4',
  measles: '#EC4899',
  dengue: '#F97316',
  respiratory: '#6366F1',
  typhoid: '#14B8A6',
  ebola: '#DC2626',
  covid: '#64748B',
};

export function getRiskColor(level: RiskLevel): string {
  return RISK_COLORS[level] || RISK_COLORS.minimal;
}

export function getRiskBgColor(level: RiskLevel): string {
  return RISK_BG_COLORS[level] || RISK_BG_COLORS.minimal;
}

export function getRiskLabel(level: RiskLevel): string {
  const labels: Record<RiskLevel, string> = {
    minimal: 'Minimal',
    low: 'Low',
    moderate: 'Moderate',
    high: 'High',
    critical: 'Critical',
  };
  return labels[level] || 'Unknown';
}

export function getSeverityColor(severity: AlertSeverity): string {
  return SEVERITY_COLORS[severity] || SEVERITY_COLORS.info;
}

export function getDiseaseColor(disease: string): string {
  return DISEASE_COLORS[disease] || '#64748B';
}

export function formatRiskScore(score: number): string {
  return score.toFixed(1);
}

export function getRiskLevelFromScore(score: number): RiskLevel {
  if (score >= 80) return 'critical';
  if (score >= 60) return 'high';
  if (score >= 40) return 'moderate';
  if (score >= 20) return 'low';
  return 'minimal';
}

export function getMarkerSize(riskScore: number): number {
  // Scale marker size based on risk score (8-24 pixels)
  return 8 + (riskScore / 100) * 16;
}
