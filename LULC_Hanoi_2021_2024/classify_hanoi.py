################################################################################# # Quy trình Phân loại Lớp phủ LULC Hà Nội Cấp học thuật (Alternative Plan)# # Notebook này thực hiện quy trình phân loại lớp phủ bề mặt (Land Use / Land Cover - LULC) cấp học thuật cho thành phố Hà Nội. Quy trình này chuyển đổi phương pháp từ lấy mẫu đa giác thủ công sang lấy mẫu phân tầng tự động dựa trên bộ dữ liệu **ESA WorldCover 2021**, tích hợp các đặc trưng địa hình (Độ cao, Độ dốc) từ dữ liệu **ALOS AW3D30 DEM**, và huấn luyện mô hình **Random Forest (150 cây)** trên **Google Earth Engine (GEE)** kết hợp với các bộ lọc hậu xử lý giảm nhiễu.################################################################################
################################################################################# ## 1. Khởi tạo Google Earth Engine (GEE)# # Chúng ta sẽ import các thư viện cần thiết và khởi tạo kết nối với Google Earth Engine API.################################################################################
import os
import sys
import ee
import geopandas as gpd
import pandas as pd
import geemap
import folium

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

print("Initializing Google Earth Engine...")
try:
    ee.Initialize(project='crested-library-500309-i2')
    print("GEE Initialized Successfully!")
except Exception as e:
    print("Failed to initialize GEE, attempting authentication:", e)
    ee.Authenticate()
    ee.Initialize(project='crested-library-500309-i2')
    print("GEE Authenticated and Initialized Successfully!")

################################################################################# ## 2. Tải và lọc ranh giới hành chính Hà Nội# # Chúng ta tải ranh giới huyện của Hà Nội từ Open Development Mekong và chuyển đổi sang FeatureCollection của GEE.################################################################################
print("Loading Hanoi district boundary...")
geojson_url = "https://data.opendevelopmentmekong.net/dataset/6f054351-bf2c-422e-8deb-0a511d63a315/resource/78b3fb31-8c96-47d3-af64-d1a6e168e2ea/download/diaphanhuyen.geojson"
gdf = gpd.read_file(geojson_url)
hanoi_gdf = gdf[gdf['Ten_Tinh'] == 'Hà Nội'].copy()
hanoi_fc = geemap.gdf_to_ee(hanoi_gdf)
print(f"Loaded {len(hanoi_gdf)} districts for Hanoi.")

################################################################################# ## 3. Tiền xử lý ảnh composite Sentinel-2 và Đặc trưng Địa hình DEM# # Chúng ta xây dựng hàm tạo ảnh Sentinel-2 composite khô (từ 01/01 đến 15/02) để tránh các nhiễu sương mù dày đặc vào cuối mùa xuân ở miền Bắc. Để tránh lỗi co giãn lưới chiếu của GEE khi tính median composite, ta thực hiện nội suy `.resample('bicubic')` trực tiếp trên từng ảnh đơn lẻ của Collection.# # Ngoài ra, chúng ta tính toán thêm dữ liệu độ cao và độ dốc từ **ALOS AW3D30 DEM** làm thuộc tính địa hình độc lập.################################################################################
def get_s2_composite(year, boundary):
    start_date = f"{year}-01-01"
    end_date = f"{year}-02-15"
    
    def maskS2clouds(image):
        qa = image.select('QA60')
        cloudBitMask = 1 << 10
        cirrusBitMask = 1 << 11
        mask = qa.bitwiseAnd(cloudBitMask).eq(0).And(qa.bitwiseAnd(cirrusBitMask).eq(0))
        masked = image.updateMask(mask)
        # Resample individual image so that it retains native spatial projection and scale
        return masked.resample('bicubic')

    s2_col = (ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
              .filterBounds(boundary)
              .filterDate(start_date, end_date)
              .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20)))
    
    base_image = s2_col.sort('CLOUDY_PIXEL_PERCENTAGE').limit(10).map(maskS2clouds).median().select(['B2', 'B3', 'B4', 'B8', 'B11', 'B12']).clip(boundary)
    
    ndvi = base_image.normalizedDifference(['B8', 'B4']).rename('NDVI')
    ndbi = base_image.normalizedDifference(['B11', 'B8']).rename('NDBI')
    mndwi = base_image.normalizedDifference(['B3', 'B11']).rename('MNDWI')
    
    # Standard deviation of NDVI for the full year
    full_year_col = (ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
                     .filterBounds(boundary)
                     .filterDate(f"{year}-01-01", f"{year}-12-31")
                     .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20)))
    
    def calculate_ndvi(img):
        qa = img.select('QA60')
        cloudBitMask = 1 << 10
        cirrusBitMask = 1 << 11
        mask = qa.bitwiseAnd(cloudBitMask).eq(0).And(qa.bitwiseAnd(cirrusBitMask).eq(0))
        masked = img.updateMask(mask).resample('bicubic')
        return masked.normalizedDifference(['B8', 'B4']).rename('NDVI')
        
    ndvi_stddev = full_year_col.map(calculate_ndvi).reduce(ee.Reducer.stdDev()).rename('NDVI_stdDev').clip(boundary)
    
    # GLCM Contrast on composite B8 band scaled to 8-bit
    b8_scaled = base_image.select('B8').divide(40).toInt()
    glcm = b8_scaled.glcmTexture(size=1)
    b8_contrast = glcm.select('B8_contrast')
    
    # Scale bands to 0-1 for EVI, SAVI, BSI formulas
    b2 = base_image.select('B2').divide(10000.0)
    b4 = base_image.select('B4').divide(10000.0)
    b8 = base_image.select('B8').divide(10000.0)
    b11 = base_image.select('B11').divide(10000.0)
    
    # Enhanced Vegetation Index (EVI)
    evi = base_image.expression(
        '2.5 * ((B8 - B4) / (B8 + 6.0 * B4 - 7.5 * B2 + 1.0))',
        {'B8': b8, 'B4': b4, 'B2': b2}
    ).rename('EVI')
    
    # Soil Adjusted Vegetation Index (SAVI)
    savi = base_image.expression(
        '((B8 - B4) / (B8 + B4 + 0.5)) * 1.5',
        {'B8': b8, 'B4': b4}
    ).rename('SAVI')
    
    # Bare Soil Index (BSI)
    bsi = base_image.expression(
        '((B11 + B4) - (B8 + B2)) / ((B11 + B4) + (B8 + B2))',
        {'B11': b11, 'B4': b4, 'B8': b8, 'B2': b2}
    ).rename('BSI')
    
    return base_image.addBands([ndvi, ndbi, mndwi, ndvi_stddev, b8_contrast, evi, savi, bsi])

print("Querying and compositing Sentinel-2 imagery...")
# Load DEM and calculate slope
dem = ee.ImageCollection('JAXA/ALOS/AW3D30/V4_1').mosaic().select('DSM').rename('elevation')
slope = ee.Terrain.slope(dem).rename('slope')
dem_features = dem.addBands(slope).clip(hanoi_fc)

s2_2021 = get_s2_composite(2021, hanoi_fc).addBands(dem_features)
s2_2024 = get_s2_composite(2024, hanoi_fc).addBands(dem_features)
print("Imagery and DEM composites prepared successfully!")

################################################################################# ## 4. Tải và phân loại lại bản đồ tham chiếu ESA WorldCover# # Chúng ta reclassify dữ liệu ESA WorldCover từ 11 lớp toàn cầu thành 5 lớp mục tiêu cục bộ: Nước (0), Đô thị (1), Nông nghiệp (2), Cây xanh (3), và Đất trống (4).################################################################################
print("Loading and reclassifying ESA WorldCover 2021...")
esa = ee.ImageCollection('ESA/WorldCover/v200').first().clip(hanoi_fc)
from_list = [10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 100]
to_list = [3, 3, 3, 2, 1, 4, 4, 0, 3, 3, 4]
reclassified_esa = esa.select('Map').remap(from_list, to_list).rename('class')

################################################################################# ## 5. Lấy mẫu Phân tầng Tự động (Stratified Sampling) và chia tập dữ liệu# # Sử dụng bản đồ nhãn ESA reclassified để lấy ngẫu nhiên 800 mẫu cho mỗi lớp phủ ở độ phân giải 10m trên toàn bộ Hà Nội. Để làm giàu phổ nước đục cho năm 2024, ta ghép thêm 50 mẫu nước mặt trên sông Hồng số hóa thủ công. Dữ liệu sau đó được chia theo tỷ lệ **70% huấn luyện (Train set)** và **30% kiểm thử độc lập (Test set)**.################################################################################
print("Running stratified sampling on 2021 composite...")
image_with_class_2021 = s2_2021.addBands(reclassified_esa)

samples_2021 = image_with_class_2021.stratifiedSample(
    numPoints=2500,
    classBand='class',
    region=hanoi_fc.geometry(),
    scale=10,
    seed=42,
    classValues=[0, 1, 2, 3, 4],
    classPoints=[2000, 1500, 1500, 1500, 2500],
    geometries=True
)

# Mẫu nước bổ sung từ sông Hồng năm 2024
water_poly = ee.Geometry.Polygon([[105.842, 21.082], [105.846, 21.082], [105.846, 21.086], [105.842, 21.086]])
water_samples_2024 = s2_2024.sample(
    region=water_poly,
    scale=10,
    numPixels=50,
    seed=42,
    geometries=True
).map(lambda f: f.set('class', 0))

# Ghép mẫu
combined_samples = samples_2021.merge(water_samples_2024)

# Lọc sạch nhãn nhiễu (mismatch giữa nhãn bản đồ tham chiếu và ảnh dry-season thực tế)
water_filter = ee.Filter.Or(
    ee.Filter.neq('class', 0),
    ee.Filter.gt('MNDWI', -0.05)
)
green_filter = ee.Filter.Or(
    ee.Filter.neq('class', 3),
    ee.Filter.gt('NDVI', 0.25)
)
bare_filter = ee.Filter.Or(
    ee.Filter.neq('class', 4),
    ee.Filter.And(
        ee.Filter.lt('MNDWI', 0.0),
        ee.Filter.lt('NDVI', 0.3)
    )
)
cleaned_samples = combined_samples.filter(water_filter).filter(green_filter).filter(bare_filter)

# Chia 70/30
samples_with_random = cleaned_samples.randomColumn('random', seed=42)
train_set = samples_with_random.filter(ee.Filter.lt('random', 0.7))
test_set = samples_with_random.filter(ee.Filter.gte('random', 0.7))
print(f"Train samples: {train_set.size().getInfo()}")
print(f"Test samples: {test_set.size().getInfo()}")

################################################################################# ## 6. Huấn luyện và Đánh giá độ chính xác mô hình Random Forest# # Chúng ta huấn luyện mô hình học máy Random Forest với **200 cây quyết định** và thực hiện đánh giá độ chính xác trên tập kiểm thử độc lập.################################################################################
features = ['B2', 'B3', 'B4', 'B8', 'B11', 'B12', 'NDVI', 'NDBI', 'MNDWI', 'elevation', 'slope', 'NDVI_stdDev', 'B8_contrast', 'EVI', 'SAVI', 'BSI']
print("Huấn luyện Random Forest 200 cây...")
classifier = ee.Classifier.smileRandomForest(200).train(
    features=train_set,
    classProperty='class',
    inputProperties=features
)

# Đánh giá
validated = test_set.classify(classifier)
error_matrix = validated.errorMatrix('class', 'classification')
accuracy = error_matrix.accuracy().getInfo()
kappa = error_matrix.kappa().getInfo()
matrix = error_matrix.getInfo()

print("=== KẾT QUẢ ĐÁNH GIÁ MÔ HÌNH (70/30 SPLIT) ===")
print(f"Overall Accuracy (OA): {accuracy * 100:.2f}%")
print(f"Kappa Coefficient: {kappa:.4f}")
print("Confusion Matrix:")
for row in matrix:
    print(row)

################################################################################# ## 7. Phân loại LULC năm 2024 và Hậu xử lý bộ lọc# # Chúng ta áp dụng mô hình phân loại lên composite năm 2024. Để tối ưu hóa chất lượng, chúng ta áp dụng:# 1. **Bộ lọc Focal Mode (bán kính 1px)**: Loại bỏ các pixel nhiễu cục bộ.# 2. **Ép mặt nạ nước ESA**: Khôi phục chính xác dòng chảy các con sông chính từ bộ nhãn nước vĩnh cửu của ESA WorldCover.################################################################################
print("Classifying 2024 composite...")
classified_2024 = s2_2024.classify(classifier)

print("Applying post-processing filters (Focal Mode & Water Mask)...")
classified_smooth = classified_2024.focalMode(radius=1, kernelType='circle')
final_classified = classified_smooth.where(esa.select('Map').eq(80), 0)
print("Classification and filtering complete!")

################################################################################# ## 8. Thống kê diện tích lớp phủ của các Quận/Huyện ở độ phân giải 10m# # Dùng raster `pixelArea()` và `reduceRegions()` ở scale 10m để thống kê diện tích từng lớp phủ ($km^2$) cho 29 quận/huyện của Hà Nội.################################################################################
print("Calculating district LULC areas at 10m scale...")
areas_list = []
for c in range(5):
    class_area = ee.Image.pixelArea().updateMask(final_classified.eq(c)).divide(1e6).rename(f'class_{c}_area')
    areas_list.append(class_area)

areas_image = ee.Image.cat(areas_list)

district_areas = areas_image.reduceRegions(
    collection=hanoi_fc,
    reducer=ee.Reducer.sum(),
    scale=10
)

print("Downloading area statistics...")
df = geemap.ee_to_df(district_areas)
print("Dataframe built successfully!")

################################################################################# ## 9. Định dạng và xuất dữ liệu thống kê ra file CSV# # Chúng ta sắp xếp cột, đổi tên nhãn và tính tổng diện tích để xuất bảng báo cáo diện tích chi tiết.################################################################################
df_clean = pd.DataFrame()
df_clean['Code_Vung'] = df['Code_vung']
df_clean['District_Name'] = df['Ten_Huyen']
df_clean['Water_Area_km2'] = df['class_0_area']
df_clean['Urban_Area_km2'] = df['class_1_area']
df_clean['Agriculture_Area_km2'] = df['class_2_area']
df_clean['Greenery_Area_km2'] = df['class_3_area']
df_clean['Bare_Land_Area_km2'] = df['class_4_area']

# Tính tổng
df_clean['Total_LULC_Area_km2'] = (
    df_clean['Water_Area_km2'] + 
    df_clean['Urban_Area_km2'] + 
    df_clean['Agriculture_Area_km2'] + 
    df_clean['Greenery_Area_km2'] + 
    df_clean['Bare_Land_Area_km2']
)

df_clean = df_clean.sort_values('Code_Vung').reset_index(drop=True)

csv_output = "hanoi_lulc_district_areas.csv"
df_clean.to_csv(csv_output, index=False, encoding='utf-8')
print(f"Area statistics exported successfully to '{csv_output}'!")
print(df_clean.head(10))

################################################################################# ## 10. Trực quan hóa bản đồ tương tác lớp phủ LULC với Folium# # Chúng ta tạo một bản đồ tương tác sử dụng Folium hiển thị ranh giới quận huyện, lớp phân loại LULC và tooltip hiển thị diện tích chi tiết và tỷ lệ đô thị hóa khi di chuột qua quận huyện đó.################################################################################
print("Generating interactive Folium map...")
merged_gdf = hanoi_gdf.merge(df_clean, left_on='Ten_Huyen', right_on='District_Name')
merged_gdf['Urban_Pct'] = (merged_gdf['Urban_Area_km2'] / merged_gdf['Total_LULC_Area_km2']) * 100

m = folium.Map(location=[21.0285, 105.8542], zoom_start=10, control_scale=True)

# Google Satellite basemap
folium.TileLayer(
    tiles="https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
    attr="Google",
    name="Google Satellite",
    overlay=False
).add_to(m)

# GEE classified map layer
map_id = final_classified.getMapId({'min': 0, 'max': 4, 'palette': ['0000ff', 'ff0000', 'ffff00', '008000', 'a0522d']})
folium.TileLayer(
    tiles=map_id['tile_fetcher'].url_format,
    attr="Google Earth Engine",
    name="Hanoi LULC Map (Alternative)",
    overlay=True,
    opacity=0.75
).add_to(m)

# Boundary styling
def style_function(feature):
    return {
        'fillColor': '#ffffff',
        'color': '#000000',
        'fillOpacity': 0.0,
        'weight': 1.5
    }

def highlight_function(feature):
    return {
        'fillColor': '#000000',
        'color': '#ff0000',
        'fillOpacity': 0.1,
        'weight': 2.0
    }

folium.GeoJson(
    merged_gdf.to_json(),
    name="Hanoi Districts",
    style_function=style_function,
    highlight_function=highlight_function,
    tooltip=folium.GeoJsonTooltip(
        fields=['Ten_Huyen', 'Urban_Area_km2', 'Bare_Land_Area_km2', 'Total_LULC_Area_km2', 'Urban_Pct'],
        aliases=['District:', 'Urban Area (km²):', 'Bare Land Area (km²):', 'Total Area (km²):', 'Urbanization (%):'],
        localize=True,
        sticky=False,
        labels=True,
        style="""
            background-color: #F0F2F6;
            border: 2px solid #31333F;
            font-family: sans-serif;
            font-size: 13px;
        """
    )
).add_to(m)

# HTML Legend
legend_html = '''
     <div style="position: fixed; 
     bottom: 50px; left: 50px; width: 220px; height: 210px; 
     border: 1px solid rgba(0,0,0,0.2); z-index:9999; font-size:13px;
     background-color: rgba(255, 255, 255, 0.95);
     backdrop-filter: blur(5px);
     box-shadow: 0 0 15px rgba(0,0,0,0.2);
     border-radius: 8px;
     padding: 12px;
     font-family: Arial, sans-serif;
     line-height: 1.5;">
     <b style="font-size: 14px; display: block; margin-bottom: 8px; color: #333;">Lớp Phủ LULC Hà Nội</b>
     <div style="display: flex; align-items: center; margin-bottom: 8px;">
         <span style="background:#0000FF; width: 18px; height: 18px; display: inline-block; margin-right: 8px; border: 1px solid #555; border-radius: 3px;"></span>
         <span>Water (Nước)</span>
     </div>
     <div style="display: flex; align-items: center; margin-bottom: 8px;">
         <span style="background:#FF0000; width: 18px; height: 18px; display: inline-block; margin-right: 8px; border: 1px solid #555; border-radius: 3px;"></span>
         <span>Urban (Đô thị)</span>
     </div>
     <div style="display: flex; align-items: center; margin-bottom: 8px;">
         <span style="background:#FFFF00; width: 18px; height: 18px; display: inline-block; margin-right: 8px; border: 1px solid #555; border-radius: 3px;"></span>
         <span>Agriculture (Nông nghiệp)</span>
     </div>
     <div style="display: flex; align-items: center; margin-bottom: 8px;">
         <span style="background:#008000; width: 18px; height: 18px; display: inline-block; margin-right: 8px; border: 1px solid #555; border-radius: 3px;"></span>
         <span>Greenery (Cây xanh)</span>
     </div>
     <div style="display: flex; align-items: center; margin-bottom: 4px;">
         <span style="background:#A0522D; width: 18px; height: 18px; display: inline-block; margin-right: 8px; border: 1px solid #555; border-radius: 3px;"></span>
         <span>Bare Land (Đất trống)</span>
     </div>
     </div>
     '''
m.get_root().html.add_child(folium.Element(legend_html))
folium.LayerControl().add_to(m)

html_output = "hanoi_lulc_interactive.html"
m.save(html_output)
print(f"Interactive Folium map saved to '{html_output}' successfully!")

