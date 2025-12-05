import { useQuery } from '@tanstack/react-query';
import { regionsApi } from '../services/api';

export function useRegions(params?: {
  level?: string;
  continent?: string;
  parent_code?: string;
  skip?: number;
  limit?: number;
}) {
  return useQuery({
    queryKey: ['regions', params],
    queryFn: () => regionsApi.getAll(params),
  });
}

export function useRegion(code: string) {
  return useQuery({
    queryKey: ['regions', code],
    queryFn: () => regionsApi.getById(code),
    enabled: !!code,
  });
}

export function useRegionChildren(code: string) {
  return useQuery({
    queryKey: ['regions', code, 'children'],
    queryFn: () => regionsApi.getChildren(code),
    enabled: !!code,
  });
}
