import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';

const ChartPanel = ({ results, config }) => {
  const [activeTab, setActiveTab] = useState('deforestation');

  // Mock data - replace with actual results
  const deforestationData = [
    { date: '2023-01', forestCover: 95 },
    { date: '2023-03', forestCover: 94.5 },
    { date: '2023-05', forestCover: 93.8 },
    { date: '2023-07', forestCover: 93.2 },
    { date: '2023-09', forestCover: 92.5 },
    { date: '2023-11', forestCover: 91.8 },
    { date: '2024-01', forestCover: 91.2 },
  ];

  const ndviData = [
    { date: '2023-01', ndvi: 0.82 },
    { date: '2023-03', ndvi: 0.8 },
    { date: '2023-05', ndvi: 0.78 },
    { date: '2023-07', ndvi: 0.75 },
    { date: '2023-09', ndvi: 0.73 },
    { date: '2023-11', ndvi: 0.71 },
    { date: '2024-01', ndvi: 0.69 },
  ];

  const temperatureData = [
    { range: '25-28°C', count: 15 },
    { range: '28-31°C', count: 25 },
    { range: '31-34°C', count: 35 },
    { range: '34-37°C', count: 20 },
    { range: '37-40°C', count: 10 },
    { range: '>40°C', count: 5 },
  ];

  const riskData = [
    { name: 'Low Risk', value: 30, color: '#10B981' },
    { name: 'Medium Risk', value: 45, color: '#F59E0B' },
    { name: 'High Risk', value: 25, color: '#EF4444' },
  ];

  const tabs = [
    { id: 'deforestation', name: 'Deforestation', icon: '🌳' },
    { id: 'vegetation', name: 'Vegetation', icon: '🌱' },
    { id: 'temperature', name: 'Temperature', icon: '🌡️' },
    { id: 'risk', name: 'Risk Score', icon: '⚠️' },
  ];

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="glass p-3 rounded-lg">
          <p className="text-white font-semibold">{label}</p>
          {payload.map((entry, index) => (
            <p key={index} className="text-white/80 text-sm">
              {entry.name}: {entry.value.toFixed(2)}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="glass p-6">
      <h2 className="text-2xl font-bold text-white mb-4 font-poppins">
        Analysis Results
      </h2>

      {/* Tab Navigation */}
      <div className="flex space-x-2 mb-6">
        {tabs.map((tab) => (
          <motion.button
            key={tab.id}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => setActiveTab(tab.id)}
            className={`glass-button text-sm flex items-center space-x-1 ${
              activeTab === tab.id ? 'bg-white/30' : ''
            }`}
          >
            <span>{tab.icon}</span>
            <span className="text-white">{tab.name}</span>
          </motion.button>
        ))}
      </div>

      {/* Chart Content */}
      <motion.div
        key={activeTab}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        className="h-[400px]"
      >
        {activeTab === 'deforestation' && (
          <div>
            <h3 className="text-white/80 text-lg mb-4">
              Forest Cover Over Time
            </h3>
            <ResponsiveContainer width="100%" height={350}>
              <AreaChart data={deforestationData}>
                <defs>
                  <linearGradient
                    id="forestGradient"
                    x1="0"
                    y1="0"
                    x2="0"
                    y2="1"
                  >
                    <stop offset="5%" stopColor="#10B981" stopOpacity={0.8} />
                    <stop offset="95%" stopColor="#10B981" stopOpacity={0.1} />
                  </linearGradient>
                </defs>
                <CartesianGrid
                  strokeDasharray="3 3"
                  stroke="rgba(255,255,255,0.1)"
                />
                <XAxis dataKey="date" stroke="rgba(255,255,255,0.5)" />
                <YAxis stroke="rgba(255,255,255,0.5)" />
                <Tooltip content={<CustomTooltip />} />
                <Area
                  type="monotone"
                  dataKey="forestCover"
                  stroke="#10B981"
                  fillOpacity={1}
                  fill="url(#forestGradient)"
                  strokeWidth={2}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        )}

        {activeTab === 'vegetation' && (
          <div>
            <h3 className="text-white/80 text-lg mb-4">NDVI Trend Analysis</h3>
            <ResponsiveContainer width="100%" height={350}>
              <LineChart data={ndviData}>
                <CartesianGrid
                  strokeDasharray="3 3"
                  stroke="rgba(255,255,255,0.1)"
                />
                <XAxis dataKey="date" stroke="rgba(255,255,255,0.5)" />
                <YAxis stroke="rgba(255,255,255,0.5)" />
                <Tooltip content={<CustomTooltip />} />
                <Line
                  type="monotone"
                  dataKey="ndvi"
                  stroke="#22D3EE"
                  strokeWidth={3}
                  dot={{ fill: '#22D3EE', r: 4 }}
                  activeDot={{ r: 6 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}

        {activeTab === 'temperature' && (
          <div>
            <h3 className="text-white/80 text-lg mb-4">
              Temperature Distribution
            </h3>
            <ResponsiveContainer width="100%" height={350}>
              <BarChart data={temperatureData}>
                <CartesianGrid
                  strokeDasharray="3 3"
                  stroke="rgba(255,255,255,0.1)"
                />
                <XAxis dataKey="range" stroke="rgba(255,255,255,0.5)" />
                <YAxis stroke="rgba(255,255,255,0.5)" />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="count" fill="#F59E0B" radius={[8, 8, 0, 0]}>
                  {temperatureData.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={
                        index < 2
                          ? '#10B981'
                          : index < 4
                          ? '#F59E0B'
                          : '#EF4444'
                      }
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}

        {activeTab === 'risk' && (
          <div>
            <h3 className="text-white/80 text-lg mb-4">
              Environmental Risk Assessment
            </h3>
            <div className="grid grid-cols-2 gap-4">
              <ResponsiveContainer width="100%" height={350}>
                <PieChart>
                  <Pie
                    data={riskData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={120}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {riskData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip content={<CustomTooltip />} />
                </PieChart>
              </ResponsiveContainer>

              <div className="flex flex-col justify-center space-y-4">
                {riskData.map((item) => (
                  <div key={item.name} className="glass-card">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-white font-medium">
                        {item.name}
                      </span>
                      <span className="text-white/80">{item.value}%</span>
                    </div>
                    <div className="w-full bg-white/20 rounded-full h-2">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${item.value}%` }}
                        transition={{ duration: 1, delay: 0.2 }}
                        className="h-full rounded-full"
                        style={{ backgroundColor: item.color }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </motion.div>

      {/* Analysis Summary */}
      {results && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="mt-6 pt-6 border-t border-white/20"
        >
          <div className="grid grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-3xl font-bold text-white">
                {results?.deforestationRate || '3.8'}%
              </div>
              <div className="text-white/60 text-sm">Deforestation Rate</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-white">
                {results?.heatIslands || '5'}
              </div>
              <div className="text-white/60 text-sm">Heat Islands</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-white">
                {results?.ndviChange || '-0.13'}
              </div>
              <div className="text-white/60 text-sm">NDVI Change</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-white">
                {results?.confidence || '94'}%
              </div>
              <div className="text-white/60 text-sm">Confidence</div>
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
};

export default ChartPanel;
