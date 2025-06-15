import React from 'react';
import { motion } from 'framer-motion';

const Loader = () => {
  const containerVariants = {
    start: {
      transition: {
        staggerChildren: 0.2,
      },
    },
    end: {
      transition: {
        staggerChildren: 0.2,
      },
    },
  };

  const circleVariants = {
    start: {
      y: '0%',
    },
    end: {
      y: '100%',
    },
  };

  const circleTransition = {
    duration: 0.5,
    yoyo: Infinity,
    ease: 'easeInOut',
  };

  return (
    <div className="flex items-center justify-center min-h-[400px]">
      <div className="glass-card p-12 text-center">
        <motion.div
          className="flex space-x-2 justify-center mb-6"
          variants={containerVariants}
          initial="start"
          animate="end"
        >
          {[0, 1, 2].map((index) => (
            <motion.span
              key={index}
              className="block w-4 h-4 bg-white rounded-full"
              variants={circleVariants}
              transition={circleTransition}
            />
          ))}
        </motion.div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
        >
          <h3 className="text-xl font-semibold text-white mb-2">
            Analyzing Satellite Data
          </h3>
          <p className="text-white/60 text-sm">
            Processing imagery with AI models...
          </p>
        </motion.div>

        {/* Progress Steps */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1 }}
          className="mt-8 space-y-3"
        >
          <LoadingStep text="Fetching satellite imagery" delay={0} />
          <LoadingStep text="Running deforestation detection" delay={0.5} />
          <LoadingStep text="Analyzing heat patterns" delay={1} />
          <LoadingStep text="Computing vegetation indices" delay={1.5} />
        </motion.div>
      </div>
    </div>
  );
};

const LoadingStep = ({ text, delay }) => {
  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay }}
      className="flex items-center space-x-3 text-left"
    >
      <motion.div
        animate={{ rotate: 360 }}
        transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
        className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full"
      />
      <span className="text-white/80 text-sm">{text}</span>
    </motion.div>
  );
};

export default Loader;
