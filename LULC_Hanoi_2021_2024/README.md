# Academic-Grade LULC Classification Pipeline for Hanoi (2021 - 2024)

This repository contains the source code implementing an academic-grade Land Use / Land Cover (LULC) classification pipeline for Hanoi. The methodology transitions from manual polygon digitizing to automated stratified sampling based on the **ESA WorldCover 2021** dataset, integrates topographic features (Elevation, Slope) from the **ALOS AW3D30 DEM**, and trains a **Random Forest (200 trees)** classifier on **Google Earth Engine (GEE)** combined with post-processing noise reduction filters.

---

## 1. Classification Methodology

The classification pipeline consists of 5 main stages:

### Stage 1: Data Acquisition & Pre-processing
* **Satellite Imagery**: Sentinel-2 Surface Reflectance (Level-2A) image composites are generated for the dry season (January 1st to February 15th) for 2021 (baseline year for sampling) and 2024 (target year for classification).
* **Cloud Masking**: A QA60 cloud mask is applied to remove thick clouds and cirrus.
* **Resampling**: To prevent GEE from automatically downsampling the imagery to a coarse 1-degree resolution during median compositing, `.resample('bicubic')` is applied directly to each individual image within the ImageCollection to preserve the native UTM projection and 10m grid.
* **Topographic Features**: Elevation and slope data from JAXA's **ALOS AW3D30 DEM** (originally 30m resolution) are integrated and resampled to 10m.

### Stage 2: Feature Selection & Engineering
A total of **16 predictor features** are input into the classifier:
* **Spectral Bands**: Blue (`B2`), Green (`B3`), Red (`B4`), Near-Infrared (`B8`), SWIR-1 (`B11`), and SWIR-2 (`B12`).
* **Spectral Indices**:
  * **NDVI** (Normalized Difference Vegetation Index): For identifying greenery/vegetation.
  * **NDBI** (Normalized Difference Build-up Index): For identifying urban/built-up surfaces.
  * **MNDWI** (Modified Normalized Difference Water Index): For identifying surface water bodies.
  * **EVI** (Enhanced Vegetation Index): To improve differentiation of dense vegetation structures.
  * **SAVI** (Soil Adjusted Vegetation Index): Adjusts for soil background brightness in sparse areas.
  * **BSI** (Bare Soil Index): Enhances identification of construction sites and dry agricultural land.
* **Topographic Indices**: Elevation (`elevation`) and Slope (`slope`).
* **Temporal Variation Feature**: `NDVI_stdDev` (the standard deviation of NDVI over the entire year) helps distinguish seasonal cropland from stable urban areas or river sandbars.
* **Spatial Texture Feature**: `B8_contrast` (GLCM contrast of the NIR B8 band) helps differentiate smooth riverbed sandbars from the complex, high-contrast textures of urban structures.

### Stage 3: Automated Stratified Sampling & Noise Filtering
* **Reference Labels**: The **ESA WorldCover 2021 (10m)** dataset is reclassified from 11 global classes to 5 local target classes:
  * `0`: Water (Open water - ESA class 80)
  * `1`: Urban (Built-up - ESA class 50)
  * `2`: Agriculture (Cropland - ESA class 40)
  * `3`: Greenery (Trees, Shrubland, Grassland, Herbaceous wetland - ESA classes 10, 20, 30, 90, 95)
  * `4`: Bare Land (Barren / sparse vegetation - ESA classes 60, 100)
* **Sampling**: The `.stratifiedSample()` function is executed on the 2021 Sentinel-2 composite over Hanoi using the reclassified ESA map:
  * Total stratified sample points: **2,500 points** (maximum allocation: [2000, 1500, 1500, 1500, 2500])
* **Spectral Filtering**: To eliminate reference label noise caused by seasonal mismatches (e.g., dry river sandbars mislabeled as Water by the static ESA WorldCover map), physical index filters are applied:
  * Water samples must satisfy `MNDWI > -0.05`.
  * Greenery samples must satisfy `NDVI > 0.25`.
  * Bare Land samples must satisfy `MNDWI < 0` and `NDVI < 0.3`.
* **Water Sample Enrichment**: An additional 50 manually digitized water pixels on the Red River from 2024 are merged to capture turbid water spectral profiles.
* **Train/Test Split**: 70% of clean samples are used for training, and 30% are reserved for independent testing.

### Stage 4: Model Training & Validation
* **Model**: A Random Forest classifier configured with **200 decision trees** (`ee.Classifier.smileRandomForest(200)`).
* **Validation**: Evaluated using the independent 30% test split.

### Stage 5: Post-processing
To eliminate salt-and-pepper noise and spatial classification errors, two filters are applied:
1. **Spatial Mode Filter (Focal Mode)**: A circular focal mode filter with a 1-pixel radius (`.focalMode(1, 'circle')`) is applied to smooth out isolated misclassified pixels.
2. **Water Masking**: Permanent water bodies from ESA WorldCover (class 80) are forced into the final LULC map using `.where()` to guarantee the high-fidelity representation of the main flow of the Red River.

---

## 2. Accuracy Assessment Results (70/30 Split)

After integrating spectral indices (EVI, SAVI, BSI) and spectral filtering:
* **Overall Accuracy (OA)**: **83.48%**
* **Kappa Coefficient**: **0.7930**

### Confusion Matrix
```text
Actual \ Predicted | Water (0) | Urban (1) | Agriculture (2) | Greenery (3) | Bare Land (4)
Water (0)          |    533    |     0     |       18        |      0       |      5
Urban (1)          |      2    |   353     |       18        |     34       |     61
Agriculture (2)    |     16    |    16     |      344        |     54       |     11
Greenery (3)       |      1    |    32     |       57        |    347       |      2
Bare Land (4)      |      1    |    41     |       17        |      0       |    383
```

---

## 3. Directory Deliverables
* 📄 **[classify_hanoi.py](classify_hanoi.py)**: Python script executing the classification pipeline from start to finish and exporting results.
* 📄 **[classify_hanoi.ipynb](classify_hanoi.ipynb)**: Detailed Jupyter Notebook preserving the execution outputs and visualizations.
* 📄 **[hanoi_lulc_district_areas.csv](hanoi_lulc_district_areas.csv)**: Detailed area statistics ($km^2$) for the 5 LULC classes calculated at 10m scale for the 29 districts of Hanoi.
* 📄 **[hanoi_lulc_interactive.html](hanoi_lulc_interactive.html)**: Interactive Folium map displaying district boundaries, a 5-class LULC overlay, custom legend, and tooltips showing urbanization rate on hover.

---

## 4. GEE Map Tile Expiration (Important Note)

> [!WARNING]
> The LULC classification overlay on the interactive map (`hanoi_lulc_interactive.html`) is loaded dynamically from Google Earth Engine using a temporary Map ID. **These GEE Map IDs automatically expire after 36 to 72 hours.**
> 
> If the LULC overlay does not appear when opening the HTML file, the Map ID has expired. You can regenerate the files with fresh, active Map IDs by running the pipeline again.

---

## 5. How to Run

Ensure that the environment containing Python and dependencies (`ee`, `geemap`, `folium`, `geopandas`, `pandas`, `rasterio`) is set up:

```bash
# Run the Python script to regenerate map and CSV area statistics
python classify_hanoi.py
```
