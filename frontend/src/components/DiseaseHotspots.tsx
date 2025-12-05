import type { RiskLevel } from '../types';
import { getDiseaseColor, formatRiskScore } from '../utils/risk';
import { Activity } from 'lucide-react';

interface DiseaseHotspot {
  region_code: string;
  region_name: string;
  risk_score: number;
  risk_level: RiskLevel;
}

interface DiseaseHotspotsProps {
  hotspots: Record<string, DiseaseHotspot[]>;
  onRegionClick?: (regionCode: string) => void;
}

const DISEASE_LABELS: Record<string, string> = {
  malaria: 'Malaria',
  cholera: 'Cholera',
  measles: 'Measles',
  dengue: 'Dengue',
  respiratory: 'Respiratory',
  typhoid: 'Typhoid',
  ebola: 'Ebola',
  covid: 'COVID-19',
};

export function DiseaseHotspots({ hotspots, onRegionClick }: DiseaseHotspotsProps) {
  const diseases = Object.entries(hotspots).filter(([_, regions]) => regions.length > 0);

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-800">Disease Hotspots</h3>
        <Activity className="w-5 h-5 text-gray-400" />
      </div>

      {diseases.length === 0 ? (
        <p className="text-center text-gray-500 py-4">
          No active disease hotspots
        </p>
      ) : (
        <div className="space-y-4">
          {diseases.map(([disease, regions]) => {
            const color = getDiseaseColor(disease);

            return (
              <div key={disease}>
                <div
                  className="flex items-center space-x-2 mb-2"
                  style={{ color }}
                >
                  <span
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: color }}
                  />
                  <span className="font-medium">
                    {DISEASE_LABELS[disease] || disease}
                  </span>
                </div>

                <div className="pl-5 space-y-1">
                  {regions.slice(0, 3).map((region) => (
                    <div
                      key={region.region_code}
                      className="flex items-center justify-between text-sm py-1 px-2 rounded hover:bg-gray-50 cursor-pointer"
                      onClick={() => onRegionClick?.(region.region_code)}
                    >
                      <span className="text-gray-700">{region.region_name}</span>
                      <span className="font-medium" style={{ color }}>
                        {formatRiskScore(region.risk_score)}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
