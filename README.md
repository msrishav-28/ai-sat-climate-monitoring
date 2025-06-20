```markdown
# 🛰️ AI-Powered Satellite Climate Monitoring

[![Python](https://img.shields.io/badge/python-3.9+-blue)](https://python.org)
[![React](https://img.shields.io/badge/frontend-React-61DAFB)](https://reactjs.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

An interactive, full-stack application for real-time satellite image analysis focusing on deforestation detection, urban heat island mapping, and vegetation change monitoring using Google Earth Engine and deep learning.

## 🌟 Features

-   **🌳 Deforestation Detection**: Utilizes a U-Net based segmentation model on NDVI (Normalized Difference Vegetation Index) rasters to identify areas of forest loss.
-   **🏙️ Urban Heat Island Analysis**: Implements Land Surface Temperature (LST) threshold detection with connected components to map urban heat islands.
-   **🌱 Vegetation Change Tracking**: Performs multi-temporal NDVI trend analysis to monitor changes in vegetation health over time.
-   **🗺️ Interactive Mapping**: Features a real-time, interactive map with GeoJSON overlays using Leaflet for visualizing analysis results.
-   **📊 Dynamic Visualizations**: Presents data through dynamic charts and histograms, including time-series graphs for forest cover and NDVI trends, and temperature distribution bar charts.
-   **💫 Modern UI**: Boasts a sleek, glassmorphic design with fluid animations built with React, Tailwind CSS, and Framer Motion.

## 🏗️ Architecture

The application is composed of a React frontend and a Python backend, which communicate via a REST API. The backend leverages the Google Earth Engine for satellite imagery and TensorFlow for machine learning model inference.

```

┌─────────────────┐     ┌──────────────────┐     ┌────────────────┐
│  React Frontend │────▶│  FastAPI Server  │────▶│ Google Earth   │
│  (Vite)         │     │  (Python)        │     │ Engine API     │
└─────────────────┘     └──────────────────┘     └────────────────┘
│                        │                         │
│                        ▼                         ▼
│               ┌─────────────────┐      ┌─────────────────┐
└──────────────▶│   ML Models     │      │  Sentinel-2/    │
│  (TensorFlow)   │      │  Landsat-8      │
└─────────────────┘      └─────────────────┘

````

## 🛠️ Tech Stack

### Backend

-   **Framework**: Streamlit, FastAPI
-   **Geospatial**: Google Earth Engine, geemap, folium
-   **ML**: TensorFlow/Keras (U-Net), scikit-learn, OpenCV
-   **Data Processing**: NumPy, Pandas, Rasterio

### Frontend

-   **Framework**: React, Vite
-   **Styling**: Tailwind CSS, Glassmorphism
-   **Animations**: Framer Motion
-   **Maps**: React-Leaflet
-   **Charts**: Recharts
-   **HTTP Client**: Axios

## 🚀 Quick Start

### Prerequisites

-   Python 3.9+
-   Node.js 18+
-   Google Earth Engine account and authenticated credentials
-   Service account credentials (for non-interactive use)

### Backend Setup

```bash
cd backend
python -m venv venv
# On Windows: venv\Scripts\activate
# On macOS/Linux: source venv/bin/activate
pip install -r requirements.txt

# Configure Earth Engine credentials by running the following command
# and following the on-screen instructions:
earthengine authenticate

# To run the Streamlit application:
streamlit run app.py

# To run the FastAPI server:
python api_server.py
````

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The React development server will start on `http://localhost:3000` and proxy API requests to the FastAPI backend on `http://localhost:8000`.

## 📁 Project Structure

```
ai-sat-climate-monitoring/
├── backend/               # Python backend (Streamlit and FastAPI)
│   ├── .streamlit/        # Streamlit configuration
│   ├── src/               # Source code for backend logic
│   │   ├── gee_utils.py   # Google Earth Engine utilities
│   │   ├── inference.py   # ML model inference functions
│   │   └── config.py      # Configuration constants
│   ├── api_server.py      # FastAPI application
│   ├── app.py             # Main Streamlit application
│   └── requirements.txt   # Python dependencies
│
└── frontend/              # React frontend
    ├── src/
    │   ├── components/    # React components
    │   ├── hooks/         # Custom React hooks
    │   ├── styles/        # CSS and styling
    │   └── App.jsx        # Main application component
    └── package.json       # Node.js dependencies
```

## 🔧 Configuration

### Environment Variables

For non-interactive authentication with Google Earth Engine, you can create a `.streamlit/secrets.toml` file in the `backend` directory with the following content:

```toml
[gee]
service_account = "your-service-account@project.iam.gserviceaccount.com"
private_key = "-----BEGIN PRIVATE KEY-----\n..."
```

### API Endpoints

The FastAPI server provides the following endpoints:

  - `GET /api/health`: Health check for the API server.
  - `POST /api/analyze`: Triggers a new analysis based on the provided configuration.
  - `GET /api/deforestation`: Retrieves deforestation analysis results.
  - `GET /api/ndvi`: Fetches NDVI time-series data.
  - `GET /api/lst`: Gets Land Surface Temperature data.

## 🔬 ML Models

### Deforestation Detection

  - **Architecture**: U-Net
  - **Input**: NDVI image stack
  - **Output**: Binary segmentation mask of deforested areas

### Heat Island Detection

  - **Method**: Thresholding and connected components analysis
  - **Input**: Land Surface Temperature (LST) array
  - **Output**: Mask of urban heat islands with statistics

## 🤝 Contributing

Contributions are welcome\! Please follow these steps to contribute:

1.  Fork the repository.
2.  Create a new feature branch (`git checkout -b feature/amazing-feature`).
3.  Commit your changes (`git commit -m 'Add amazing feature'`).
4.  Push to the branch (`git push origin feature/amazing-feature`).
5.  Open a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](https://www.google.com/search?q=LICENSE) file for details.

```
```
