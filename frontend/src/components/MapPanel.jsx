import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Polygon, Popup } from 'react-leaflet';
import { motion, AnimatePresence } from 'framer-motion';
import 'leaflet/dist/leaflet.css';

const MapPanel = ({ results, config }) => {
  const [activeLayer, setActiveLayer] = useState('satellite');

  const areaCoordinates = {
    amazon: {
      center: [-10, -63],
      zoom: 9,
      polygon: [
        [-10.5, -63.5],
        [-10.5, -62.5],
        [-9.5, -62.5],
        [-9.5, -63.5],
      ],
    },
    jakarta: {
      center: [-6.2, 106.8],
      zoom: 11,
      polygon: [
        [-6.4, 106.7],
        [-6.4, 107.0],
        [-6.1, 107.0],
        [-6.1, 106.7],
      ],
    },
    california: {
      center: [37.5, -121],
      zoom: 9,
      polygon: [
        [38.0, -121.5],
        [38.0, -120.5],
        [37.0, -120.5],
        [37.0, -121.5],
      ],
    },
  };

  const currentArea = areaCoordinates[config.aoi] || areaCoordinates.amazon;

  const layers = [
    { id: 'satellite', name: 'Satellite', icon: '🛰️' },
    { id: 'ndvi', name: 'NDVI', icon: '🌱' },
    { id: 'temperature', name: 'Temperature', icon: '🌡️' },
    { id: 'deforestation', name: 'Deforestation', icon: '🌳' },
  ];

  return (
    <div className="glass p-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-bold text-white font-poppins">
          Interactive Analysis Map
        </h2>

        {/* Layer Toggle */}
        <div className="flex space-x-2">
          {layers.map((layer) => (
            <motion.button
              key={layer.id}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setActiveLayer(layer.id)}
              className={`glass-button text-sm flex items-center space-x-1 ${
                activeLayer === layer.id ? 'bg-white/30' : ''
              }`}
            >
              <span>{layer.icon}</span>
              <span className="text-white">{layer.name}</span>
            </motion.button>
          ))}
        </div>
      </div>

      <div className="relative h-[500px] rounded-lg overflow-hidden">
        <MapContainer
          center={currentArea.center}
          zoom={currentArea.zoom}
          className="h-full w-full"
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          {/* Area of Interest Polygon */}
          <Polygon
            positions={currentArea.polygon}
            pathOptions={{
              color: '#4F46E5',
              weight: 2,
              opacity: 0.8,
              fillOpacity: 0.1,
            }}
          >
            <Popup>
              <div className="text-sm">
                <strong>Analysis Area</strong>
                <br />
                {config.aoi.charAt(0).toUpperCase() + config.aoi.slice(1)}
              </div>
            </Popup>
          </Polygon>

          {/* Analysis Results Overlays */}
          <AnimatePresence>
            {results &&
              activeLayer === 'deforestation' &&
              results.deforestation && (
                <Polygon
                  positions={results.deforestation.coordinates}
                  pathOptions={{
                    color: '#EF4444',
                    weight: 2,
                    opacity: 0.8,
                    fillOpacity: 0.5,
                  }}
                >
                  <Popup>
                    <div className="text-sm">
                      <strong>Deforestation Detected</strong>
                      <br />
                      Area: {results.deforestation.area} hectares
                    </div>
                  </Popup>
                </Polygon>
              )}
          </AnimatePresence>
        </MapContainer>

        {/* Map Legend */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="absolute bottom-4 left-4 glass p-4 rounded-lg"
        >
          <h4 className="text-white font-semibold mb-2">Legend</h4>
          <div className="space-y-1 text-sm">
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 bg-indigo-500 rounded"></div>
              <span className="text-white/80">Analysis Area</span>
            </div>
            {activeLayer === 'deforestation' && (
              <div className="flex items-center space-x-2">
                <div className="w-4 h-4 bg-red-500 rounded"></div>
                <span className="text-white/80">Deforestation</span>
              </div>
            )}
            {activeLayer === 'temperature' && (
              <div className="flex items-center space-x-2">
                <div className="w-4 h-4 bg-orange-500 rounded"></div>
                <span className="text-white/80">Heat Islands</span>
              </div>
            )}
          </div>
        </motion.div>

        {/* Analysis Stats Overlay */}
        {results && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="absolute top-4 right-4 glass p-4 rounded-lg"
          >
            <div className="text-white text-sm space-y-1">
              <div>
                <span className="font-semibold">Images Analyzed:</span>{' '}
                {results.imageCount || 12}
              </div>
              <div>
                <span className="font-semibold">Cloud Cover:</span>{' '}
                {results.cloudCover || 15}%
              </div>
              <div>
                <span className="font-semibold">Processing Time:</span>{' '}
                {results.processingTime || '2.3'}s
              </div>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
};

export default MapPanel;
