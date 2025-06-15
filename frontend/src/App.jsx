import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Layout from './components/Layout';
import Hero from './components/Hero';
import MapPanel from './components/MapPanel';
import ChartPanel from './components/ChartPanel';
import ControlBar from './components/ControlBar';
import Loader from './components/Loader';
import useFetch from './hooks/useFetch';

function App() {
  const [showHero, setShowHero] = useState(true);
  const [analysisConfig, setAnalysisConfig] = useState({
    aoi: 'amazon',
    dateRange: {
      start: new Date(Date.now() - 365 * 24 * 60 * 60 * 1000),
      end: new Date(),
    },
    features: {
      deforestation: true,
      heatIslands: true,
      vegetation: true,
    },
  });

  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResults, setAnalysisResults] = useState(null);

  const { fetchData } = useFetch();

  const handleRunAnalysis = async () => {
    setShowHero(false);
    setIsAnalyzing(true);

    try {
      // Simulate API calls to backend
      const results = await fetchData('/api/analyze', {
        method: 'POST',
        body: JSON.stringify(analysisConfig),
      });

      setAnalysisResults(results);
    } catch (error) {
      console.error('Analysis failed:', error);
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-600">
      <AnimatePresence mode="wait">
        {showHero ? (
          <Hero key="hero" onStart={() => handleRunAnalysis()} />
        ) : (
          <Layout key="main">
            <div className="grid grid-cols-1 lg:grid-cols-[300px_1fr] gap-6 p-6">
              {/* Control Sidebar */}
              <motion.div
                initial={{ x: -300, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                transition={{ duration: 0.5 }}
              >
                <ControlBar
                  config={analysisConfig}
                  onChange={setAnalysisConfig}
                  onRun={handleRunAnalysis}
                  isAnalyzing={isAnalyzing}
                />
              </motion.div>

              {/* Main Content */}
              <div className="space-y-6">
                {isAnalyzing ? (
                  <Loader />
                ) : (
                  <>
                    <motion.div
                      initial={{ y: 20, opacity: 0 }}
                      animate={{ y: 0, opacity: 1 }}
                      transition={{ delay: 0.2 }}
                    >
                      <MapPanel
                        results={analysisResults}
                        config={analysisConfig}
                      />
                    </motion.div>

                    <motion.div
                      initial={{ y: 20, opacity: 0 }}
                      animate={{ y: 0, opacity: 1 }}
                      transition={{ delay: 0.4 }}
                    >
                      <ChartPanel
                        results={analysisResults}
                        config={analysisConfig}
                      />
                    </motion.div>
                  </>
                )}
              </div>
            </div>
          </Layout>
        )}
      </AnimatePresence>
    </div>
  );
}

export default App;
