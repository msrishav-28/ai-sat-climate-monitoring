"""
Configuration constants for satellite image analysis
"""

# Earth Engine Collections
SENTINEL2_COLLECTION = "COPERNICUS/S2_SR_HARMONIZED"
LANDSAT8_COLLECTION = "LANDSAT/LC08/C02/T1_L2"

# Band Names
S2_BANDS = {
    "blue": "B2",
    "green": "B3", 
    "red": "B4",
    "nir": "B8",
    "swir1": "B11",
    "swir2": "B12",
    "qa": "QA60"
}

L8_BANDS = {
    "blue": "SR_B2",
    "green": "SR_B3",
    "red": "SR_B4", 
    "nir": "SR_B5",
    "swir1": "SR_B6",
    "swir2": "SR_B7",
    "thermal": "ST_B10",
    "qa": "QA_PIXEL"
}

# Cloud Masking
S2_CLOUD_BIT = 10
S2_CIRRUS_BIT = 11
L8_CLOUD_BIT = 3
L8_CLOUD_SHADOW_BIT = 4

# Analysis Parameters
MAX_CLOUD_COVER = 20  # Maximum cloud cover percentage
BUFFER_SIZE = 10000  # Buffer around AOI in meters
SCALE = 30  # Resolution in meters for analysis

# Vegetation Indices Thresholds
NDVI_FOREST_THRESHOLD = 0.7
NDVI_VEGETATION_THRESHOLD = 0.3
NDVI_CHANGE_THRESHOLD = -0.2  # Significant negative change

# Urban Heat Island Parameters
LST_URBAN_THRESHOLD = 303  # Kelvin (~30°C)
LST_PERCENTILE = 90  # Percentile for heat island detection
MIN_HEAT_ISLAND_AREA = 10000  # Square meters

# Time Series Analysis
MIN_OBSERVATIONS = 5  # Minimum images for trend analysis
TREND_SIGNIFICANCE = 0.05  # P-value threshold

# Model Configuration
MODEL_INPUT_SIZE = (512, 512, 4)  # Height, Width, Channels
MODEL_PATH = "models/deforestation_unet.h5"
CONFIDENCE_THRESHOLD = 0.5

# Visualization
NDVI_VIS_PARAMS = {
    "min": -0.2,
    "max": 1.0,
    "palette": ["#8B0000", "#FF0000", "#FFFF00", "#00FF00", "#006400"]
}

LST_VIS_PARAMS = {
    "min": 290,
    "max": 320,
    "palette": ["#0000FF", "#00FFFF", "#00FF00", "#FFFF00", "#FF0000"]
}

DEFORESTATION_COLORS = {
    "forest": "#006400",
    "non_forest": "#8B4513",
    "deforestation": "#FF0000",
    "regrowth": "#90EE90"
}

# Export Settings
EXPORT_SCALE = 30
EXPORT_CRS = "EPSG:4326"
MAX_PIXELS = 1e9

# Cache Settings
CACHE_TTL = 3600  # 1 hour in seconds
MAX_CACHE_SIZE = 100  # Maximum cached results

# API Rate Limits
MAX_REQUESTS_PER_MINUTE = 60
MAX_AREA_SQKM = 1000  # Maximum area for single analysis

# Default Areas of Interest (for demo)
DEFAULT_AOIS = {
    "amazon": {
        "name": "Amazon Rainforest - Rondônia",
        "coordinates": [[-63.5, -10.5], [-62.5, -10.5], [-62.5, -9.5], [-63.5, -9.5]],
        "description": "Deforestation hotspot in Brazilian Amazon"
    },
    "jakarta": {
        "name": "Jakarta Metropolitan",
        "coordinates": [[106.7, -6.4], [107.0, -6.4], [107.0, -6.1], [106.7, -6.1]],
        "description": "Urban heat island in Indonesian capital"
    },
    "california": {
        "name": "California Central Valley", 
        "coordinates": [[-121.5, 38.0], [-120.5, 38.0], [-120.5, 37.0], [-121.5, 37.0]],
        "description": "Agricultural area with vegetation changes"
    }
}