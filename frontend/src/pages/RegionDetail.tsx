import { useParams, useNavigate } from 'react-router-dom';
import { format } from 'date-fns';
import {
  ArrowLeft,
  MapPin,
  Users,
  AlertTriangle,
  Activity,
  Utensils,
  Building2,
} from 'lucide-react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  Cell,
} from 'recharts';

import { RiskBadge } from '../components/RiskBadge';
import { useRegion } from '../hooks/useRegions';
import { useRegionRisks } from '../hooks/useRisks';
import { getDiseaseColor, formatRiskScore, RISK_COLORS } from '../utils/risk';
import type { RiskLevel } from '../types';

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

export function RegionDetail() {
  const { code } = useParams<{ code: string }>();
  const navigate = useNavigate();

  const { data: region, isLoading: regionLoading } = useRegion(code || '');
  const { data: risks, isLoading: risksLoading } = useRegionRisks(code || '');

  if (regionLoading || risksLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <p className="text-gray-500">Loading region data...</p>
      </div>
    );
  }

  if (!region || !risks) {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center">
        <p className="text-gray-500 mb-4">Region not found</p>
        <button
          onClick={() => navigate('/')}
          className="text-blue-600 hover:underline"
        >
          Return to Dashboard
        </button>
      </div>
    );
  }

  const compositeRisk = risks.composite_risk;

  // Prepare chart data
  const trendData =
    risks.risk_trend?.map((point) => ({
      date: format(new Date(point.date), 'MMM d'),
      value: point.vital_risk_index,
      level: point.risk_level,
    })) || [];

  const diseaseData = risks.disease_risks.map((dr) => ({
    name: DISEASE_LABELS[dr.disease_type] || dr.disease_type,
    score: dr.risk_score,
    color: getDiseaseColor(dr.disease_type),
  }));

  const indexBreakdown = [
    {
      name: 'Hunger Stress',
      value: compositeRisk.hunger_stress_index,
      icon: Utensils,
    },
    {
      name: 'Health Strain',
      value: compositeRisk.health_system_strain_index,
      icon: Building2,
    },
    {
      name: 'Disease Outbreak',
      value: compositeRisk.disease_outbreak_index,
      icon: Activity,
    },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
          <button
            onClick={() => navigate('/')}
            className="flex items-center text-gray-600 hover:text-gray-900 mb-4"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Dashboard
          </button>

          <div className="flex items-start justify-between">
            <div>
              <div className="flex items-center space-x-3">
                <h1 className="text-2xl font-bold text-gray-900">
                  {region.name}
                </h1>
                <RiskBadge level={region.current_risk_level as RiskLevel} />
              </div>
              <div className="flex items-center space-x-4 mt-2 text-sm text-gray-500">
                <span className="flex items-center">
                  <MapPin className="w-4 h-4 mr-1" />
                  {region.continent} • {region.level}
                </span>
                {region.population && (
                  <span className="flex items-center">
                    <Users className="w-4 h-4 mr-1" />
                    {region.population.toLocaleString()} population
                  </span>
                )}
              </div>
            </div>

            <div className="text-right">
              <p className="text-3xl font-bold" style={{
                color: RISK_COLORS[compositeRisk.risk_level as RiskLevel]
              }}>
                {formatRiskScore(compositeRisk.vital_risk_index)}
              </p>
              <p className="text-sm text-gray-500">Vital Risk Index</p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
        {/* Active Alerts Banner */}
        {region.active_alerts_count > 0 && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <div className="flex items-center">
              <AlertTriangle className="w-5 h-5 text-red-600 mr-3" />
              <p className="text-red-800">
                <span className="font-semibold">{region.active_alerts_count}</span>{' '}
                active alert(s) for this region
              </p>
              <button
                onClick={() => navigate(`/alerts?region=${code}`)}
                className="ml-auto text-red-600 hover:underline text-sm"
              >
                View Alerts
              </button>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Index Breakdown */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <h2 className="text-lg font-semibold text-gray-800 mb-4">
              Risk Index Breakdown
            </h2>

            <div className="space-y-4">
              {indexBreakdown.map((item) => {
                const Icon = item.icon;
                const level = item.value >= 80 ? 'critical' :
                              item.value >= 60 ? 'high' :
                              item.value >= 40 ? 'moderate' :
                              item.value >= 20 ? 'low' : 'minimal';

                return (
                  <div key={item.name}>
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center space-x-2">
                        <Icon className="w-4 h-4 text-gray-500" />
                        <span className="text-sm font-medium text-gray-700">
                          {item.name}
                        </span>
                      </div>
                      <span
                        className="font-semibold"
                        style={{ color: RISK_COLORS[level as RiskLevel] }}
                      >
                        {formatRiskScore(item.value)}
                      </span>
                    </div>
                    <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                      <div
                        className="h-full rounded-full transition-all"
                        style={{
                          width: `${item.value}%`,
                          backgroundColor: RISK_COLORS[level as RiskLevel],
                        }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>

            <div className="mt-4 pt-4 border-t border-gray-100 text-sm text-gray-500">
              <p>
                Confidence:{' '}
                <span className="font-medium">
                  {(compositeRisk.confidence_score * 100).toFixed(0)}%
                </span>
              </p>
              <p>
                Data Completeness:{' '}
                <span className="font-medium">
                  {(compositeRisk.data_completeness * 100).toFixed(0)}%
                </span>
              </p>
            </div>
          </div>

          {/* Risk Trend Chart */}
          <div className="lg:col-span-2 bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <h2 className="text-lg font-semibold text-gray-800 mb-4">
              Risk Trend (7 Days)
            </h2>

            {trendData.length > 0 ? (
              <div className="h-[250px]">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={trendData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                    <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                    <YAxis domain={[0, 100]} tick={{ fontSize: 12 }} />
                    <Tooltip />
                    <Line
                      type="monotone"
                      dataKey="value"
                      stroke="#3B82F6"
                      strokeWidth={2}
                      dot={{ fill: '#3B82F6' }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <p className="text-center text-gray-500 py-8">
                No trend data available
              </p>
            )}
          </div>
        </div>

        {/* Disease Risks */}
        <div className="mt-6 bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">
            Disease Risk Scores
          </h2>

          {diseaseData.length > 0 ? (
            <div className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={diseaseData} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                  <XAxis type="number" domain={[0, 100]} />
                  <YAxis type="category" dataKey="name" width={100} />
                  <Tooltip />
                  <Bar dataKey="score" radius={[0, 4, 4, 0]}>
                    {diseaseData.map((entry, index) => (
                      <Cell key={index} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <p className="text-center text-gray-500 py-8">
              No disease risk data available
            </p>
          )}

          {/* Disease Details */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mt-6">
            {risks.disease_risks.map((dr) => (
              <div
                key={dr.disease_type}
                className="p-3 rounded-lg border"
                style={{
                  borderColor: getDiseaseColor(dr.disease_type),
                  backgroundColor: `${getDiseaseColor(dr.disease_type)}10`,
                }}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium">
                    {DISEASE_LABELS[dr.disease_type] || dr.disease_type}
                  </span>
                  <span
                    className="text-lg font-bold"
                    style={{ color: getDiseaseColor(dr.disease_type) }}
                  >
                    {formatRiskScore(dr.risk_score)}
                  </span>
                </div>
                <div className="text-xs text-gray-600 space-y-1">
                  {dr.is_high_season && (
                    <p className="text-amber-600">High Season</p>
                  )}
                  {dr.trend_direction && (
                    <p>
                      Trend:{' '}
                      <span className="capitalize">{dr.trend_direction}</span>
                    </p>
                  )}
                  <p>
                    Confidence: {(dr.confidence_score * 100).toFixed(0)}%
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}
