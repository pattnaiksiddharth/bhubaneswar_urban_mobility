# Bhubaneswar Urban Mobility Analytics: Traffic & Public Transport Demand Forecasting

An end-to-end data analytics and forecasting project applying the **CRISP-DM (Cross-Industry Standard Process for Data Mining)** methodology to urban mobility, public transport accessibility, and traffic demand forecasting in Bhubaneswar, Odisha, India.

---

## Project Structure

```
urban-mobility-bbsr/
├── data/
│   ├── raw/          # Raw OSM geospatial data (Road network, bus stops, POIs)
│   ├── interim/      # Intermediate visualizations and transformed datasets
│   └── processed/    # Cleaned, feature-engineered modeling tables
├── notebooks/        # Jupyter notebooks for EDA and experimental modeling
├── src/
│   ├── data/         # Extraction & ingestion scripts (fetch_osm.py, preview_map.py)
│   ├── features/     # Feature engineering & spatial joining pipelines
│   ├── models/       # Demand forecasting models (Prophet, scikit-learn, statsmodels)
│   └── viz/          # Interactive visualization modules & mapping helpers
├── requirements.txt  # Project dependency manifest
└── README.md         # Project documentation
```

---

## Getting Started

### 1. Prerequisites & Virtual Environment

Ensure Python 3.10+ is installed and set up a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Step 1: Data Extraction

Pull raw OpenStreetMap road network, OSM-tagged bus stops, and key Points of Interest (POIs) for Bhubaneswar:

```bash
python src/data/fetch_osm.py
```

Outputs saved to `data/raw/`:
- `bhubaneswar_road_network.graphml` (Drivable road graph)
- `bhubaneswar_roads.gpkg` (Road edges & nodes layers)
- `bhubaneswar_bus_stops_osm.gpkg` (OSM bus stops)
- `bhubaneswar_pois.gpkg` (Hospitals, colleges, universities, markets, malls, stations)

### 3. Step 2: Preview Network Map

Generate a static preview of the extracted road network and bus stop locations:

```bash
python src/data/preview_map.py
```

Outputs saved to `data/interim/`:
- `bhubaneswar_network_preview.png`
