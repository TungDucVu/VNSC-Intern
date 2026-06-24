# Day 1: Hanoi Administrative Districts NDVI & NDBI Analysis (2023-2024)

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/TungDucVu/VNSC-Intern/blob/main/Day1.ipynb)

This folder contains the work completed for Day 1 of the internship. The objective was to analyze vegetation (NDVI) and built-up/urban indices (NDBI) for all administrative districts of Hanoi using satellite imagery from Sentinel-2 and Landsat 8.

## Folder Structure
- **`Day1.ipynb`**: The main Jupyter Notebook containing the full Earth Engine pipeline, designed to run in Google Colab.
- **`hanoi_district_indices.csv`**: The output table containing `Code_Vung`, `District_Name`, `Population_2009`, and the calculated mean NDVI & NDBI values for each of the 30 Hanoi districts/towns from both Sentinel-2 and Landsat 8 composites.
- **`objective.txt`**: The original text file containing the requirements/tasks for Day 1.

---

## Prerequisites & How to Run

1. Open `Day1.ipynb` in **Google Colab** via the badge above.
2. Ensure you have a valid **Google Earth Engine** project. Update the `project` ID in the initialization cell if needed:
   ```python
   ee.Initialize(project='your-gee-project-id')
   ```
3. Run all cells sequentially. The notebook will:
   - Install required packages (`earthengine-api`, `geemap`, `geopandas`, `pandas`)
   - Authenticate and initialize GEE
   - Download and process data
   - Save results to `hanoi_district_indices.csv`
   - Display an interactive map

---

## Technical Methodology

### 1. Vector Boundaries
- **Source**: Administrative district boundaries GeoJSON from the Open Development Mekong database.
- **Filter**: Filtered for `Ten_Tinh == 'Hà Nội'` to extract the **30** districts/towns of Hanoi.
- **GEE Loading**: Converted the filtered GeoDataFrame to an Earth Engine `FeatureCollection` using `geemap.gdf_to_ee()`.

### 2. Raster Collections & Composites
- **Sentinel-2**: `COPERNICUS/S2_SR_HARMONIZED`
  - Filtered by boundaries and dates (2023-01-01 to 2024-12-31).
  - Filtered for cloud cover less than 10% (`CLOUDY_PIXEL_PERCENTAGE`).
  - Cloud masked using the `QA60` band (cloud and cirrus bits).
  - Calculated NDVI and NDBI per image.
  - Reduced to a single image using the `median()` reducer.
- **Landsat 8**: `LANDSAT/LC08/C02/T1_L2`
  - Filtered by boundaries and dates (2023-01-01 to 2024-12-31).
  - Filtered for cloud cover less than 10% (`CLOUD_COVER`).
  - Cloud and cloud-shadow masked using the `QA_PIXEL` band.
  - Scaled optical bands to surface reflectance range [0, 1] (`× 0.0000275 + (−0.2)`).
  - Calculated NDVI and NDBI per image.
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
- Computed the average (mean) NDVI and NDBI value for each of the 30 districts using Earth Engine's `.reduceRegions()` reducer.
- Scale: **10 meters** for Sentinel-2, **30 meters** for Landsat 8.
- Results were merged with district metadata (`Code_Vung`, `Population_2009`) and exported to CSV.

### 5. Interactive Visualization
- Utilized the `geemap` library to render an interactive map interface within the notebook.

- Displayed the administrative district boundaries of Hanoi as a red outline for spatial context.

---

## Analysis & Key Findings

1. **Urban Core vs. Rural Fringe**:
   - Central districts like **Đống Đa** (S2 NDVI ≈ 0.19, NDBI ≈ 0.13) and **Hai Bà Trưng** (S2 NDVI ≈ 0.14, NDBI ≈ 0.06) exhibit high built-up values and low vegetation, representing heavily paved, high-density urban areas.
   - Outer districts like **Thạch Thất** (S2 NDVI ≈ 0.52) and **Ba Vì** (S2 NDVI ≈ 0.51) have very high greenness and strongly negative NDBI values, showcasing dense forest/shrub vegetation and minimal artificial cover.
2. **Sentinel-2 vs. Landsat 8 Comparison**:
   - Both satellites show high correlation in indexing trends across all 30 districts.
   - Sentinel-2's 10m spatial resolution provides finer mapping boundaries compared to Landsat 8's 30m resolution.
   - Landsat 8 NDBI values are consistently shifted more negatively compared to Sentinel-2, likely due to differences in sensor-specific band wavelengths and atmospheric correction algorithms.
