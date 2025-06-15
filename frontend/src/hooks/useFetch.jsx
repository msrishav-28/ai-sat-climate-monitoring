import { useState, useCallback } from 'react';

const useFetch = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchData = useCallback(async (url, options = {}) => {
    setLoading(true);
    setError(null);

    try {
      // In development, simulate API responses
      if (import.meta.env.DEV) {
        // Simulate network delay
        await new Promise((resolve) => setTimeout(resolve, 2000));

        // Return mock data based on the endpoint
        if (url.includes('/api/analyze')) {
          return {
            timestamp: new Date().toISOString(),
            deforestationRate: 3.8,
            heatIslands: 5,
            ndviChange: -0.13,
            confidence: 94,
            imageCount: 12,
            cloudCover: 15,
            processingTime: '2.3',
            deforestation: {
              coordinates: [
                [-10.3, -63.2],
                [-10.3, -63.1],
                [-10.2, -63.1],
                [-10.2, -63.2],
              ],
              area: 250,
            },
          };
        }
      }

      // Actual fetch for production
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return { fetchData, loading, error };
};

export default useFetch;
