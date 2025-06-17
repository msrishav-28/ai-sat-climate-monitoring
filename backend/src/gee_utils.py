import ee
import streamlit as st
import os
from pathlib import Path

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