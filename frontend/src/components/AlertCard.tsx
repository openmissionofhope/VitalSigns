import { format } from 'date-fns';
import {
  AlertTriangle,
  AlertCircle,
  Info,
  MapPin,
  Clock,
} from 'lucide-react';
import type { Alert, AlertSeverity } from '../types';
import { getSeverityColor } from '../utils/risk';

interface AlertCardProps {
  alert: Alert;
  onClick?: () => void;
}

const severityIcons: Record<AlertSeverity, React.ReactNode> = {
  critical: <AlertTriangle className="w-5 h-5" />,
  urgent: <AlertCircle className="w-5 h-5" />,
  warning: <AlertCircle className="w-5 h-5" />,
  info: <Info className="w-5 h-5" />,
};

export function AlertCard({ alert, onClick }: AlertCardProps) {
  const color = getSeverityColor(alert.severity);

  return (
    <div
      className="bg-white rounded-lg border shadow-sm p-4 cursor-pointer hover:shadow-md transition-shadow"
      style={{ borderLeftColor: color, borderLeftWidth: '4px' }}
      onClick={onClick}
    >
      <div className="flex items-start justify-between">
        <div className="flex items-start space-x-3">
          <div style={{ color }}>{severityIcons[alert.severity]}</div>
          <div>
            <h3 className="font-semibold text-gray-900">{alert.title}</h3>
            <div className="flex items-center text-sm text-gray-500 mt-1">
              <MapPin className="w-4 h-4 mr-1" />
              {alert.region_name}
            </div>
          </div>
        </div>
        <span
          className="px-2 py-1 rounded-full text-xs font-medium capitalize"
          style={{ backgroundColor: `${color}20`, color }}
        >
          {alert.severity}
        </span>
      </div>

      {alert.description && (
        <p className="text-sm text-gray-600 mt-3 line-clamp-2">
          {alert.description}
        </p>
      )}

      <div className="flex items-center justify-between mt-3 pt-3 border-t border-gray-100">
        <div className="flex items-center text-xs text-gray-500">
          <Clock className="w-3 h-3 mr-1" />
          {format(new Date(alert.triggered_at), 'MMM d, HH:mm')}
        </div>
        <div className="text-xs">
          <span className="text-gray-500">Risk Score: </span>
          <span className="font-medium" style={{ color }}>
            {alert.risk_score.toFixed(1)}
          </span>
        </div>
      </div>
    </div>
  );
}
