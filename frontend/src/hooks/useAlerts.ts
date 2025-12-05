import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { alertsApi } from '../services/api';

export function useAlerts(params?: {
  status?: string;
  severity?: string;
  alert_type?: string;
  region_code?: string;
  limit?: number;
}) {
  return useQuery({
    queryKey: ['alerts', params],
    queryFn: () => alertsApi.getAll(params),
    refetchInterval: 60 * 1000, // Refresh every minute
  });
}

export function useActiveAlerts(severity?: string, limit?: number) {
  return useQuery({
    queryKey: ['alerts', 'active', severity, limit],
    queryFn: () => alertsApi.getActive({ severity, limit }),
    refetchInterval: 60 * 1000,
  });
}

export function useAlert(id: number) {
  return useQuery({
    queryKey: ['alerts', id],
    queryFn: () => alertsApi.getById(id),
    enabled: !!id,
  });
}

export function useAcknowledgeAlert() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, notes }: { id: number; notes?: string }) =>
      alertsApi.acknowledge(id, notes),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] });
    },
  });
}

export function useResolveAlert() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      id,
      resolution_notes,
      was_false_positive,
    }: {
      id: number;
      resolution_notes?: string;
      was_false_positive?: boolean;
    }) => alertsApi.resolve(id, { resolution_notes, was_false_positive }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] });
    },
  });
}
