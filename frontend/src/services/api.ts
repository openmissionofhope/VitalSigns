import axios from 'axios';
import type {
  Region,
  RegionDetail,
  RegionListResponse,
  RiskSummary,
  RegionRisks,
  DiseaseRisk,
  Alert,
  AlertListResponse,
  GlobalRiskMapResponse,
  Signal,
  SignalTimeSeries,
} from '../types';

const API_BASE = '/api/v1';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Region endpoints
export const regionsApi = {
  getAll: async (params?: {
    level?: string;
    continent?: string;
    parent_code?: string;
    skip?: number;
    limit?: number;
  }): Promise<RegionListResponse> => {
    const { data } = await api.get('/regions', { params });
    return data;
  },

  getById: async (code: string): Promise<RegionDetail> => {
    const { data } = await api.get(`/regions/${code}`);
    return data;
  },

  getChildren: async (code: string): Promise<RegionListResponse> => {
    const { data } = await api.get(`/regions/${code}/children`);
    return data;
  },
};

// Risk endpoints
export const risksApi = {
  getSummary: async (params?: {
    continent?: string;
    level?: string;
  }): Promise<RiskSummary> => {
    const { data } = await api.get('/risks/summary', { params });
    return data;
  },

  getMap: async (level?: string): Promise<GlobalRiskMapResponse> => {
    const { data } = await api.get('/risks/map', {
      params: { level: level || 'country' },
    });
    return data;
  },

  getRegionRisks: async (regionCode: string): Promise<RegionRisks> => {
    const { data } = await api.get(`/risks/regions/${regionCode}`);
    return data;
  },

  getDiseaseRisks: async (
    diseaseType: string,
    params?: { risk_level?: string; limit?: number }
  ): Promise<DiseaseRisk[]> => {
    const { data } = await api.get(`/risks/diseases/${diseaseType}`, { params });
    return data;
  },
};

// Alert endpoints
export const alertsApi = {
  getAll: async (params?: {
    status?: string;
    severity?: string;
    alert_type?: string;
    region_code?: string;
    skip?: number;
    limit?: number;
  }): Promise<AlertListResponse> => {
    const { data } = await api.get('/alerts', { params });
    return data;
  },

  getActive: async (params?: {
    severity?: string;
    limit?: number;
  }): Promise<AlertListResponse> => {
    const { data } = await api.get('/alerts/active', { params });
    return data;
  },

  getById: async (id: number): Promise<Alert> => {
    const { data } = await api.get(`/alerts/${id}`);
    return data;
  },

  acknowledge: async (
    id: number,
    notes?: string
  ): Promise<Alert> => {
    const { data } = await api.post(`/alerts/${id}/acknowledge`, { notes });
    return data;
  },

  resolve: async (
    id: number,
    params: { resolution_notes?: string; was_false_positive?: boolean }
  ): Promise<Alert> => {
    const { data } = await api.post(`/alerts/${id}/resolve`, params);
    return data;
  },
};

// Signal endpoints
export const signalsApi = {
  getTypes: async () => {
    const { data } = await api.get('/signals/types');
    return data;
  },

  getRegionSignals: async (
    regionCode: string,
    params?: {
      signal_type?: string;
      indicator?: string;
      days?: number;
      limit?: number;
    }
  ): Promise<Signal[]> => {
    const { data } = await api.get(`/signals/regions/${regionCode}`, { params });
    return data;
  },

  getTimeSeries: async (
    regionCode: string,
    signalType: string,
    indicator: string,
    days?: number
  ): Promise<SignalTimeSeries> => {
    const { data } = await api.get(`/signals/regions/${regionCode}/timeseries`, {
      params: { signal_type: signalType, indicator, days },
    });
    return data;
  },
};

// Health check
export const healthApi = {
  check: async () => {
    const { data } = await api.get('/health');
    return data;
  },

  ready: async () => {
    const { data } = await api.get('/health/ready');
    return data;
  },
};

export default api;
