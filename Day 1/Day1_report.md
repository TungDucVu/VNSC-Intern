# BÁO CÁO KẾT QUẢ HỌC TẬP & MỤC TIÊU DỰ ÁN (DAY 1)

Báo cáo này tổng hợp những kiến thức, kỹ năng đã tiếp thu được trong ngày đầu tiên thực tập tại VNSC, phân tích những khó khăn kỹ thuật cốt lõi và đề ra định hướng phát triển cho các ngày tiếp theo.

---

## 1. Những Kiến Thức & Kỹ Năng Đã Học Được (What I Learned)

### A. Công nghệ Điện toán đám mây & Google Earth Engine (GEE)
* **Khai thác kho dữ liệu Raster khổng lồ**: Học cách truy vấn trực tiếp các Image Collection chuẩn quốc tế từ Sentinel-2 (`COPERNICUS/S2_SR_HARMONIZED`) và Landsat 8 (`LANDSAT/LC08/C02/T1_L2`) mà không cần tải thủ công hàng trăm GB dữ liệu về máy.
* **Lọc mây tự động (Cloud Masking)**: 
  * Cách phân tích và trích xuất các bit mây/mù từ băng chất lượng `QA60` đối với Sentinel-2.
  * Cách xử lý băng `QA_PIXEL` đối với Landsat 8 để loại bỏ cả mây và bóng mây (cloud shadow).
* **Tính toán chỉ số phổ (Spectral Indices)**: Hiểu sâu sắc cơ sở vật lý và công thức tính toán chỉ số Thực vật (**NDVI**) và Đô thị hóa/Xây dựng (**NDBI**) để đánh giá hiện trạng mặt phủ địa lý.
* **Thống kê vùng (Zonal Statistics)**: Sử dụng thuật toán `.reduceRegions()` của Earth Engine để tính toán thống kê giá trị trung bình (mean) cho hàng loạt đa giác vector cùng lúc với hiệu suất cực kỳ cao.

### B. Xử lý GIS Cục bộ (Local GIS Pipeline)
* **Lập trình Python không gian (Geospatial Python)**:
  * Sử dụng thư viện `geopandas` để đọc, truy vấn thuộc tính và quản lý không gian các file Vector shapefile.
  * Sử dụng `rasterio` để mở, đọc thông số hình học (transform, bounds, CRS) của ảnh GeoTIFF vệ tinh đơn băng.
* **Tải dữ liệu vệ tinh chuẩn quốc tế**: Đăng ký và làm quen với quy trình tìm kiếm, lọc điều kiện và tải ảnh vệ tinh Surface Reflectance (L2) từ cổng dữ liệu của NASA Earthdata và USGS EarthExplorer.
* **Trực quan hóa bản đồ tương tác**: Sử dụng thư viện `folium` để tạo bản đồ web tương tác (HTML), tích hợp các lớp nền vệ tinh (Esri Satellite, OpenStreetMap) và cấu hình popup/tooltip để truy vấn động thông tin thuộc tính xã/phường.

### C. Sử dụng QGIS Desktop
* Làm quen với giao diện QGIS, cách import vector và raster.
* Thực hiện phân loại màu (Categorized Styling) cho bản đồ hành chính và bật chế độ hiển thị Label tên huyện.
* Thiết lập tổ hợp màu (Band Composite) True Color và False Color để nhận biết thực vật bằng mắt thường trực quan.

### D. Phân tích thông số ảnh vệ tinh Landsat 9 thực tế
* **Thông tin ảnh vệ tinh**: Landsat 9 scene `LC09_L2SP_127045_20251125_20251126_02_T1` được tải từ USGS EarthExplorer.
* **Thời gian và chất lượng**: Ảnh được chụp ngày 25/11/2025 với độ phủ mây chỉ 0.51%, đáp ứng yêu cầu chất lượng dữ liệu.
* **Mức xử lý & Hệ tọa độ**: Dữ liệu ở mức xử lý L2SP (Level-2 Surface Reflectance and Surface Temperature), hệ tọa độ UTM Zone 48N, datum WGS84.
* **Đặc tính kỹ thuật**: Các kênh phản xạ có độ phân giải không gian 30 m và kiểu dữ liệu UINT16.
* **Thông số góc chiếu**: Góc cao mặt trời tại thời điểm chụp là 43.15° và góc phương vị mặt trời là 153.61°.

---

## 2. Những Khó Khăn Gặp Phải (Challenges & Curve)

Mặc dù đã hiểu rõ bản chất quy trình xử lý, quá trình thực hiện thực tế vẫn gặp phải các rào cản kỹ thuật đặc trưng của ngành GIS:

### A. Lệch Hệ tọa độ (CRS Misalignment)
* **Vấn đề**: File Vector ranh giới xã phường nội địa thường sử dụng hệ tọa độ VN-2000 (múi chiếu 3 độ hoặc 6 độ), trong khi các ảnh vệ tinh toàn cầu thường sử dụng hệ tọa độ WGS 84 / UTM Zone 48N (EPSG:32648) hoặc WGS 84 Geographic (EPSG:4326). Nếu chồng đè trực tiếp mà không chuyển đổi CRS, các lớp dữ liệu sẽ bị lệch xa nhau hoặc không hiển thị.
* **Giải pháp**: Phải luôn kiểm tra thuộc tính `.crs` của raster và sử dụng `gdf.to_crs(raster_crs)` để đồng nhất hệ tọa độ trước khi vẽ hoặc thực hiện bất kỳ phép phân tích không gian nào.

### B. Quá tải bộ nhớ khi xử lý ảnh Raster cục bộ (Local Out of Memory)
* **Vấn đề**: Các file ảnh vệ tinh đơn băng tải về máy có kích thước rất lớn (hơn 120MB một băng, độ phân giải $9140 \times 8178$ pixel). Khi chồng nhiều băng làm RGB composite và plot bằng Matplotlib, hệ thống rất dễ bị đơ hoặc lỗi Out Of Memory (OOM).
* **Giải pháp**: Áp dụng kỹ thuật đọc giảm phân giải (Downsampling) trong `rasterio` sử dụng tham số `out_shape` và thuật toán nội suy `Resampling.bilinear` để giảm kích thước ảnh đi 10 lần trước khi nạp vào mảng numpy vẽ bản đồ tĩnh.

### C. Hiệu chỉnh hệ số phản xạ bức xạ (Reflectance Scaling)
* **Vấn đề**: Giá trị pixel thô của ảnh Landsat 8 Level 2 Surface Reflectance nằm ở dạng số nguyên 16-bit (DN - Digital Number). Nếu tính toán trực tiếp mà không hiệu chỉnh, kết quả NDVI/NDBI sẽ hoàn toàn sai lệch.
* **Giải pháp**: Tra cứu file `.MTL` đi kèm của Landsat và áp dụng công thức nhân hệ số tỷ lệ và cộng sai số: $\text{Reflectance} = \text{DN} \times 0.0000275 - 0.2$ để đưa giá trị phản xạ về khoảng vật lý thực tế $[0, 1]$.

