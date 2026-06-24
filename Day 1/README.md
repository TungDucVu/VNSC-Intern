# Day 1: Hanoi Administrative Districts NDVI & NDBI Analysis (2023-2024)

This folder contains the work completed for Day 1 of the internship. The objective was to analyze vegetation (NDVI) and built-up/urban indices (NDBI) for all administrative districts of Hanoi using satellite imagery from Sentinel-2 and Landsat 8.

## Folder Structure
- **`Day1.ipynb`**: The main Jupyter Notebook containing the full Earth Engine pipeline designed to run in Google Colab.
- **`hanoi_district_indices.csv`**: The output table containing the calculated mean NDVI and NDBI values for each Hanoi district/town from both Sentinel-2 and Landsat 8 composites.
- **`objective.txt`**: The original text file containing the requirements/tasks for Day 1.

---

## Technical Methodology

### 1. Vector Boundaries
- **Source**: Administrative district boundaries GeoJSON from the Open Development Mekong database.
- **Filter**: Filtered for `Ten_Tinh == 'Hà Nội'` to extract the 29 districts/towns of Hanoi.
- **GEE Loading**: Converted the filtered GeoDataFrame to an Earth Engine `FeatureCollection` using `geemap.gdf_to_ee()`.

### 2. Raster Collections & Composites
- **Sentinel-2**: `COPERNICUS/S2_SR_HARMONIZED`
  - Filtered by boundaries and dates (2023-01-01 to 2024-12-31).
  - Filtered for cloud cover less than 10%.
  - Cloud masked using the `QA60` band.
  - Calculated NDVI and NDBI.
  - Reduced to a single image using the `median()` reducer.
- **Landsat 8**: `LANDSAT/LC08/C02/T1_L2`
  - Filtered by boundaries and dates (2023-01-01 to 2024-12-31).
  - Filtered for cloud cover less than 10%.
  - Cloud masked using the `QA_PIXEL` band.
  - Scaled optical bands to reflectance range [0, 1].
  - Calculated NDVI and NDBI.
  - Reduced to a single image using the `median()` reducer.

### 3. Spectral Indices
- **NDVI** (Normalized Difference Vegetation Index):
  - Formula: $\text{NDVI} = \frac{\text{NIR} - \text{Red}}{\text{NIR} + \text{Red}}$
  - Sentinel-2 Bands: `B8` (NIR) and `B4` (Red)
  - Landsat 8 Bands: `SR_B5` (NIR) and `SR_B4` (Red)
- **NDBI** (Normalized Difference Built-up Index):
  - Formula: $\text{NDBI} = \frac{\text{SWIR1} - \text{NIR}}{\text{SWIR1} + \text{NIR}}$
  - Sentinel-2 Bands: `B11` (SWIR1) and `B8` (NIR)
  - Landsat 8 Bands: `SR_B6` (SWIR1) and `SR_B5` (NIR)

### 4. Region Reduction
- Computed the average (mean) NDVI and NDBI value for each of the 29 districts using Earth Engine's `.reduceRegions()` reducer with a scale of 10 meters for Sentinel-2 and 30 meters for Landsat 8.

### 5. Interactive Visualization
- Utilized the `geemap` library to render an interactive map interface within the notebook.
- Overlaid the calculated Sentinel-2 and Landsat 8 NDVI and NDBI median composites using specific color palettes (e.g., green-white-red for NDBI).
- Displayed the administrative district boundaries of Hanoi as an outline for spatial context.

---

## Analysis & Key Findings

1. **Urban Core vs. Rural Fringe**:
   - Central districts like **Đống Đa** and **Hai Bà Trưng** exhibit high built-up values (NDBI > 0.05) and low vegetation indices (NDVI < 0.20), representing heavily paved, high-density urban areas.
   - Outer districts like **Thạch Thất** and **Ba Vì** have very high greenness (NDVI > 0.50) and low built-up indices (NDBI < -0.11), showcasing dense forest/shrub vegetation and low artificial cover.
2. **Sentinel-2 vs. Landsat 8 Comparison**:
   - Both satellites show high correlation in indexing trends.
   - Sentinel-2's 10m spatial resolution provides finer mapping boundaries compared to Landsat 8's 30m resolution.
   - Landsat 8 NDBI values are shifted more negatively compared to Sentinel-2, likely due to differences in sensor-specific band wavelengths and atmospheric corrections.
