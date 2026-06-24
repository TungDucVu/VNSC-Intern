import os
import geopandas as gpd
import rasterio
import matplotlib.pyplot as plt
from rasterio.plot import show
import numpy as np

# 1. Path resolution (works whether run from workspace root or Day 1 directory)
base_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else os.getcwd()
if not base_dir.endswith('Day 1'):
    day1_dir = os.path.join(base_dir, 'Day 1')
else:
    day1_dir = base_dir

shp_path = os.path.join(day1_dir, "shp_Hanoi-20260624T064257Z-3-001", "shp_Hanoi", "hc_TpHN_xa.shp")
sentinel_dir = os.path.join(day1_dir, "sentinel Hanoi 2024")

print("1. Vector Loading: Reading commune polygon shapefile...")
gdf = gpd.read_file(shp_path)
print(f"   Loaded {len(gdf)} communes.")

print("2. Raster Reading & Downsampling: Opening Sentinel-2 True Color bands...")
downsample_factor = 10

# Read and downsample Red band (B4)
band4_path = os.path.join(sentinel_dir, "B4_2024_Optical.tif")
with rasterio.open(band4_path) as r_red:
    out_shape = (int(r_red.height / downsample_factor), int(r_red.width / downsample_factor))
    red_data = r_red.read(1, out_shape=out_shape, resampling=rasterio.enums.Resampling.bilinear)
    # Calculate transform for downsampled resolution
    t = r_red.transform
    transform = rasterio.Affine(t.a * downsample_factor, t.b, t.c, t.d, t.e * downsample_factor, t.f)
    crs = r_red.crs

# Read and downsample Green band (B3)
band3_path = os.path.join(sentinel_dir, "B3_2024_Optical.tif")
with rasterio.open(band3_path) as r_green:
    green_data = r_green.read(1, out_shape=out_shape, resampling=rasterio.enums.Resampling.bilinear)

# Read and downsample Blue band (B2)
band2_path = os.path.join(sentinel_dir, "B2_2024_Optical.tif")
with rasterio.open(band2_path) as r_blue:
    blue_data = r_blue.read(1, out_shape=out_shape, resampling=rasterio.enums.Resampling.bilinear)

# Stack bands to create True Color RGB composite
rgb = np.dstack((red_data, green_data, blue_data))

# Scale reflectance values (range 0-10000) for display
rgb = rgb / 4000.0
rgb = np.clip(rgb, 0, 1)

print("3. CRS Alignment & Static Map: Aligning coordinates and plotting...")
# Align shapefile CRS with the raster image CRS (both are EPSG:4326)
gdf = gdf.to_crs(crs)

# Plotting
fig, ax = plt.subplots(figsize=(12, 12))
show(rgb.transpose(2, 0, 1), transform=transform, ax=ax)
gdf.boundary.plot(ax=ax, color='red', linewidth=0.5)
ax.set_title("Hanoi Commune Boundaries overlay on Sentinel-2 True Color (2024)", fontsize=14)
ax.set_xlabel("Longitude", fontsize=11)
ax.set_ylabel("Latitude", fontsize=11)

# Save the map
output_path = os.path.join(day1_dir, "hanoi_commune_boundaries.png")
plt.savefig(output_path, dpi=150, bbox_inches='tight')
print(f"   Static map successfully saved to: {output_path}")
plt.close()
