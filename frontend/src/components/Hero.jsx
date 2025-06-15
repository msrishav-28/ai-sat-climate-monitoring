import React from 'react';
import { motion } from 'framer-motion';

const Hero = ({ onStart }) => {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="min-h-screen flex items-center justify-center p-8"
    >
      <motion.div
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.2, duration: 0.8 }}
        className="glass-card max-w-4xl w-full text-center"
      >
        <motion.div
          initial={{ scale: 0.8 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.4, type: 'spring', stiffness: 200 }}
        >
          <h1 className="text-6xl font-bold text-white mb-4 font-poppins">
            🛰️ AI Satellite Climate Monitor
          </h1>
        </motion.div>

        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
          className="text-xl text-white/80 mb-8"
        >
          Real-time analysis of deforestation, urban heat islands, and
          vegetation changes using cutting-edge AI and satellite imagery
        </motion.p>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
          className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8"
        >
          <div className="glass p-6 rounded-lg">
            <div className="text-4xl mb-3">🌳</div>
            <h3 className="text-lg font-semibold text-white mb-2">
              Deforestation Detection
            </h3>
            <p className="text-white/70 text-sm">
              AI-powered analysis using U-Net deep learning models
            </p>
          </div>

          <div className="glass p-6 rounded-lg">
            <div className="text-4xl mb-3">🏙️</div>
            <h3 className="text-lg font-semibold text-white mb-2">
              Urban Heat Islands
            </h3>
            <p className="text-white/70 text-sm">
              Identify temperature anomalies in urban areas
            </p>
          </div>

          <div className="glass p-6 rounded-lg">
            <div className="text-4xl mb-3">🌱</div>
            <h3 className="text-lg font-semibold text-white mb-2">
              Vegetation Trends
            </h3>
            <p className="text-white/70 text-sm">
              Track NDVI changes over time with trend analysis
            </p>
          </div>
        </motion.div>

        <motion.button
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1 }}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={onStart}
          className="glass-button bg-gradient-to-r from-indigo-500 to-purple-600 text-white px-8 py-4 text-lg font-semibold"
        >
          Start Analysis →
        </motion.button>
      </motion.div>
    </motion.div>
  );
};

export default Hero;
