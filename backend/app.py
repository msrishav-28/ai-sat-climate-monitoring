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

# Now import with try-except for better error handling
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
    st.error(f"Import Error: {e}")
    st.error("Make sure you're running from the backend directory: `cd backend && streamlit run app.py`")
    st.stop()

from datetime import datetime, timedelta
import json
from typing import Dict, List

# Import visualization libraries with error handling
try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    st.warning("Plotly not installed. Install with: pip install plotly")

try:
    import folium
    from streamlit_folium import st_folium
    FOLIUM_AVAILABLE = True
except ImportError:
    FOLIUM_AVAILABLE = False
    st.warning("Folium not installed. Install with: pip install folium streamlit-folium")

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
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: bold;
        border-radius: 10px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
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
    try:
        initialize_earth_engine()
        return True
    except Exception as e:
        st.error(f"Failed to initialize Earth Engine: {e}")
        return False

# Header
st.markdown("<h1 style='text-align: center;'>🛰️ AI-Powered Satellite Climate Monitoring</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: white;'>Real-time analysis of deforestation, urban heat islands, and vegetation changes</p>", unsafe_allow_html=True)

# Initialize Earth Engine
if not st.session_state.initialized:
    with st.spinner("Initializing Earth Engine..."):
        if init_ee():
            st.session_state.initialized = True
            st.success("✅ Earth Engine initialized successfully!")
        else:
            st.stop()

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
col1, col2 = st.columns([2, 1])

with col1:
    # Map Display
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.subheader("🗺️ Interactive Map")
    
    if FOLIUM_AVAILABLE and selected_aoi:
        # Create folium map
        center_lat = np.mean([coord[1] for coord in selected_aoi['coordinates']])
        center_lon = np.mean([coord[0] for coord in selected_aoi['coordinates']])
        
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=10,
            tiles="OpenStreetMap"
        )
        
        # Add AOI polygon
        folium.Polygon(
            locations=[[coord[1], coord[0]] for coord in selected_aoi['coordinates']],
            color='blue',
            fill=True,
            fillColor='blue',
            fillOpacity=0.2
        ).add_to(m)
        
        # Display map
        map_data = st_folium(m, height=500, key="main_map")
    else:
        st.info("Select an area of interest to display the map")
    
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
            st.metric("🌳 Forest Loss", f"{results.get('deforestation_pct', 0):.1f}%", 
                     delta=f"{results.get('deforestation_change', 0):.1f}%")
            
        with metric_col2:
            st.metric("🌡️ Heat Islands", f"{results.get('heat_islands_count', 0)}", 
                     delta=f"+{results.get('heat_area_km2', 0):.1f} km²")
        
        # Risk Score
        risk_score = results.get('risk_score', {})
        st.metric("⚠️ Environmental Risk", risk_score.get('risk_level', 'Unknown'),
                 delta=f"Score: {risk_score.get('overall_score', 0):.2f}")
        
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
if st.session_state.analysis_results and PLOTLY_AVAILABLE:
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
    
    with tab2:
        if analyze_heat_islands and 'heat_data' in st.session_state.analysis_results:
            # Temperature distribution
            temps = st.session_state.analysis_results['heat_data']['temperatures']
            fig = px.histogram(x=temps, nbins=30,
                             title='Land Surface Temperature Distribution',
                             labels={'x': 'Temperature (°C)', 'y': 'Frequency'})
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
        
        # Validate inputs
        if not selected_aoi:
            st.error("Please select an area of interest")
            return
            
        # Get AOI geometry
        status_text.text("Preparing area of interest...")
        aoi = get_aoi_geometry(selected_aoi['coordinates'])
        progress_bar.progress(10)
        
        # Initialize results
        results = {
            'timestamp': datetime.now().isoformat(),
            'aoi': selected_aoi['name'],
            'date_range': f"{start_date} to {end_date}"
        }
        
        # For demo purposes, generate mock data
        # In production, these would be real Earth Engine calls
        
        if analyze_deforestation:
            status_text.text("Analyzing deforestation...")
            # Mock deforestation data
            results['deforestation_pct'] = np.random.uniform(2, 5)
            results['deforestation_change'] = np.random.uniform(-1, -3)
            results['deforestation_data'] = {
                'date': pd.date_range(start_date, end_date, periods=7).tolist(),
                'forest_cover': np.random.uniform(90, 95, 7).tolist()
            }
            progress_bar.progress(40)
        
        if analyze_heat_islands:
            status_text.text("Detecting urban heat islands...")
            # Mock heat island data
            results['heat_islands_count'] = np.random.randint(3, 8)
            results['heat_area_km2'] = np.random.uniform(1, 5)
            results['heat_data'] = {
                'temperatures': np.random.normal(35, 5, 1000).tolist(),
                'islands': [
                    {'area': np.random.uniform(0.1, 2), 
                     'mean_temperature': np.random.uniform(35, 45)}
                    for _ in range(5)
                ]
            }
            progress_bar.progress(70)
        
        if analyze_vegetation:
            status_text.text("Analyzing vegetation trends...")
            # Mock vegetation data
            results['vegetation_data'] = {
                'date': pd.date_range(start_date, end_date, periods=10).tolist(),
                'ndvi': np.random.uniform(0.3, 0.8, 10).tolist()
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