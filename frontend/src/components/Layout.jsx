import React from 'react';
import { motion } from 'framer-motion';

const Layout = ({ children }) => {
  return (
    <div className="min-h-screen">
      {/* Header */}
      <motion.header
        initial={{ y: -100 }}
        animate={{ y: 0 }}
        className="glass-dark border-b border-white/10"
      >
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <span className="text-3xl">🛰️</span>
            <h1 className="text-2xl font-bold text-white font-poppins">
              Climate Monitor
            </h1>
          </div>

          <nav className="flex items-center space-x-6">
            <button className="text-white/70 hover:text-white transition-colors">
              Dashboard
            </button>
            <button className="text-white/70 hover:text-white transition-colors">
              History
            </button>
            <button className="text-white/70 hover:text-white transition-colors">
              Settings
            </button>
            <button className="glass-button text-white">Export Results</button>
          </nav>
        </div>
      </motion.header>

      {/* Main Content */}
      <main className="relative">{children}</main>

      {/* Footer */}
      <footer className="glass-dark border-t border-white/10 mt-12">
        <div className="max-w-7xl mx-auto px-4 py-6 text-center">
          <p className="text-white/60 text-sm">
            Built with ❤️ using React, Earth Engine, and TensorFlow
          </p>
        </div>
      </footer>
    </div>
  );
};

export default Layout;
