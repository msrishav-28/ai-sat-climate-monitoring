import React from 'react';
import { motion } from 'framer-motion';

const ControlBar = ({ config, onChange, onRun, isAnalyzing }) => {
  const areas = [
    { id: 'amazon', name: 'Amazon Rainforest', icon: '🌳' },
    { id: 'jakarta', name: 'Jakarta Metropolitan', icon: '🏙️' },
    { id: 'california', name: 'California Valley', icon: '🌾' },
  ];

  const updateConfig = (key, value) => {
    onChange({
      ...config,
      [key]: value,
    });
  };

  const updateFeature = (feature, enabled) => {
    onChange({
      ...config,
      features: {
        ...config.features,
        [feature]: enabled,
      },
    });
  };

  return (
    <div className="glass p-6 h-fit">
      <h2 className="text-2xl font-bold text-white mb-6 font-poppins">
        Analysis Controls
      </h2>

      {/* Area Selection */}
      <div className="mb-6">
        <label className="block text-white/80 text-sm font-medium mb-3">
          Select Area
        </label>
        <div className="space-y-2">
          {areas.map((area) => (
            <motion.button
              key={area.id}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => updateConfig('aoi', area.id)}
              className={`w-full glass-button text-left flex items-center space-x-3 ${
                config.aoi === area.id ? 'bg-white/30' : ''
              }`}
            >
              <span className="text-2xl">{area.icon}</span>
              <span className="text-white">{area.name}</span>
            </motion.button>
          ))}
        </div>
      </div>

      {/* Date Range */}
      <div className="mb-6">
        <label className="block text-white/80 text-sm font-medium mb-3">
          Date Range
        </label>
        <div className="space-y-3">
          <div>
            <label className="text-white/60 text-xs">Start Date</label>
            <input
              type="date"
              value={config.dateRange.start.toISOString().split('T')[0]}
              onChange={(e) =>
                updateConfig('dateRange', {
                  ...config.dateRange,
                  start: new Date(e.target.value),
                })
              }
              className="glass-input w-full"
            />
          </div>
          <div>
            <label className="text-white/60 text-xs">End Date</label>
            <input
              type="date"
              value={config.dateRange.end.toISOString().split('T')[0]}
              onChange={(e) =>
                updateConfig('dateRange', {
                  ...config.dateRange,
                  end: new Date(e.target.value),
                })
              }
              className="glass-input w-full"
            />
          </div>
        </div>
      </div>

      {/* Features Toggle */}
      <div className="mb-6">
        <label className="block text-white/80 text-sm font-medium mb-3">
          Analysis Features
        </label>
        <div className="space-y-3">
          <FeatureToggle
            label="Deforestation Detection"
            icon="🌳"
            enabled={config.features.deforestation}
            onChange={(enabled) => updateFeature('deforestation', enabled)}
          />
          <FeatureToggle
            label="Urban Heat Islands"
            icon="🏙️"
            enabled={config.features.heatIslands}
            onChange={(enabled) => updateFeature('heatIslands', enabled)}
          />
          <FeatureToggle
            label="Vegetation Trends"
            icon="🌱"
            enabled={config.features.vegetation}
            onChange={(enabled) => updateFeature('vegetation', enabled)}
          />
        </div>
      </div>

      {/* Run Button */}
      <motion.button
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        onClick={onRun}
        disabled={isAnalyzing}
        className="w-full glass-button bg-gradient-to-r from-indigo-500 to-purple-600 text-white font-semibold py-3"
      >
        {isAnalyzing ? (
          <span className="flex items-center justify-center">
            <svg className="animate-spin h-5 w-5 mr-3" viewBox="0 0 24 24">
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
                fill="none"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
            Analyzing...
          </span>
        ) : (
          '🚀 Run Analysis'
        )}
      </motion.button>
    </div>
  );
};

const FeatureToggle = ({ label, icon, enabled, onChange }) => {
  return (
    <div className="flex items-center justify-between">
      <div className="flex items-center space-x-2">
        <span className="text-xl">{icon}</span>
        <span className="text-white/80 text-sm">{label}</span>
      </div>
      <button
        onClick={() => onChange(!enabled)}
        className={`${
          enabled ? 'bg-indigo-600' : 'bg-white/20'
        } relative inline-flex h-6 w-11 items-center rounded-full transition-colors`}
      >
        <span
          className={`${
            enabled ? 'translate-x-6' : 'translate-x-1'
          } inline-block h-4 w-4 transform rounded-full bg-white transition-transform`}
        />
      </button>
    </div>
  );
};

export default ControlBar;
