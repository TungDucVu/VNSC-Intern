# Academic LULC Pipeline for Hanoi (Alternative Plan)

This directory contains the implementation of an academic-grade Land Use / Land Cover (LULC) classification pipeline for Hanoi. It shifts the methodology from manual polygon-based sampling to automated stratified sampling based on the **ESA WorldCover 2021** dataset, integrates topographical features (Elevation, Slope) from the **ALOS AW3D30 DEM**, and trains a Random Forest model with post-processing noise reduction.

---

## 1. Classification Methodology

The alternative classification pipeline consists of 5 main stages:

### Stage 1: Data Acquisition & Preprocessing
* **Satellite Imagery**: Sentinel-2 (Level-2A) surface reflectance imagery composited for the dry season (January 1st – March 31st) of 2021 (training reference year) and 2024 (target year).
* **Cloud Masking**: QA60 cloud mask applied to eliminate thick clouds and cirrus.
* **Resampling**: Mapped `.resample('bicubic')` over individual collection images to preserve native UTM projections and prevent GEE scale fallback during composite generation.
* **Topographical Features**: Integrated elevation and slope from JAXA's **ALOS AW3D30 DEM** at 30m resolution, resampled to 10m.

### Stage 2: Feature Engineering
A total of **11 predictive features** are fed into the classifier:
* **Spectral Bands**: Blue (`B2`), Green (`B3`), Red (`B4`), Near-Infrared (`B8`), SWIR-1 (`B11`), and SWIR-2 (`B12`).
* **Spectral Indices**:
  * NDVI (Normalized Difference Vegetation Index) for vegetation.
  * NDBI (Normalized Difference Built-Up Index) for urban/built surfaces.
  * MNDWI (Modified Normalized Difference Water Index) for open water.
* **Topographical Indices**: Elevation (DSM) and Slope.

### Stage 3: Automated Stratified Sampling
* **Reference Labels**: **ESA WorldCover 2021 (10m)** reclassified from 11 global classes into 5 local classes:
  * `0`: Water (Open water, class 80)
  * `1`: Urban (Built-up, class 50)
  * `2`: Agriculture (Cropland, class 40)
  * `3`: Greenery (Trees, Shrubland, Grassland, Herbaceous wetland, classes 10, 20, 30, 90, 95)
  * `4`: Bare Land (Barren / sparse vegetation, class 60, 100)
* **Sampling**: `.stratifiedSample()` executed on the 2021 Sentinel-2 composite over Hanoi using the reclassified ESA map. A total of **800 points per class** were selected.
* **Water Signature Update**: 50 hand-digitized water pixels sampled from the 2024 Red River to capture the 2024 spectral signature of turbid river water.

### Stage 4: Model Training & Validation
* **Model**: Random Forest classifier configured with **150 decision trees** (`ee.Classifier.smileRandomForest`).
* **Split**: 70% of the sample pool used for training, 30% held out for validation.

### Stage 5: Post-Processing
To eliminate classification errors and spatial noise, two filters were applied:
1. **Focal Mode**: A 1-pixel circular focal mode filter (`.focalMode(1, 'circle')`) to smooth out isolated "salt-and-pepper" pixels.
2. **Water Masking**: Permanently forced ESA WorldCover's permanent water bodies (class 80) into the final LULC water layer using `.where()`.

---

## 2. Validation Metrics (70/30 Split)

* **Overall Accuracy (OA)**: **74.31%**
* **Kappa Coefficient**: **0.6786**

### Confusion Matrix
```text
Class       | Water (0) | Urban (1) | Agri (2) | Green (3) | Bare (4)
Water (0)   |    187    |     1     |    11    |     4     |    31
Urban (1)   |      0    |   174     |    19    |    16     |    26
Agri (2)    |      5    |    23     |   165    |    30     |    22
Green (3)   |      2    |    23     |    31    |   207     |     4
Bare (4)    |     14    |    20     |    30    |     3     |   178
```

*Note: The misclassifications between Water/Bare Land and Urban/Bare Land reflect physical ground truths during the dry season (exposed dry riverbeds, construction sites, and bare agricultural fields).*

---

## 3. Directory Deliverables
* 📄 **[classify_hanoi.py](classify_hanoi.py)**: Python script executing the entire GEE pipeline, calculating statistics, and building the interactive Folium map.
* 📄 **[hanoi_lulc_district_areas.csv](hanoi_lulc_district_areas.csv)**: Zonal statistics of LULC class areas ($km^2$) for Hanoi's 29 districts computed at 10m scale.
* 📄 **[hanoi_lulc_interactive.html](hanoi_lulc_interactive.html)**: Interactive Folium map with district boundaries, urbanization tooltips, a 5-class color scheme, and map legend.

---

## 4. How to Run

Ensure the `hanoi_gis` conda environment is active, then run:

```bash
python LULC_Alternative/classify_hanoi.py
```
