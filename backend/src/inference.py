"""
Machine Learning inference for satellite image analysis
"""

import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models
import cv2
from typing import Dict, Tuple, List, Optional
import streamlit as st
from scipy import ndimage
from skimage import measure, morphology

from src.config import (
    MODEL_INPUT_SIZE, MODEL_PATH, CONFIDENCE_THRESHOLD,
    LST_URBAN_THRESHOLD, MIN_HEAT_ISLAND_AREA, NDVI_FOREST_THRESHOLD
)


@st.cache_resource
def load_deforestation_model():
    """Load pre-trained U-Net model for deforestation detection"""
    try:
        # Try to load existing model
        model = tf.keras.models.load_model(MODEL_PATH)
        return model
    except:
        # Create a simple U-Net architecture if model doesn't exist
        return create_unet_model()


def create_unet_model(input_shape: Tuple = MODEL_INPUT_SIZE) -> tf.keras.Model:
    """Create a simple U-Net model for segmentation"""
    
    inputs = tf.keras.Input(shape=input_shape)
    
    # Encoder
    c1 = layers.Conv2D(64, (3, 3), activation='relu', padding='same')(inputs)
    c1 = layers.Conv2D(64, (3, 3), activation='relu', padding='same')(c1)
    p1 = layers.MaxPooling2D((2, 2))(c1)
    
    c2 = layers.Conv2D(128, (3, 3), activation='relu', padding='same')(p1)
    c2 = layers.Conv2D(128, (3, 3), activation='relu', padding='same')(c2)
    p2 = layers.MaxPooling2D((2, 2))(c2)
    
    c3 = layers.Conv2D(256, (3, 3), activation='relu', padding='same')(p2)
    c3 = layers.Conv2D(256, (3, 3), activation='relu', padding='same')(c3)
    p3 = layers.MaxPooling2D((2, 2))(c3)
    
    # Bridge
    c4 = layers.Conv2D(512, (3, 3), activation='relu', padding='same')(p3)
    c4 = layers.Conv2D(512, (3, 3), activation='relu', padding='same')(c4)
    
    # Decoder
    u5 = layers.Conv2DTranspose(256, (2, 2), strides=(2, 2), padding='same')(c4)
    u5 = layers.concatenate([u5, c3])
    c5 = layers.Conv2D(256, (3, 3), activation='relu', padding='same')(u5)
    c5 = layers.Conv2D(256, (3, 3), activation='relu', padding='same')(c5)
    
    u6 = layers.Conv2DTranspose(128, (2, 2), strides=(2, 2), padding='same')(c5)
    u6 = layers.concatenate([u6, c2])
    c6 = layers.Conv2D(128, (3, 3), activation='relu', padding='same')(u6)
    c6 = layers.Conv2D(128, (3, 3), activation='relu', padding='same')(c6)
    
    u7 = layers.Conv2DTranspose(64, (2, 2), strides=(2, 2), padding='same')(c6)
    u7 = layers.concatenate([u7, c1])
    c7 = layers.Conv2D(64, (3, 3), activation='relu', padding='same')(u7)
    c7 = layers.Conv2D(64, (3, 3), activation='relu', padding='same')(c7)
    
    outputs = layers.Conv2D(1, (1, 1), activation='sigmoid')(c7)
    
    model = tf.keras.Model(inputs=[inputs], outputs=[outputs])
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    
    return model


def preprocess_for_inference(
    image_array: np.ndarray,
    target_size: Tuple = (512, 512)
) -> np.ndarray:
    """Preprocess image array for model inference"""
    
    # Resize if needed
    if image_array.shape[:2] != target_size:
        image_array = cv2.resize(image_array, target_size)
    
    # Normalize to 0-1 range
    if image_array.max() > 1:
        image_array = image_array / 255.0
    
    # Add batch dimension
    if len(image_array.shape) == 3:
        image_array = np.expand_dims(image_array, axis=0)
    
    return image_array


def detect_deforestation_ml(
    ndvi_stack: np.ndarray,
    model: Optional[tf.keras.Model] = None
) -> Dict:
    """Detect deforestation using deep learning model"""
    
    if model is None:
        model = load_deforestation_model()
    
    # Preprocess
    processed = preprocess_for_inference(ndvi_stack)
    
    # Predict
    prediction = model.predict(processed, verbose=0)
    
    # Post-process
    binary_mask = (prediction[0, :, :, 0] > CONFIDENCE_THRESHOLD).astype(np.uint8)
    
    # Apply morphological operations to clean up
    kernel = np.ones((5, 5), np.uint8)
    binary_mask = cv2.morphologyEx(binary_mask, cv2.MORPH_CLOSE, kernel)
    binary_mask = cv2.morphologyEx(binary_mask, cv2.MORPH_OPEN, kernel)
    
    # Calculate statistics
    deforestation_pixels = np.sum(binary_mask)
    total_pixels = binary_mask.size
    deforestation_percentage = (deforestation_pixels / total_pixels) * 100
    
    return {
        'mask': binary_mask,
        'deforestation_pixels': int(deforestation_pixels),
        'total_pixels': int(total_pixels),
        'deforestation_percentage': float(deforestation_percentage),
        'confidence_map': prediction[0, :, :, 0]
    }


def detect_heat_islands_threshold(
    lst_array: np.ndarray,
    threshold: float = LST_URBAN_THRESHOLD,
    min_area: float = MIN_HEAT_ISLAND_AREA
) -> Dict:
    """Detect urban heat islands using threshold and connected components"""
    
    # Apply threshold
    heat_mask = (lst_array > threshold).astype(np.uint8)
    
    # Remove small components
    min_pixels = min_area / (30 * 30)  # Convert area to pixels (assuming 30m resolution)
    heat_mask = morphology.remove_small_objects(heat_mask.astype(bool), min_pixels)
    
    # Label connected components
    labeled, num_features = ndimage.label(heat_mask)
    
    # Get properties of each heat island
    props = measure.regionprops(labeled)
    
    heat_islands = []
    for prop in props:
        heat_islands.append({
            'centroid': prop.centroid,
            'area': prop.area * 30 * 30,  # Convert to square meters
            'bbox': prop.bbox,
            'mean_intensity': np.mean(lst_array[labeled == prop.label])
        })
    
    # Calculate overall statistics
    total_heat_area = np.sum(heat_mask) * 30 * 30  # in square meters
    mean_heat_temp = np.mean(lst_array[heat_mask]) if np.any(heat_mask) else 0
    
    return {
        'mask': heat_mask,
        'num_islands': num_features,
        'islands': heat_islands,
        'total_heat_area': float(total_heat_area),
        'mean_heat_temperature': float(mean_heat_temp)
    }


def analyze_vegetation_trend(
    ndvi_time_series: np.ndarray,
    dates: List[str]
) -> Dict:
    """Analyze vegetation trends from NDVI time series"""
    
    # Reshape for pixel-wise analysis
    if len(ndvi_time_series.shape) == 4:  # (time, height, width, channels)
        ndvi_time_series = ndvi_time_series[:, :, :, 0]
    
    time_steps, height, width = ndvi_time_series.shape
    
    # Create time array (days from start)
    time_array = np.arange(time_steps)
    
    # Initialize result arrays
    slope_array = np.zeros((height, width))
    r_squared_array = np.zeros((height, width))
    
    # Compute linear trend for each pixel
    for i in range(height):
        for j in range(width):
            pixel_series = ndvi_time_series[:, i, j]
            
            # Skip if all NaN
            if np.all(np.isnan(pixel_series)):
                continue
            
            # Remove NaN values
            valid_mask = ~np.isnan(pixel_series)
            if np.sum(valid_mask) < 3:  # Need at least 3 points
                continue
            
            valid_time = time_array[valid_mask]
            valid_ndvi = pixel_series[valid_mask]
            
            # Fit linear regression
            coeffs = np.polyfit(valid_time, valid_ndvi, 1)
            slope_array[i, j] = coeffs[0]
            
            # Calculate R-squared
            predicted = np.polyval(coeffs, valid_time)
            ss_res = np.sum((valid_ndvi - predicted) ** 2)
            ss_tot = np.sum((valid_ndvi - np.mean(valid_ndvi)) ** 2)
            r_squared_array[i, j] = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
    
    # Classify trends
    significant_mask = r_squared_array > 0.5
    improvement_mask = (slope_array > 0.001) & significant_mask
    degradation_mask = (slope_array < -0.001) & significant_mask
    stable_mask = ~improvement_mask & ~degradation_mask & significant_mask
    
    return {
        'slope_map': slope_array,
        'r_squared_map': r_squared_array,
        'improvement_mask': improvement_mask,
        'degradation_mask': degradation_mask,
        'stable_mask': stable_mask,
        'mean_slope': float(np.mean(slope_array[significant_mask])),
        'improvement_area': float(np.sum(improvement_mask) * 30 * 30),
        'degradation_area': float(np.sum(degradation_mask) * 30 * 30)
    }


def generate_risk_score(
    deforestation_pct: float,
    heat_island_area: float,
    vegetation_degradation: float
) -> Dict:
    """Generate environmental risk score based on multiple factors"""
    
    # Normalize inputs to 0-1 scale
    deforestation_score = min(deforestation_pct / 20, 1.0)  # 20% = max score
    heat_score = min(heat_island_area / 1e6, 1.0)  # 1 sq km = max score  
    vegetation_score = min(vegetation_degradation / 1e6, 1.0)
    
    # Weighted combination
    weights = {
        'deforestation': 0.4,
        'heat_island': 0.3,
        'vegetation': 0.3
    }
    
    overall_score = (
        weights['deforestation'] * deforestation_score +
        weights['heat_island'] * heat_score +
        weights['vegetation'] * vegetation_score
    )
    
    # Determine risk level
    if overall_score < 0.3:
        risk_level = "Low"
        color = "#00FF00"
    elif overall_score < 0.6:
        risk_level = "Medium"
        color = "#FFFF00"
    else:
        risk_level = "High"
        color = "#FF0000"
    
    return {
        'overall_score': float(overall_score),
        'risk_level': risk_level,
        'color': color,
        'components': {
            'deforestation': float(deforestation_score),
            'heat_island': float(heat_score),
            'vegetation_degradation': float(vegetation_score)
        }
    }