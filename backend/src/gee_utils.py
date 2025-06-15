"""
Google Earth Engine utilities for satellite data processing
"""

import ee
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import json

from src.config import (
    SENTINEL2_COLLECTION, LANDSAT8_COLLECTION,
    S2_BANDS, L8_BANDS, MAX_CLOUD_COVER,
    SCALE, NDVI_VIS_PARAMS, LST_VIS_PARAMS
)


def initialize_earth_engine():
    """Initialize Earth Engine with service account credentials"""
    try:
        # Try to use Streamlit secrets
        service_account = st.secrets["gee"]["service_account"]
        private_key = st.secrets["gee"]["private_key"]
        
        credentials = ee.ServiceAccountCredentials(
            service_account, 
            key_data=private_key
        )
        ee.Initialize(credentials)
        
    except Exception as e:
        # Fallback to default authentication
        try:
            ee.Initialize()
        except:
            st.error("Failed to initialize Earth Engine. Please check credentials.")
            raise e


def get_aoi_geometry(coordinates: List[List[float]]) -> ee.Geometry:
    """Convert coordinate list to Earth Engine geometry"""
    return ee.Geometry.Polygon(coordinates)


def mask_s2_clouds(image: ee.Image) -> ee.Image:
    """Cloud mask for Sentinel-2"""
    qa = image.select('QA60')
    
    # Bits 10 and 11 are clouds and cirrus
    cloud_bit_mask = 1 << 10
    cirrus_bit_mask = 1 << 11
    
    mask = (qa.bitwiseAnd(cloud_bit_mask).eq(0)
            .And(qa.bitwiseAnd(cirrus_bit_mask).eq(0)))
    
    return image.updateMask(mask).divide(10000)


def mask_l8_clouds(image: ee.Image) -> ee.Image:
    """Cloud mask for Landsat 8"""
    qa = image.select('QA_PIXEL')
    
    # Bits 3 and 4 are cloud and cloud shadow
    cloud_bit_mask = 1 << 3
    cloud_shadow_bit_mask = 1 << 4
    
    mask = (qa.bitwiseAnd(cloud_bit_mask).eq(0)
            .And(qa.bitwiseAnd(cloud_shadow_bit_mask).eq(0)))
    
    # Scale and apply mask
    optical_bands = image.select(['SR_B.*']).multiply(0.0000275).add(-0.2)
    thermal_bands = image.select('ST_B10').multiply(0.00341802).add(149.0)
    
    return (image.addBands(optical_bands, None, True)
            .addBands(thermal_bands, None, True)
            .updateMask(mask))


def calculate_ndvi(image: ee.Image, sensor: str = "S2") -> ee.Image:
    """Calculate NDVI for given sensor"""
    if sensor == "S2":
        nir = image.select(S2_BANDS["nir"])
        red = image.select(S2_BANDS["red"])
    else:  # L8
        nir = image.select(L8_BANDS["nir"])
        red = image.select(L8_BANDS["red"])
    
    ndvi = nir.subtract(red).divide(nir.add(red)).rename('NDVI')
    return image.addBands(ndvi)


def calculate_lst(image: ee.Image) -> ee.Image:
    """Calculate Land Surface Temperature from Landsat 8"""
    # LST is already in the thermal band after scaling
    lst = image.select('ST_B10').rename('LST')
    return image.addBands(lst)


def get_image_collection(
    aoi: ee.Geometry,
    start_date: str,
    end_date: str,
    sensor: str = "S2",
    max_cloud: float = MAX_CLOUD_COVER
) -> ee.ImageCollection:
    """Get filtered image collection for AOI and date range"""
    
    if sensor == "S2":
        collection = (ee.ImageCollection(SENTINEL2_COLLECTION)
                     .filterBounds(aoi)
                     .filterDate(start_date, end_date)
                     .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', max_cloud))
                     .map(mask_s2_clouds)
                     .map(lambda img: calculate_ndvi(img, "S2")))
    else:  # L8
        collection = (ee.ImageCollection(LANDSAT8_COLLECTION)
                     .filterBounds(aoi)
                     .filterDate(start_date, end_date)
                     .filter(ee.Filter.lt('CLOUD_COVER', max_cloud))
                     .map(mask_l8_clouds)
                     .map(lambda img: calculate_ndvi(img, "L8"))
                     .map(calculate_lst))
    
    return collection


def get_composite_image(
    collection: ee.ImageCollection,
    reducer: str = "median"
) -> ee.Image:
    """Create composite image from collection"""
    if reducer == "median":
        return collection.median()
    elif reducer == "mean":
        return collection.mean()
    elif reducer == "max":
        return collection.max()
    elif reducer == "min":
        return collection.min()
    else:
        return collection.median()


def compute_ndvi_trend(
    aoi: ee.Geometry,
    start_date: str,
    end_date: str,
    sensor: str = "S2"
) -> Dict:
    """Compute NDVI trend over time"""
    collection = get_image_collection(aoi, start_date, end_date, sensor)
    
    # Add time band for linear regression
    def add_time_band(image):
        return (image.addBands(image.metadata('system:time_start')
                .divide(1e9)  # Convert to seconds
                .divide(86400)  # Convert to days
                .divide(365.25)))  # Convert to years
    
    collection_with_time = collection.map(add_time_band)
    
    # Linear regression
    linear_fit = (collection_with_time
                 .select(['system:time_start', 'NDVI'])
                 .reduce(ee.Reducer.linearFit()))
    
    # Extract results
    scale_reducer = ee.Reducer.mean()
    stats = linear_fit.reduceRegion(
        reducer=scale_reducer,
        geometry=aoi,
        scale=SCALE,
        maxPixels=1e9
    )
    
    return stats.getInfo()


def detect_deforestation(
    aoi: ee.Geometry,
    baseline_start: str,
    baseline_end: str,
    current_start: str,
    current_end: str,
    sensor: str = "S2"
) -> ee.Image:
    """Detect deforestation by comparing NDVI between periods"""
    
    # Get baseline and current NDVI
    baseline_collection = get_image_collection(aoi, baseline_start, baseline_end, sensor)
    current_collection = get_image_collection(aoi, current_start, current_end, sensor)
    
    baseline_ndvi = baseline_collection.select('NDVI').median()
    current_ndvi = current_collection.select('NDVI').median()
    
    # Calculate NDVI difference
    ndvi_diff = current_ndvi.subtract(baseline_ndvi)
    
    # Classify deforestation (significant NDVI decrease)
    deforestation = ndvi_diff.lt(-0.3).rename('deforestation')
    
    return deforestation


def identify_heat_islands(
    aoi: ee.Geometry,
    start_date: str,
    end_date: str,
    percentile: int = 90
) -> ee.Image:
    """Identify urban heat islands using LST"""
    
    # Get Landsat 8 collection with LST
    collection = get_image_collection(aoi, start_date, end_date, "L8")
    
    # Get LST composite
    lst_composite = collection.select('LST').median()
    
    # Calculate percentile threshold
    lst_percentile = collection.select('LST').reduce(
        ee.Reducer.percentile([percentile])
    )
    
    # Identify heat islands
    heat_islands = lst_composite.gt(lst_percentile).rename('heat_islands')
    
    return heat_islands


def export_to_geojson(
    image: ee.Image,
    aoi: ee.Geometry,
    scale: int = SCALE,
    threshold: float = 0.5
) -> Dict:
    """Convert raster to vector GeoJSON"""
    
    # Convert to binary mask
    mask = image.gt(threshold)
    
    # Vectorize
    vectors = mask.reduceToVectors(
        geometryType='polygon',
        reducer=ee.Reducer.countEvery(),
        scale=scale,
        geometry=aoi,
        maxPixels=1e9
    )
    
    # Convert to GeoJSON
    geojson = vectors.getInfo()
    
    return geojson


def get_time_series_data(
    aoi: ee.Geometry,
    start_date: str,
    end_date: str,
    sensor: str = "S2",
    index: str = "NDVI"
) -> pd.DataFrame:
    """Extract time series data for charts"""
    
    collection = get_image_collection(aoi, start_date, end_date, sensor)
    
    def extract_values(image):
        stats = image.select(index).reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=aoi,
            scale=SCALE,
            maxPixels=1e9
        )
        
        return ee.Feature(None, {
            'date': image.date().millis(),
            'value': stats.get(index)
        })
    
    # Extract values
    features = collection.map(extract_values)
    feature_list = features.getInfo()['features']
    
    # Convert to DataFrame
    dates = [datetime.fromtimestamp(f['properties']['date'] / 1000) 
             for f in feature_list]
    values = [f['properties']['value'] for f in feature_list]
    
    df = pd.DataFrame({
        'date': dates,
        index: values
    })
    
    return df.dropna()


def get_area_statistics(
    image: ee.Image,
    aoi: ee.Geometry,
    scale: int = SCALE
) -> Dict:
    """Calculate area statistics for classified image"""
    
    # Calculate pixel counts
    pixel_count = image.select(0).reduceRegion(
        reducer=ee.Reducer.count(),
        geometry=aoi,
        scale=scale,
        maxPixels=1e9
    )
    
    # Calculate area of positive pixels
    area_image = image.multiply(ee.Image.pixelArea())
    area_stats = area_image.reduceRegion(
        reducer=ee.Reducer.sum(),
        geometry=aoi,
        scale=scale,
        maxPixels=1e9
    )
    
    stats = {
        'total_pixels': pixel_count.getInfo(),
        'area_sq_meters': area_stats.getInfo(),
        'area_hectares': {k: v / 10000 for k, v in area_stats.getInfo().items()}
    }
    
    return stats


@st.cache_data(ttl=3600)
def get_map_tiles(
    image: ee.Image,
    vis_params: Dict,
    name: str = "Layer"
) -> str:
    """Get map tile URL for visualization"""
    
    map_id = image.getMapId(vis_params)
    return map_id['tile_fetcher'].url_format