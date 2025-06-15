# 🛰️ AI-Powered Satellite Climate Monitoring

[![Live Demo](https://img.shields.io/badge/demo-live-brightgreen)](https://your-app.streamlit.app)
[![React Frontend](https://img.shields.io/badge/frontend-React-61DAFB)](https://your-app.vercel.app)
[![Python](https://img.shields.io/badge/python-3.9+-blue)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

An interactive, full-stack application for real-time satellite image analysis focusing on deforestation detection, urban heat island mapping, and vegetation change monitoring using Google Earth Engine and deep learning.

## 🌟 Features

- **🌳 Deforestation Detection**: U-Net based segmentation on NDVI rasters
- **🏙️ Urban Heat Island Analysis**: LST threshold detection with connected components
- **🌱 Vegetation Change Tracking**: Multi-temporal NDVI trend analysis
- **🗺️ Interactive Mapping**: Real-time GeoJSON overlays with Leaflet
- **📊 Dynamic Visualizations**: Time-series charts and histograms
- **💫 Modern UI**: Glassmorphic design with fluid animations

## 🏗️ Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌────────────────┐
│  React Frontend │────▶│  Python Backend  │────▶│ Google Earth   │
│  (Vercel)       │     │  (Streamlit)     │     │ Engine API     │
└─────────────────┘     └──────────────────┘     └────────────────┘
        │                        │                         │
        │                        ▼                         ▼
        │               ┌─────────────────┐      ┌─────────────────┐
        └──────────────▶│   ML Models     │      │  Sentinel-2/    │
                        │  (TensorFlow)   │      │  Landsat-8      │
                        └─────────────────┘      └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 16+
- Google Earth Engine account
- Service account credentials

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure Earth Engine credentials
# Add your service account JSON to .streamlit/secrets.toml

# Run Streamlit app
streamlit run app.py
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

## 📁 Project Structure

```
ai-sat-climate-monitoring/
├── frontend/          # React + Vite + Tailwind
│   ├── src/
│   │   ├── components/   # UI components
│   │   ├── hooks/        # Custom React hooks
│   │   └── styles/       # CSS and animations
│   └── package.json
│
└── backend/           # Python + Streamlit
    ├── src/
    │   ├── gee_utils.py    # Earth Engine utilities
    │   ├── inference.py    # ML model inference
    │   └── config.py       # Configuration
    └── app.py             # Main Streamlit app
```

## 🔧 Configuration

### Environment Variables

Create `.streamlit/secrets.toml`:

```toml
[gee]
service_account = "your-service-account@project.iam.gserviceaccount.com"
private_key = "-----BEGIN PRIVATE KEY-----\n..."

[mapbox]
token = "your-mapbox-token"  # Optional
```

### API Endpoints

- `GET /api/deforestation` - Deforestation analysis results
- `GET /api/ndvi` - NDVI time series data
- `GET /api/lst` - Land Surface Temperature data
- `POST /api/analyze` - Trigger new analysis

## 🛠️ Tech Stack

### Backend
- **Framework**: Streamlit + FastAPI
- **Geospatial**: Google Earth Engine, geemap
- **ML**: TensorFlow/Keras (U-Net), scikit-learn
- **Data Processing**: NumPy, Pandas, Rasterio

### Frontend
- **Framework**: React + Vite
- **Styling**: Tailwind CSS + Glassmorphism
- **Animations**: Framer Motion
- **Maps**: React-Leaflet
- **Charts**: Recharts

## 📊 Data Sources

- **Sentinel-2**: 10m resolution multispectral imagery
- **Landsat-8**: 30m resolution thermal and optical bands
- **Processing**: Google Earth Engine cloud platform

## 🚀 Deployment

### Backend (Streamlit Cloud)

1. Push to GitHub
2. Connect repo to Streamlit Cloud
3. Add secrets in dashboard
4. Deploy automatically

### Frontend (Vercel)

```bash
cd frontend
npm run build
vercel --prod
```

## 🔬 ML Models

### Deforestation Detection
- Architecture: U-Net with EfficientNet backbone
- Input: 4-channel NDVI time series
- Output: Binary segmentation mask

### Heat Island Detection
- Method: Adaptive thresholding + morphological operations
- Input: Land Surface Temperature raster
- Output: Polygon boundaries of heat islands

## 📈 Performance

- Image processing: < 5s for 512x512 tiles
- Model inference: < 2s per prediction
- API response time: < 500ms average

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🏆 Acknowledgments

- Google Earth Engine for satellite data access
- Streamlit team for the amazing framework
- TensorFlow Hub for pretrained models

## 📞 Contact

Project Link: [https://github.com/yourusername/ai-sat-climate-monitoring](https://github.com/yourusername/ai-sat-climate-monitoring)

---

Built with ❤️ for [Hackathon Name] 2024