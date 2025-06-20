"""
FastAPI server to expose APIs for React frontend
Run this alongside Streamlit: python api_server.py
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import numpy as np
import pandas as pd
from typing import Dict, List, Optional

# It's better to handle potential import errors if running standalone
try:
    from src.gee_utils import initialize_earth_engine
    from src.inference import generate_risk_score
    is_prod = True
except ImportError:
    print("Warning: Could not import src modules. Running in standalone mock mode.")
    is_prod = False

app = FastAPI()

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Earth Engine on startup if not in mock mode
@app.on_event("startup")
async def startup_event():
    if is_prod:
        try:
            # This part requires credentials to be set up
            # initialize_earth_engine() 
            print("Earth Engine initialization skipped for now. Add credentials to enable.")
        except Exception as e:
            print(f"Failed to initialize Earth Engine: {e}")
    else:
        print("Running in mock mode. No Earth Engine connection.")

# Request/Response models
class AnalysisConfig(BaseModel):
    aoi: str
    dateRange: Dict[str, str]
    features: Dict[str, bool]

class AnalysisResponse(BaseModel):
    timestamp: str
    deforestationRate: float
    heatIslands: int
    ndviChange: float
    confidence: float
    imageCount: int
    cloudCover: float
    processingTime: str
    deforestation: Optional[Dict]
    geojson: Dict

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "AI Satellite Climate Monitor API"}

@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze(config: AnalysisConfig):
    """Run analysis based on configuration"""
    try:
        # In a real scenario, this would call actual Earth Engine analysis functions
        # For this demo, we'll return mock data as intended.
        
        mock_results = {
            "timestamp": datetime.now().isoformat(),
            "deforestationRate": round(np.random.uniform(2, 5), 2),
            "heatIslands": np.random.randint(3, 8),
            "ndviChange": round(np.random.uniform(-0.2, -0.05), 2),
            "confidence": round(np.random.uniform(85, 95), 2),
            "imageCount": np.random.randint(10, 20),
            "cloudCover": round(np.random.uniform(5, 25), 2),
            "processingTime": f"{np.random.uniform(1.5, 3.5):.1f}",
            "deforestation": {
                "coordinates": [
                    [-10.3, -63.2],
                    [-10.3, -63.1],
                    [-10.2, -63.1],
                    [-10.2, -63.2],
                ],
                "area": round(np.random.uniform(100, 500), 2)
            },
            "geojson": {
                "type": "FeatureCollection",
                "features": [] # Populate with actual GeoJSON features in a real implementation
            }
        }
        
        return AnalysisResponse(**mock_results)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/deforestation")
async def get_deforestation_data():
    """Get deforestation analysis results"""
    # Mock data for demo
    dates = pd.date_range(start='2023-01-01', end='2024-01-01', freq='M')
    return {
        "data": [
            {"date": date.isoformat(), "forestCover": round(np.random.uniform(90, 95), 2)}
            for date in dates
        ]
    }

@app.get("/api/ndvi")
async def get_ndvi_data():
    """Get NDVI time series data"""
    dates = pd.date_range(start='2023-01-01', end='2024-01-01', freq='M')
    return {
        "data": [
            {"date": date.isoformat(), "ndvi": round(np.random.uniform(0.3, 0.8), 2)}
            for date in dates
        ]
    }

@app.get("/api/lst")
async def get_temperature_data():
    """Get Land Surface Temperature data"""
    return {
        "data": {
            "temperatures": np.random.normal(35, 5, 100).tolist(),
            "heatIslands": [
                {
                    "id": i,
                    "center": [np.random.uniform(-10.5, -9.5), np.random.uniform(-63.5, -62.5)],
                    "area": round(np.random.uniform(0.5, 3), 2),
                    "maxTemp": round(np.random.uniform(38, 45), 2)
                }
                for i in range(5)
            ]
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
