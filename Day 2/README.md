# Ngày 2: Phân loại lớp phủ Hà Nội (LULC) bằng Random Forest & Google Earth Engine (GEE)

Thư mục này chứa toàn bộ mã nguồn, dữ liệu đầu ra và kết quả phân loại lớp phủ bề mặt (Land Use / Land Cover - LULC) cho thành phố Hà Nội bằng phương pháp học máy có kiểm định (Supervised Classification).

---

## 1. Mục tiêu dự án
* **Thiết lập mẫu huấn luyện dạng vùng (Polygons)**: Số hóa 15 vùng mẫu đại diện trên bản đồ cho 4 lớp chính: Đô thị (Urban), Nước (Water), Nông nghiệp (Agriculture), và Cây xanh (Greenery), thu thập tổng cộng 600 điểm ảnh mẫu (150 mẫu/lớp) thông qua phương pháp lấy mẫu phân tầng (Stratified Sampling).
* **Tích hợp chỉ số viễn thám**: Đưa thêm các chỉ số phổ phụ trợ **NDVI**, **NDBI**, và **MNDWI** làm biến đầu vào (Features) để tăng độ phân biệt giữa các lớp phủ.
* **Huấn luyện mô hình Random Forest**: Sử dụng bộ phân loại `ee.Classifier.smileRandomForest` cấu hình **100 cây quyết định** chạy trực tiếp trên GEE.
* **Thống kê diện tích**: Raster-to-Vector zonal statistics để tính toán diện tích ($km^2$) từng lớp phủ của 29 Quận/Huyện của Hà Nội, so sánh sự phát triển đô thị (ví dụ: Cầu Giấy vs. Hà Đông).
* **Trực quan hóa**: Xuất bản đồ tương tác HTML hiển thị ranh giới hành chính kèm thông số đô thị hóa khi di chuột qua từng quận.

---

## 2. Cấu trúc thư mục
* 📄 [Day2.ipynb](Day2.ipynb): Jupyter Notebook hoàn chỉnh từ tiền xử lý dữ liệu, lấy mẫu, huấn luyện, đánh giá độ chính xác, thống kê diện tích đến trực quan hóa bản đồ.
* 📄 [hanoi_lulc_district_areas.csv](hanoi_lulc_district_areas.csv): Bảng dữ liệu diện tích các lớp phủ bề mặt ($km^2$) của từng Quận/Huyện.
* 📄 [hanoi_lulc_interactive.html](hanoi_lulc_interactive.html): Bản đồ tương tác LULC Hà Nội tích hợp chú giải (Legend), ranh giới quận huyện và tooltip thông tin đô thị hóa thông minh.
* 📄 [implementation_plan.md](implementation_plan.md): Kế hoạch thực hiện chi tiết.

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

### So sánh đất xây dựng (Đô thị): Cầu Giấy vs. Hà Đông
Nhờ nâng cấp lấy mẫu dạng đa giác đa điểm, mô hình phân tách hoàn hảo các vùng đất trống nông nghiệp tại Hà Đông, mang lại số liệu diện tích thực tế cao:

| Quận | Diện tích Đô thị ($km^2$) | Diện tích tự nhiên ($km^2$) | Tỷ lệ Đô thị hóa (%) |
| :--- | :---: | :---: | :---: |
| **Cầu Giấy** | 11.40 | 15.91 | 71.65% |
| **Hà Đông** | 15.02 | 34.17 | 43.96% |

* **Nhận xét**: Hà Đông có diện tích đất đô thị lớn hơn Cầu Giấy **3.62 $km^2$** (gấp 1.32 lần) do quỹ đất tự nhiên rộng lớn hơn. Tuy nhiên, Cầu Giấy có mật độ đô thị hóa cực kỳ cao (71.65% so với 43.96% của Hà Đông) do là lõi nội thành phát triển lâu đời.

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
