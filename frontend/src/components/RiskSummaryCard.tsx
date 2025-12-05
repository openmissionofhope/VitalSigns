import type { RiskSummary } from '../types';
import { RISK_COLORS } from '../utils/risk';

interface RiskSummaryCardProps {
  summary: RiskSummary;
}

export function RiskSummaryCard({ summary }: RiskSummaryCardProps) {
  const distribution = [
    { level: 'Critical', count: summary.critical_count, color: RISK_COLORS.critical },
    { level: 'High', count: summary.high_count, color: RISK_COLORS.high },
    { level: 'Moderate', count: summary.moderate_count, color: RISK_COLORS.moderate },
    { level: 'Low', count: summary.low_count, color: RISK_COLORS.low },
    { level: 'Minimal', count: summary.minimal_count, color: RISK_COLORS.minimal },
  ];

  const total = summary.total_regions;

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">
        Risk Distribution
      </h3>

      <div className="space-y-3">
        {distribution.map(({ level, count, color }) => {
          const percentage = total > 0 ? (count / total) * 100 : 0;

          return (
            <div key={level}>
              <div className="flex justify-between text-sm mb-1">
                <span className="font-medium" style={{ color }}>
                  {level}
                </span>
                <span className="text-gray-600">
                  {count} ({percentage.toFixed(1)}%)
                </span>
              </div>
              <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-500"
                  style={{
                    width: `${percentage}%`,
                    backgroundColor: color,
                  }}
                />
              </div>
            </div>
          );
        })}
      </div>

      <div className="mt-4 pt-4 border-t border-gray-100">
        <div className="text-sm text-gray-600">
          Total Regions Monitored:{' '}
          <span className="font-semibold text-gray-900">{total}</span>
        </div>
      </div>
    </div>
  );
}
