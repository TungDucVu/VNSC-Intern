# Hanoi Urban Ecosystem & Environmental Dashboard

This interactive dashboard is a spatial and statistical analysis platform exploring the relationships between **Land Use / Land Cover (LULC)**, **Environmental Quality**, and **Urbanization Pressure** across the 29 administrative districts of Hanoi.

Developed using Leaflet, Chart.js, and Vanilla CSS, this dashboard operates completely client-side for zero maintenance and offline operability.

---

## 🌟 Key Interactive Features

The dashboard is structured into three thematic modules:

### 1. 🗺️ Tab 1: LULC Overview (Hiện trạng lớp phủ)
* **Interactive Map**: Displays the final 10m-resolution **2024 LULC classification raster overlay** (generated via Google Earth Engine and Random Forest, with 83.48% accuracy) aligned over Hanoi's district boundary vectors.
* **Pie Chart breakdown**: Displays the percentage and area (in km²) of the 5 targeted classes for the selected district:
  * 🔵 **Water (Mặt nước)**
  * 🔴 **Urban / Built-up (Đất xây dựng)**
  * 🟡 **Agriculture (Đất nông nghiệp)**
  * 🟢 **Greenery (Cây xanh)**
  * 🟤 **Bare Land (Đất trống)**
* **District Rankings**: Interactive bar chart comparing urbanization rates across all districts.

### 2. 🍃 Tab 2: Environmental Quality (Chất lượng Môi trường)
* **Air Quality Index (AQI)**: Displays the annual average AQI for the selected district (color-coded: Good, Moderate, Unhealthy).
* **Land Surface Temperature (LST)**: Shows average summer surface temperature in °C.
* **Solid Waste Footprint**: Displays daily household solid waste collection volume (tons/day).
* **UHI Visualization**: Includes a bar chart illustrating the **Urban Heat Island (UHI)** effect, comparing average surface temperatures of concrete urban surfaces vs. greenery and water bodies.
* **AQI Choropleth**: The map dynamically shifts style, color-coding districts from green to red based on their annual AQI severity.

### 3. 🏙️ Tab 3: Urban Pressure (Áp lực Đô thị)
* **Population Density**: Tracks district population density (people/km²).
* **Concretization Rate**: Computes the percentage of concrete built-up area relative to the district's total area.
* **Stormwater Flood Hotspots**: Visualizes the number of recurrent flooding points during the rainy season.
* **Drainage Threat Correlation**: Includes a scatter plot correlating **Concretization Rate (%)** with **Flood Points**, highlighting how heavy urban concreting blocks rain drainage and escalates flood frequency.
* **Concretization Choropleth**: Map dynamically shifts color-coding from green (rural) to crimson (dense concrete core).

---

## 📁 Directory Structure
```text
Dashboard/
├── index.html                   # Core dashboard web portal
├── README.md                    # Technical documentation
└── data/                        # Local GIS spatial files & boundaries
    ├── hanoi_districts.geojson  # Simplified boundaries GeoJSON (199 KB)
    ├── hanoi_districts.js       # JS-wrapped boundaries (bypasses browser CORS)
    ├── hanoi_lulc_2024.png      # GEE Random Forest static raster overlay
    └── hanoi_lulc_district_areas.csv # Raw area statistics export
```

---

## 🚀 How to Launch Locally

Since the dashboard compiles all scripts, styling, and data locally:

### Option A: Double-Click (Offline)
Simply double-click the **`index.html`** file in your local file explorer to open it in any web browser. No internet or server setup is required.

### Option B: Local Python Server (Recommended)
To run the project on a local loopback server:
1. Open terminal inside the `Dashboard` directory.
2. Start Python's built-in HTTP server:
   ```bash
   python -m http.server 8000
   ```
3. Open your browser and navigate to:
   ```text
   http://localhost:8000/index.html
   ```

---

## 📊 Methodology & Data Context
* **LULC Data**: Extracted from dry-season Sentinel-2 composites. Area statistics were computed using 10m spatial resolution directly inside Google Earth Engine.
* **AQI & Waste Metrics**: Compiled from official Hanoi statistical publications, tracking average annual PM2.5 levels and regional municipal solid waste collections.
* **LST Profiles**: Derived from Landsat-8 thermal band imagery during peak summer periods, showing a clear surface thermal contrast between built structures and vegetation canopy.
