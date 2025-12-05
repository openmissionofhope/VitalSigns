import type { RiskLevel } from '../types';
import { RiskBadge } from './RiskBadge';
import { formatRiskScore } from '../utils/risk';
import { TrendingUp } from 'lucide-react';

interface TopRiskRegion {
  region_code: string;
  region_name: string;
  vital_risk_index: number;
  risk_level: RiskLevel;
}

interface TopRiskRegionsProps {
  regions: TopRiskRegion[];
  onRegionClick?: (regionCode: string) => void;
}

export function TopRiskRegions({ regions, onRegionClick }: TopRiskRegionsProps) {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-800">
          Highest Risk Regions
        </h3>
        <TrendingUp className="w-5 h-5 text-gray-400" />
      </div>

      <div className="space-y-3">
        {regions.map((region, index) => (
          <div
            key={region.region_code}
            className="flex items-center justify-between p-2 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
            onClick={() => onRegionClick?.(region.region_code)}
          >
            <div className="flex items-center space-x-3">
              <span className="w-6 h-6 flex items-center justify-center rounded-full bg-gray-100 text-sm font-medium text-gray-600">
                {index + 1}
              </span>
              <div>
                <p className="font-medium text-gray-900">{region.region_name}</p>
                <p className="text-xs text-gray-500">{region.region_code}</p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <span className="text-sm font-semibold">
                {formatRiskScore(region.vital_risk_index)}
              </span>
              <RiskBadge level={region.risk_level} size="sm" />
            </div>
          </div>
        ))}
      </div>

      {regions.length === 0 && (
        <p className="text-center text-gray-500 py-4">No high-risk regions</p>
      )}
    </div>
  );
}
