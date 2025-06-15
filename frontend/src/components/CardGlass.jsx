import React from 'react';
import { motion } from 'framer-motion';

const CardGlass = ({ children, className = '', animate = true }) => {
  const baseClasses = 'glass p-4 shadow-lg';

  if (animate) {
    return (
      <motion.div
        className={`${baseClasses} ${className}`}
        whileHover={{ scale: 1.02 }}
        transition={{ type: 'spring', stiffness: 300 }}
      >
        {children}
      </motion.div>
    );
  }

  return <div className={`${baseClasses} ${className}`}>{children}</div>;
};

export default CardGlass;
