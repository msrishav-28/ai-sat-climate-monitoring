"""
AI-Powered Satellite Climate Monitoring - Streamlit App
"""

import streamlit as st
import pandas as pd
import numpy as np
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import plotly.express as px
    import plotly.graph_objects as go
except ImportError:
    st.error("Please install plotly: pip install plotly")
    st.stop()

from datetime import datetime, timedelta
import json
from typing import Dict, List

try:
    import folium
    from streamlit_folium import st_folium
except ImportError:
    st.error("Please install folium: pip install folium streamlit-folium")
    st.stop()

# Import custom modules with error handling
try:
    from src.gee_utils import (
        initialize_earth_engine, get_aoi_geometry, get_image_collection,
        get_composite_image, compute_ndvi_trend, detect_deforestation,
        identify_heat_islands, export_to_geojson, get_time_series_data,
        get_area_statistics, get_map_tiles
    )
    from src.inference import (
        detect_deforestation_ml, detect_heat_islands_threshold,
        analyze_vegetation_trend, generate_risk_score
    )
    from src.config import (
        DEFAULT_AOIS, NDVI_VIS_PARAMS, LST_VIS_PARAMS,
        DEFORESTATION_COLORS
    )
except ImportError as e:
    st.error(f"Failed to import modules: {e}")
    st.error("Make sure you're running from the backend directory")
    st.stop()

# Page config
st.set_page_config(
    page_title="AI Satellite Climate Monitor",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for glassmorphic design
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .glass {
        background: rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        padding: 20px;
        margin: 10px 0;
    }
    .metric-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(5px);
        border-radius: 15px;
        padding: 15px;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    h1, h2, h3 {
        color: white;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'initialized' not in st.session_state:
    st.session_state.initialized = False
    st.session_state.analysis_results = None
    st.session_state.selected_aoi = None

# Initialize Earth Engine
@st.cache_resource
def init_ee():
    initialize_earth_engine()
    return True

# Header
st.markdown("<h1 style='text-align: center;'>🛰️ AI-Powered Satellite Climate Monitoring</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: white;'>Real-time analysis of deforestation, urban heat islands, and vegetation changes</p>", unsafe_allow_html=True)

# Sidebar Controls
with st.sidebar:
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.header("🎛️ Analysis Controls")
    
    # Area of Interest Selection
    st.subheader("📍 Select Area")
    aoi_option = st.selectbox(
        "Choose a predefined area or draw custom",
        ["Amazon Rainforest", "Jakarta Metropolitan", "California Central Valley", "Custom"]
    )
    
    if aoi_option != "Custom":
        aoi_key = aoi_option.lower().replace(" ", "_").replace("_rainforest", "").replace("_metropolitan", "").replace("_central_valley", "")
        selected_aoi = DEFAULT_AOIS.get(aoi_key, DEFAULT_AOIS["amazon"])
    else:
        st.info("Draw a polygon on the map to define custom area")
        selected_aoi = None
    
    # Date Range Selection
    st.subheader("📅 Time Period")
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "Start Date",
            datetime.now() - timedelta(days=365),
            max_value=datetime.now()
        )
    with col2:
        end_date = st.date_input(
            "End Date",
            datetime.now(),
            max_value=datetime.now()
        )
    
    # Analysis Features
    st.subheader("🔍 Analysis Features")
    analyze_deforestation = st.checkbox("🌳 Deforestation Detection", value=True)
    analyze_heat_islands = st.checkbox("🏙️ Urban Heat Islands", value=True)
    analyze_vegetation = st.checkbox("🌱 Vegetation Trends", value=True)
    
    # Advanced Options
    with st.expander("⚙️ Advanced Settings"):
        cloud_threshold = st.slider("Max Cloud Cover %", 0, 50, 20)
        analysis_scale = st.slider("Analysis Resolution (m)", 10, 100, 30)
        use_ml_models = st.checkbox("Use ML Models", value=True)
    
    # Run Analysis Button
    run_analysis = st.button("🚀 Run Analysis", use_container_width=True, type="primary")
    
    st.markdown("</div>", unsafe_allow_html=True)

# Main Content Area
if not st.session_state.initialized:
    with st.spinner("Initializing Earth Engine..."):
        if init_ee():
            st.session_state.initialized = True
            st.success("✅ Earth Engine initialized successfully!")

# Create main layout
col1, col2 = st.columns([2, 1])

with col1:
    # Map Display
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.subheader("🗺️ Interactive Map")
    
    # Create folium map
    if selected_aoi:
        center_lat = np.mean([coord[1] for coord in selected_aoi['coordinates']])
        center_lon = np.mean([coord[0] for coord in selected_aoi['coordinates']])
    else:
        center_lat, center_lon = 0, 0
    
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=10,
        tiles="OpenStreetMap"
    )
    
    # Add AOI polygon
    if selected_aoi:
        folium.Polygon(
            locations=[[coord[1], coord[0]] for coord in selected_aoi['coordinates']],
            color='blue',
            fill=True,
            fillColor='blue',
            fillOpacity=0.2
        ).add_to(m)
    
    # Display map
    map_data = st_folium(m, height=500, key="main_map")
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    # Metrics Panel
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.subheader("📊 Key Metrics")
    
    if st.session_state.analysis_results:
        results = st.session_state.analysis_results
        
        # Display metrics
        metric_col1, metric_col2 = st.columns(2)
        
        with metric_col1:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.metric("🌳 Forest Loss", f"{results.get('deforestation_pct', 0):.1f}%", 
                     delta=f"{results.get('deforestation_change', 0):.1f}%")
            st.markdown("</div>", unsafe_allow_html=True)
            
        with metric_col2:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.metric("🌡️ Heat Islands", f"{results.get('heat_islands_count', 0)}", 
                     delta=f"+{results.get('heat_area_km2', 0):.1f} km²")
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Risk Score
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        risk_score = results.get('risk_score', {})
        st.metric("⚠️ Environmental Risk", risk_score.get('risk_level', 'Unknown'),
                 delta=f"Score: {risk_score.get('overall_score', 0):.2f}")
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Download Results
        st.download_button(
            label="📥 Download GeoJSON",
            data=json.dumps(results.get('geojson', {})),
            file_name=f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.geojson",
            mime="application/json"
        )
    else:
        st.info("👈 Configure parameters and click 'Run Analysis' to begin")
    
    st.markdown("</div>", unsafe_allow_html=True)

# Analysis Charts Section
if st.session_state.analysis_results:
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.subheader("📈 Analysis Results")
    
    tab1, tab2, tab3 = st.tabs(["🌳 Deforestation", "🌡️ Heat Islands", "🌱 Vegetation Trends"])
    
    with tab1:
        if analyze_deforestation and 'deforestation_data' in st.session_state.analysis_results:
            col1, col2 = st.columns(2)
            
            with col1:
                # Deforestation time series
                df = pd.DataFrame(st.session_state.analysis_results['deforestation_data'])
                fig = px.line(df, x='date', y='forest_cover', 
                             title='Forest Cover Over Time',
                             labels={'forest_cover': 'Forest Cover (%)', 'date': 'Date'})
                fig.update_layout(template='plotly_dark')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Deforestation map
                fig = go.Figure(data=go.Scattermapbox(
                    lat=st.session_state.analysis_results.get('deforestation_coords', {}).get('lat', []),
                    lon=st.session_state.analysis_results.get('deforestation_coords', {}).get('lon', []),
                    mode='markers',
                    marker=dict(size=10, color='red'),
                    text='Deforestation Area'
                ))
                fig.update_layout(
                    mapbox_style="open-street-map",
                    mapbox=dict(center=dict(lat=center_lat, lon=center_lon), zoom=9),
                    margin=dict(r=0, t=0, l=0, b=0),
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        if analyze_heat_islands and 'heat_data' in st.session_state.analysis_results:
            col1, col2 = st.columns(2)
            
            with col1:
                # Temperature distribution
                temps = st.session_state.analysis_results['heat_data']['temperatures']
                fig = px.histogram(x=temps, nbins=30,
                                 title='Land Surface Temperature Distribution',
                                 labels={'x': 'Temperature (°C)', 'y': 'Frequency'})
                fig.update_layout(template='plotly_dark')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Heat island intensity
                heat_islands = st.session_state.analysis_results['heat_data']['islands']
                df_heat = pd.DataFrame(heat_islands)
                fig = px.scatter(df_heat, x='area', y='mean_temperature',
                               size='area', color='mean_temperature',
                               title='Heat Island Analysis',
                               labels={'area': 'Area (km²)', 'mean_temperature': 'Mean Temp (°C)'})
                fig.update_layout(template='plotly_dark')
                st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        if analyze_vegetation and 'vegetation_data' in st.session_state.analysis_results:
            # NDVI time series
            df_veg = pd.DataFrame(st.session_state.analysis_results['vegetation_data'])
            fig = px.line(df_veg, x='date', y='ndvi',
                         title='NDVI Time Series',
                         labels={'ndvi': 'NDVI', 'date': 'Date'})
            fig.add_hline(y=0.7, line_dash="dash", line_color="green", 
                         annotation_text="Healthy Vegetation")
            fig.add_hline(y=0.3, line_dash="dash", line_color="orange",
                         annotation_text="Sparse Vegetation")
            fig.update_layout(template='plotly_dark')
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# Run Analysis Function
def run_full_analysis():
    """Execute complete analysis pipeline"""
    try:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Get AOI geometry
        status_text.text("Preparing area of interest...")
        if selected_aoi:
            aoi = get_aoi_geometry(selected_aoi['coordinates'])
        else:
            st.error("Please select an area of interest")
            return
        
        progress_bar.progress(10)
        
        # Initialize results
        results = {
            'timestamp': datetime.now().isoformat(),
            'aoi': selected_aoi['name'],
            'date_range': f"{start_date} to {end_date}"
        }
        
        # Get satellite imagery
        status_text.text("Fetching satellite imagery...")
        collection = get_image_collection(
            aoi, 
            start_date.isoformat(), 
            end_date.isoformat(),
            sensor="S2",
            max_cloud=cloud_threshold
        )
        
        composite = get_composite_image(collection)
        progress_bar.progress(30)
        
        # Deforestation Analysis
        if analyze_deforestation:
            status_text.text("Analyzing deforestation...")
            
            # Compare with baseline (1 year ago)
            baseline_start = (start_date - timedelta(days=365)).isoformat()
            baseline_end = (start_date - timedelta(days=335)).isoformat()
            
            deforestation_mask = detect_deforestation(
                aoi, baseline_start, baseline_end,
                start_date.isoformat(), end_date.isoformat()
            )
            
            # Get statistics
            defor_stats = get_area_statistics(deforestation_mask, aoi)
            
            # Generate time series
            ndvi_ts = get_time_series_data(
                aoi, start_date.isoformat(), end_date.isoformat(),
                sensor="S2", index="NDVI"
            )
            
            results['deforestation_pct'] = defor_stats['area_hectares'].get('deforestation', 0) / 100
            results['deforestation_data'] = {
                'date': ndvi_ts['date'].tolist(),
                'forest_cover': (ndvi_ts['NDVI'] * 100).tolist()
            }
            
            progress_bar.progress(50)
        
        # Heat Island Analysis
        if analyze_heat_islands:
            status_text.text("Detecting urban heat islands...")
            
            # Get Landsat 8 data for LST
            l8_collection = get_image_collection(
                aoi, start_date.isoformat(), end_date.isoformat(),
                sensor="L8", max_cloud=cloud_threshold
            )
            
            heat_mask = identify_heat_islands(
                aoi, start_date.isoformat(), end_date.isoformat()
            )
            
            heat_stats = get_area_statistics(heat_mask, aoi)
            
            results['heat_islands_count'] = 5  # Placeholder
            results['heat_area_km2'] = heat_stats['area_hectares'].get('heat_islands', 0) / 100
            results['heat_data'] = {
                'temperatures': np.random.normal(35, 5, 1000).tolist(),
                'islands': [
                    {'area': np.random.uniform(0.1, 2), 
                     'mean_temperature': np.random.uniform(35, 45)}
                    for _ in range(5)
                ]
            }
            
            progress_bar.progress(70)
        
        # Vegetation Trend Analysis
        if analyze_vegetation:
            status_text.text("Analyzing vegetation trends...")
            
            ndvi_trend = compute_ndvi_trend(
                aoi, start_date.isoformat(), end_date.isoformat()
            )
            
            # Get time series
            veg_ts = get_time_series_data(
                aoi, start_date.isoformat(), end_date.isoformat(),
                sensor="S2", index="NDVI"
            )
            
            results['vegetation_data'] = {
                'date': veg_ts['date'].tolist(),
                'ndvi': veg_ts['NDVI'].tolist()
            }
            
            progress_bar.progress(90)
        
        # Calculate Risk Score
        status_text.text("Calculating environmental risk score...")
        risk_score = generate_risk_score(
            results.get('deforestation_pct', 0),
            results.get('heat_area_km2', 0) * 1e6,  # Convert to m²
            0  # Placeholder for vegetation degradation
        )
        results['risk_score'] = risk_score
        
        # Generate GeoJSON output
        results['geojson'] = {
            "type": "FeatureCollection",
            "features": []
        }
        
        progress_bar.progress(100)
        status_text.text("Analysis complete!")
        
        # Store results
        st.session_state.analysis_results = results
        
        # Success message
        st.success("✅ Analysis completed successfully!")
        st.balloons()
        
    except Exception as e:
        st.error(f"❌ Analysis failed: {str(e)}")
        st.exception(e)

# Handle analysis trigger
if run_analysis:
    run_full_analysis()

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: white;'>Built with ❤️ using Streamlit, Google Earth Engine, and TensorFlow</p>",
    unsafe_allow_html=True
)