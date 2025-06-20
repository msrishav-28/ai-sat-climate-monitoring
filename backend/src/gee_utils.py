"""
Google Earth Engine utilities for satellite image analysis
"""

import ee
import streamlit as st
import os
from datetime import datetime
import json
import numpy as np
import pandas as pd

from .config import (
    SENTINEL2_COLLECTION, LANDSAT8_COLLECTION,
    S2_BANDS, L8_BANDS, S2_CLOUD_BIT, S2_CIRRUS_BIT,
    L8_CLOUD_BIT, L8_CLOUD_SHADOW_BIT, SCALE, BUFFER_SIZE,
    NDVI_VIS_PARAMS, LST_VIS_PARAMS
)


def initialize_earth_engine():
    """Initialize Earth Engine with multiple authentication methods"""
    try:
        # Method 1: Try environment variable first
        if os.getenv('GEE_SERVICE_ACCOUNT') and os.getenv('GEE_PRIVATE_KEY'):
            service_account = os.getenv('GEE_SERVICE_ACCOUNT')
            private_key = os.getenv('GEE_PRIVATE_KEY')
            
            credentials = ee.ServiceAccountCredentials(
                service_account, 
                key_data=private_key
            )
            ee.Initialize(credentials)
            print("Earth Engine initialized with environment variables")
            return
            
        # Method 2: Try Streamlit secrets
        if hasattr(st, 'secrets') and 'gee' in st.secrets:
            service_account = st.secrets["gee"]["service_account"]
            private_key = st.secrets["gee"]["private_key"]
            
            credentials = ee.ServiceAccountCredentials(
                service_account, 
                key_data=private_key
            )
            ee.Initialize(credentials)
            print("Earth Engine initialized with Streamlit secrets")
            return
            
        # Method 3: Try local authentication
        try:
            ee.Initialize()
            print("Earth Engine initialized with default credentials")
            return
        except:
            # Method 4: Authenticate interactively
            print("No credentials found. Authenticating...")
            ee.Authenticate()
            ee.Initialize()
            print("Earth Engine authenticated and initialized successfully")
            
    except Exception as e:
        st.error(f"Failed to initialize Earth Engine: {str(e)}")
        st.info("""
        To fix this:
        1. Run 'earthengine authenticate' in your terminal
        2. Or set up service account credentials in .streamlit/secrets.toml
        3. Or set GEE_SERVICE_ACCOUNT and GEE_PRIVATE_KEY environment variables
        """)
        raise e


def get_aoi_geometry(coordinates):
    """Convert coordinate list to Earth Engine geometry"""
    return ee.Geometry.Polygon([coordinates])


def mask_s2_clouds(image):
    """Mask clouds in Sentinel-2 imagery"""
    qa = image.select('QA60')
    
    # Bits 10 and 11 are clouds and cirrus
    cloud_bit_mask = 1 << S2_CLOUD_BIT
    cirrus_bit_mask = 1 << S2_CIRRUS_BIT
    
    # Both flags should be set to zero, indicating clear conditions
    mask = qa.bitwiseAnd(cloud_bit_mask).eq(0).And(
        qa.bitwiseAnd(cirrus_bit_mask).eq(0)
    )
    
    return image.updateMask(mask).divide(10000)


def mask_l8_clouds(image):
    """Mask clouds in Landsat 8 imagery"""
    qa = image.select('QA_PIXEL')
    
    # Bits 3 and 4 are cloud and cloud shadow
    cloud_bit_mask = 1 << L8_CLOUD_BIT
    cloud_shadow_bit_mask = 1 << L8_CLOUD_SHADOW_BIT
    
    # Both flags should be set to zero
    mask = qa.bitwiseAnd(cloud_bit_mask).eq(0).And(
        qa.bitwiseAnd(cloud_shadow_bit_mask).eq(0)
    )
    
    return image.updateMask(mask)


def add_ndvi_s2(image):
    """Add NDVI band to Sentinel-2 image"""
    ndvi = image.normalizedDifference([S2_BANDS['nir'], S2_BANDS['red']]).rename('NDVI')
    return image.addBands(ndvi)


def add_ndvi_l8(image):
    """Add NDVI band to Landsat 8 image"""
    ndvi = image.normalizedDifference([L8_BANDS['nir'], L8_BANDS['red']]).rename('NDVI')
    return image.addBands(ndvi)


def get_image_collection(aoi, start_date, end_date, sensor='S2', max_cloud=20):
    """Get filtered image collection for the AOI"""
    if sensor == 'S2':
        collection = ee.ImageCollection(SENTINEL2_COLLECTION) \
            .filterBounds(aoi) \
            .filterDate(start_date, end_date) \
            .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', max_cloud)) \
            .map(mask_s2_clouds) \
            .map(add_ndvi_s2)
    else:  # L8
        collection = ee.ImageCollection(LANDSAT8_COLLECTION) \
            .filterBounds(aoi) \
            .filterDate(start_date, end_date) \
            .filter(ee.Filter.lt('CLOUD_COVER', max_cloud)) \
            .map(mask_l8_clouds) \
            .map(add_ndvi_l8)
    
    return collection


def get_composite_image(collection):
    """Create a median composite from image collection"""
    return collection.median()


def compute_ndvi_trend(aoi, start_date, end_date):
    """Compute NDVI trend over time"""
    collection = get_image_collection(aoi, start_date, end_date, 'S2')
    
    # Add time band
    def add_time(image):
        time = ee.Image(image.date().millis()).divide(1e9)  # Convert to seconds
        return image.addBands(time.rename('time').float())
    
    collection_with_time = collection.map(add_time)
    
    # Linear regression
    linear_fit = collection_with_time.select(['time', 'NDVI']) \
        .reduce(ee.Reducer.linearFit())
    
    return linear_fit


def detect_deforestation(aoi, baseline_start, baseline_end, current_start, current_end):
    """Detect deforestation by comparing baseline and current NDVI"""
    # Get baseline NDVI
    baseline_collection = get_image_collection(aoi, baseline_start, baseline_end, 'S2')
    baseline_ndvi = baseline_collection.select('NDVI').mean()
    
    # Get current NDVI
    current_collection = get_image_collection(aoi, current_start, current_end, 'S2')
    current_ndvi = current_collection.select('NDVI').mean()
    
    # Calculate change
    ndvi_change = current_ndvi.subtract(baseline_ndvi)
    
    # Threshold for deforestation (significant negative change)
    deforestation_mask = ndvi_change.lt(-0.2)
    
    return deforestation_mask


def identify_heat_islands(aoi, start_date, end_date):
    """Identify urban heat islands using Landsat 8 thermal data"""
    collection = get_image_collection(aoi, start_date, end_date, 'L8')
    
    # Get thermal band
    thermal = collection.select(L8_BANDS['thermal'])
    
    # Convert to Celsius
    lst_celsius = thermal.map(lambda image: 
        image.multiply(0.00341802).add(149.0).subtract(273.15)
    )
    
    # Get mean temperature
    mean_lst = lst_celsius.mean()
    
    # Identify heat islands (areas significantly warmer than mean)
    threshold = mean_lst.add(3)  # 3°C above mean
    heat_islands = mean_lst.gt(threshold)
    
    return heat_islands


def export_to_geojson(feature_collection):
    """Export Earth Engine feature collection to GeoJSON"""
    # This is a placeholder - actual export would require more setup
    return {
        "type": "FeatureCollection",
        "features": []
    }


def get_time_series_data(aoi, start_date, end_date, sensor='S2', index='NDVI'):
    """Extract time series data for the AOI"""
    collection = get_image_collection(aoi, start_date, end_date, sensor)
    
    # Define a function to extract mean values
    def extract_mean(image):
        mean_dict = image.select(index).reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=aoi,
            scale=SCALE,
            maxPixels=1e9
        )
        return ee.Feature(None, {
            'date': image.date().millis(),
            index: mean_dict.get(index)
        })
    
    # Map over collection
    features = collection.map(extract_mean)
    
    # Convert to pandas DataFrame (simplified for demo)
    # In production, you'd use ee.batch.Export or getInfo() carefully
    dates = pd.date_range(start_date, end_date, periods=10)
    values = np.random.uniform(0.3, 0.8, 10)  # Mock data for demo
    
    return pd.DataFrame({
        'date': dates,
        index: values
    })


def get_area_statistics(mask, aoi):
    """Calculate area statistics for a binary mask"""
    # Calculate pixel area
    pixel_area = ee.Image.pixelArea()
    
    # Mask the pixel area image
    area_image = pixel_area.updateMask(mask)
    
    # Sum the areas
    stats = area_image.reduceRegion(
        reducer=ee.Reducer.sum(),
        geometry=aoi,
        scale=SCALE,
        maxPixels=1e9
    )
    
    # Convert to hectares (mock for demo)
    return {
        'area_hectares': {
            'total': 10000,
            'affected': 250
        }
    }


def get_map_tiles(image, vis_params):
    """Get map tile URL for visualization"""
    # This would normally return a tile URL from Earth Engine
    # For demo, return a placeholder
    return {
        'url': 'https://earthengine.googleapis.com/map/{z}/{x}/{y}',
        'attribution': 'Google Earth Engine'
    }