import { useQuery } from '@tanstack/react-query';
import { risksApi } from '../services/api';

export function useRiskSummary(continent?: string, level?: string) {
  return useQuery({
    queryKey: ['risks', 'summary', continent, level],
    queryFn: () => risksApi.getSummary({ continent, level }),
    refetchInterval: 5 * 60 * 1000, // Refresh every 5 minutes
  });
}

export function useRiskMap(level?: string) {
  return useQuery({
    queryKey: ['risks', 'map', level],
    queryFn: () => risksApi.getMap(level),
    refetchInterval: 5 * 60 * 1000,
  });
}

export function useRegionRisks(regionCode: string) {
  return useQuery({
    queryKey: ['risks', 'region', regionCode],
    queryFn: () => risksApi.getRegionRisks(regionCode),
    enabled: !!regionCode,
  });
}

export function useDiseaseRisks(
  diseaseType: string,
  riskLevel?: string,
  limit?: number
) {
  return useQuery({
    queryKey: ['risks', 'disease', diseaseType, riskLevel, limit],
    queryFn: () =>
      risksApi.getDiseaseRisks(diseaseType, { risk_level: riskLevel, limit }),
    enabled: !!diseaseType,
  });
}
