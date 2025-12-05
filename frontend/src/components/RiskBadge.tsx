import type { RiskLevel } from '../types';
import { getRiskColor, getRiskLabel } from '../utils/risk';

interface RiskBadgeProps {
  level: RiskLevel;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
}

export function RiskBadge({
  level,
  size = 'md',
  showLabel = true,
}: RiskBadgeProps) {
  const color = getRiskColor(level);
  const label = getRiskLabel(level);

  const sizeClasses = {
    sm: 'px-1.5 py-0.5 text-xs',
    md: 'px-2 py-1 text-sm',
    lg: 'px-3 py-1.5 text-base',
  };

  return (
    <span
      className={`inline-flex items-center rounded-full font-medium ${sizeClasses[size]}`}
      style={{
        backgroundColor: `${color}20`,
        color: color,
      }}
    >
      <span
        className="w-2 h-2 rounded-full mr-1.5"
        style={{ backgroundColor: color }}
      />
      {showLabel && label}
    </span>
  );
}
