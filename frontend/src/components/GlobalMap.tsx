import { useEffect, useState } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup, useMap } from 'react-leaflet';
import type { MapRegion } from '../types';
import { getRiskColor, getMarkerSize, formatRiskScore, getRiskLabel } from '../utils/risk';
import { RiskBadge } from './RiskBadge';

interface GlobalMapProps {
  regions: MapRegion[];
  onRegionClick?: (regionCode: string) => void;
  center?: [number, number];
  zoom?: number;
}

function MapController({ center, zoom }: { center: [number, number]; zoom: number }) {
  const map = useMap();

  useEffect(() => {
    map.setView(center, zoom);
  }, [map, center, zoom]);

  return null;
}

export function GlobalMap({
  regions,
  onRegionClick,
  center = [10, 20],
  zoom = 2,
}: GlobalMapProps) {
  const [selectedRegion, setSelectedRegion] = useState<string | null>(null);

  const handleRegionClick = (regionCode: string) => {
    setSelectedRegion(regionCode);
    onRegionClick?.(regionCode);
  };

  return (
    <div className="h-full w-full rounded-lg overflow-hidden">
      <MapContainer
        center={center}
        zoom={zoom}
        scrollWheelZoom={true}
        className="h-full w-full"
      >
        <MapController center={center} zoom={zoom} />
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {regions.map((region) => (
          <CircleMarker
            key={region.code}
            center={[region.lat, region.lng]}
            radius={getMarkerSize(region.vital_risk_index)}
            pathOptions={{
              fillColor: getRiskColor(region.risk_level),
              color: getRiskColor(region.risk_level),
              weight: selectedRegion === region.code ? 3 : 1,
              opacity: 1,
              fillOpacity: 0.7,
            }}
            eventHandlers={{
              click: () => handleRegionClick(region.code),
            }}
          >
            <Popup>
              <div className="min-w-[200px]">
                <h3 className="font-semibold text-gray-900 mb-2">{region.name}</h3>
                <div className="mb-3">
                  <RiskBadge level={region.risk_level} />
                </div>

                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Vital Risk Index:</span>
                    <span className="font-medium">
                      {formatRiskScore(region.vital_risk_index)}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Hunger Stress:</span>
                    <span className="font-medium">
                      {formatRiskScore(region.hunger_stress)}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Health Strain:</span>
                    <span className="font-medium">
                      {formatRiskScore(region.health_strain)}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Disease Outbreak:</span>
                    <span className="font-medium">
                      {formatRiskScore(region.disease_outbreak)}
                    </span>
                  </div>
                </div>

                <button
                  className="mt-3 w-full px-3 py-1.5 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 transition-colors"
                  onClick={() => handleRegionClick(region.code)}
                >
                  View Details
                </button>
              </div>
            </Popup>
          </CircleMarker>
        ))}
      </MapContainer>
    </div>
  );
}
