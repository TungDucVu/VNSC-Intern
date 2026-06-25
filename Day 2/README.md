# Ngày 2: Phân loại lớp phủ Hà Nội (LULC) bằng Random Forest & Google Earth Engine (GEE)

Thư mục này chứa toàn bộ mã nguồn, dữ liệu đầu ra và kết quả phân loại lớp phủ bề mặt (Land Use / Land Cover - LULC) cho thành phố Hà Nội bằng phương pháp học máy có kiểm định (Supervised Classification).

---

## 1. Mục tiêu dự án
* **Thiết lập mẫu huấn luyện dạng vùng (Polygons)**: Số hóa 15 vùng mẫu đại diện trên bản đồ cho 4 lớp chính: Đô thị (Urban), Nước (Water), Nông nghiệp (Agriculture), và Cây xanh (Greenery), thu thập tổng cộng 600 điểm ảnh mẫu (150 mẫu/lớp) thông qua phương pháp lấy mẫu phân tầng (Stratified Sampling).
* **Tích hợp chỉ số viễn thám**: Đưa thêm các chỉ số phổ phụ trợ **NDVI**, **NDBI**, và **MNDWI** làm biến đầu vào (Features) để tăng độ phân biệt giữa các lớp phủ.
* **Huấn luyện mô hình Random Forest**: Sử dụng bộ phân loại `ee.Classifier.smileRandomForest` cấu hình **100 cây quyết định** chạy trực tiếp trên GEE.
* **Thống kê diện tích**: Raster-to-Vector zonal statistics để tính toán diện tích ($km^2$) từng lớp phủ của 29 Quận/Huyện của Hà Nội.
* **Trực quan hóa**: Xuất bản đồ tương tác HTML hiển thị ranh giới hành chính kèm thông số đô thị hóa khi di chuột qua từng quận.

---

## 2. Cấu trúc thư mục
* 📄 [Day2.ipynb](Day2.ipynb): Jupyter Notebook hoàn chỉnh từ tiền xử lý dữ liệu, lấy mẫu, huấn luyện, đánh giá độ chính xác, thống kê diện tích đến trực quan hóa bản đồ.
* 📄 [hanoi_lulc_district_areas.csv](hanoi_lulc_district_areas.csv): Bảng dữ liệu diện tích các lớp phủ bề mặt ($km^2$) của từng Quận/Huyện.
* 📄 [hanoi_lulc_interactive.html](hanoi_lulc_interactive.html): Bản đồ tương tác LULC Hà Nội tích hợp chú giải (Legend), ranh giới quận huyện và tooltip thông tin đô thị hóa thông minh.
* 📄 [implementation_plan.md](implementation_plan.md): Kế hoạch thực hiện chi tiết.
* 📄 [static_output.png](static_output.png): Bản đồ LULC Hà Nội 2024.


---

## 3. Quy trình thực hiện & Phương pháp
1. **Truy vấn ảnh vệ tinh**: Sentinel-2 Surface Reflectance năm 2024, lọc mây bằng kênh QA60 (mây và cirrus), lấy median composite.
2. **Tính toán chỉ số phổ**:
   * **NDVI** (Chỉ số thực vật): $NDVI = \frac{B8 - B4}{B8 + B4}$
   * **NDBI** (Chỉ số đất xây dựng): $NDBI = \frac{B11 - B8}{B11 + B8}$
   * **MNDWI** (Chỉ số nước cải tiến): $MNDWI = \frac{B3 - B11}{B3 + B11}$
3. **Lấy mẫu huấn luyện**:
   * Vẽ 15 đa giác đại diện trên bản đồ vệ tinh.
   * Sử dụng thuật toán `.paint()` kết hợp `.stratifiedSample()` của GEE để rải ngẫu nhiên 150 mẫu/lớp phủ tại độ phân giải 10m.
4. **Phân loại**: Huấn luyện Random Forest 100 cây quyết định trên 9 thuộc tính phổ (`['B2', 'B3', 'B4', 'B8', 'B11', 'B12', 'NDVI', 'NDBI', 'MNDWI']`).
5. **Đánh giá & Tính diện tích**: Đánh giá độ chính xác mô hình qua Confusion Matrix trên GEE. Tính toán diện tích từng lớp phủ bằng `ee.Image.pixelArea()` và `.reduceRegions()` với scale 10m.

---

## 4. Kết quả & Đánh giá hiệu năng

### Độ chính xác mô hình
Mô hình đạt độ chính xác phân loại tuyệt vời trên tập mẫu huấn luyện lớn:
* **Độ chính xác toàn cục (Overall Accuracy)**: **99.50%**
* **Hệ số Kappa (Kappa Coefficient)**: **0.9933**
* **Ma trận nhầm lẫn (Confusion Matrix)**:
  ```text
  Lớp phủ  | Water | Urban | Agri | Green
  Water    |  148  |   1   |  1   |   0
  Urban    |   0   |  150  |  0   |   0
  Agriculture| 0   |   0   | 150  |   0
  Greenery |   1   |   0   |  0   |  149
  ```

### Bảng Thống kê Diện tích Lớp phủ (LULC) các Quận/Huyện (Ngày 2)
Dưới đây là bảng thống kê chi tiết diện tích ($km^2$) của cả 4 lớp phủ (Water, Urban, Agriculture, Greenery) và tổng diện tích của từng Quận/Huyện ở Hà Nội (tính toán ở độ phân giải 10m):

| Mã Quận | Tên Quận/Huyện | Nước ($km^2$) | Đô thị ($km^2$) | Nông nghiệp ($km^2$) | Cây xanh ($km^2$) | Tổng Diện tích ($km^2$) |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| 01017 | Dong Anh | 43.38 | 44.26 | 94.73 | 8.08 | 190.46 |
| 01016 | Soc Son | 59.20 | 34.23 | 156.95 | 53.67 | 304.05 |
| 01271 | Ba Vi | 92.12 | 31.94 | 155.11 | 140.00 | 419.17 |
| 01018 | Gia Lam | 30.38 | 31.54 | 47.64 | 8.83 | 118.39 |
| 01019 | Tu Liem | 19.86 | 31.04 | 21.02 | 2.80 | 74.72 |
| 01277 | Chuong My | 42.57 | 29.37 | 129.03 | 28.34 | 229.30 |
| 01279 | Thuong Tin | 28.75 | 28.93 | 77.55 | 4.65 | 139.87 |
| 01280 | Phu Xuyen | 38.72 | 26.12 | 110.29 | 5.02 | 180.15 |
| 01274 | Hoai Duc | 19.91 | 23.78 | 35.02 | 5.25 | 83.94 |
| 01282 | My Duc | 42.82 | 23.40 | 111.77 | 57.33 | 235.32 |
| 01004 | Long Bien | 15.90 | 22.24 | 14.95 | 3.82 | 56.90 |
| 01020 | Thanh Tri | 18.04 | 22.18 | 26.77 | 3.44 | 70.44 |
| 01276 | Thach That | 30.98 | 21.18 | 69.99 | 50.67 | 172.83 |
| 01281 | Ung Hoa | 35.77 | 20.64 | 118.53 | 4.19 | 179.12 |
| 01275 | Quoc Oai | 29.02 | 19.82 | 77.67 | 24.74 | 151.25 |
| 01250 | Me Linh | 32.99 | 19.08 | 82.95 | 8.59 | 143.60 |
| 01008 | Hoang Mai | 9.85 | 17.93 | 8.52 | 1.68 | 37.98 |
| 01278 | Thanh Oai | 22.79 | 17.37 | 80.85 | 4.96 | 125.96 |
| 01272 | Phuc Tho | 29.88 | 16.09 | 60.26 | 12.29 | 118.51 |
| 01268 | Ha Dong | 7.94 | 15.02 | 9.64 | 1.56 | 34.17 |
| 01273 | Dan Phuong | 22.82 | 14.88 | 28.26 | 6.83 | 72.79 |
| 01269 | Son Tay | 33.70 | 14.56 | 44.51 | 29.97 | 122.74 |
| 01005 | Cau Giay | 2.82 | 11.40 | 1.46 | 0.22 | 15.91 |
| 01003 | Tay Ho | 11.93 | 9.25 | 5.55 | 0.98 | 27.72 |
| 01007 | Hai Ba Trung | 3.38 | 8.48 | 0.74 | 0.27 | 12.87 |
| 01006 | Dong Da | 1.56 | 7.04 | 0.48 | 0.06 | 9.15 |
| 01001 | Ba Dinh | 2.57 | 6.88 | 1.48 | 0.53 | 11.46 |
| 01009 | Thanh Xuan | 1.58 | 5.77 | 0.83 | 0.17 | 8.35 |
| 01002 | Hoan Kiem | 1.60 | 3.61 | 0.52 | 0.20 | 5.93 |

---

## 5. Hướng dẫn chạy chương trình
1. **Yêu cầu môi trường**: Cài đặt Python 3.10+, cài đặt các thư viện thông qua kernel `hanoi_gis`:
   ```bash
   pip install earthengine-api geemap geopandas pandas folium jinja2
   ```
2. **Xác thực GEE**: Bạn cần tài khoản Google Earth Engine đã được cấp quyền truy cập Cloud Project. Khi chạy chương trình lần đầu, chạy lệnh sau trong terminal hoặc notebook để xác thực:
   ```python
   import ee
   ee.Authenticate()
   ```
3. **Chạy Jupyter Notebook**: Mở `Day2.ipynb` bằng Jupyter Lab/Notebook và chọn kernel `hanoi_gis`, chạy toàn bộ các cell để tạo lại bảng dữ liệu CSV và xuất bản đồ.
4. **Tái sinh Folium Map**: Để cập nhật trực tiếp bản đồ HTML mà không cần mở notebook, chạy lệnh:
   ```bash
   python "generate_folium_map.py"
   ```
