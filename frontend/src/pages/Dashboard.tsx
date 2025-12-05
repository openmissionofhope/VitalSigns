import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { RefreshCw, AlertCircle } from 'lucide-react';

import { GlobalMap } from '../components/GlobalMap';
import { RiskSummaryCard } from '../components/RiskSummaryCard';
import { TopRiskRegions } from '../components/TopRiskRegions';
import { DiseaseHotspots } from '../components/DiseaseHotspots';
import { AlertCard } from '../components/AlertCard';

import { useRiskMap, useRiskSummary } from '../hooks/useRisks';
import { useActiveAlerts } from '../hooks/useAlerts';

export function Dashboard() {
  const navigate = useNavigate();
  const [mapLevel] = useState('country');

  const { data: mapData, isLoading: mapLoading, refetch: refetchMap } = useRiskMap(mapLevel);
  const { data: summary, isLoading: summaryLoading } = useRiskSummary(undefined, mapLevel);
  const { data: alertsData, isLoading: alertsLoading } = useActiveAlerts('warning', 5);

  const handleRegionClick = (regionCode: string) => {
    navigate(`/regions/${regionCode}`);
  };

  const handleAlertClick = (alertId: number) => {
    navigate(`/alerts/${alertId}`);
  };

  const isLoading = mapLoading || summaryLoading || alertsLoading;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">VitalSigns</h1>
              <p className="text-sm text-gray-500">
                Global Health Early Warning Dashboard
              </p>
            </div>
            <button
              onClick={() => refetchMap()}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              disabled={isLoading}
            >
              <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
              <span>Refresh</span>
            </button>
          </div>
        </div>
      </header>

      {/* Disclaimer Banner */}
      <div className="bg-amber-50 border-b border-amber-200">
        <div className="max-w-7xl mx-auto px-4 py-2 sm:px-6 lg:px-8">
          <div className="flex items-center text-sm text-amber-800">
            <AlertCircle className="w-4 h-4 mr-2 flex-shrink-0" />
            <span>
              VitalSigns provides informational risk indicators only. It does not
              provide medical advice and should not replace professional health
              assessments.
            </span>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Map - Takes up 2 columns on large screens */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
              <h2 className="text-lg font-semibold text-gray-800 mb-4">
                Global Risk Map
              </h2>
              <div className="h-[500px]">
                {mapData ? (
                  <GlobalMap
                    regions={mapData.regions}
                    onRegionClick={handleRegionClick}
                  />
                ) : (
                  <div className="h-full flex items-center justify-center bg-gray-100 rounded-lg">
                    <p className="text-gray-500">Loading map data...</p>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Sidebar - Risk Summary and Alerts */}
          <div className="space-y-6">
            {/* Risk Summary */}
            {summary && <RiskSummaryCard summary={summary} />}

            {/* Active Alerts */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-800">
                  Active Alerts
                </h3>
                {alertsData && (
                  <span className="px-2 py-1 bg-red-100 text-red-800 text-xs font-medium rounded-full">
                    {alertsData.active_count}
                  </span>
                )}
              </div>

              <div className="space-y-3">
                {alertsData?.alerts.slice(0, 3).map((alert) => (
                  <AlertCard
                    key={alert.id}
                    alert={alert}
                    onClick={() => handleAlertClick(alert.id)}
                  />
                ))}

                {alertsData?.alerts.length === 0 && (
                  <p className="text-center text-gray-500 py-4">
                    No active alerts
                  </p>
                )}
              </div>

              {alertsData && alertsData.active_count > 3 && (
                <button
                  className="w-full mt-4 px-4 py-2 text-blue-600 text-sm font-medium hover:bg-blue-50 rounded-lg transition-colors"
                  onClick={() => navigate('/alerts')}
                >
                  View All Alerts ({alertsData.active_count})
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Bottom Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
          {/* Top Risk Regions */}
          {summary && (
            <TopRiskRegions
              regions={summary.top_risk_regions}
              onRegionClick={handleRegionClick}
            />
          )}

          {/* Disease Hotspots */}
          {summary && (
            <DiseaseHotspots
              hotspots={summary.disease_hotspots}
              onRegionClick={handleRegionClick}
            />
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-8">
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
          <p className="text-center text-sm text-gray-500">
            VitalSigns - Humanitarian Early Warning System | All data is aggregated
            and privacy-preserving
          </p>
        </div>
      </footer>
    </div>
  );
}
