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

### Kết quả Chỉ số phổ Trung bình các Quận/Huyện (Từ Ngày 1)
Dưới đây là bảng chỉ số thực vật (NDVI) và chỉ số đất xây dựng (NDBI) trung bình của các Quận/Huyện tại Hà Nội tính toán từ ảnh Sentinel-2 (S2) và Landsat 8 (L8) ở Ngày 1:

| Mã Quận | Tên Quận/Huyện | Dân số (2009) | S2 NDVI Mean | S2 NDBI Mean | L8 NDVI Mean | L8 NDBI Mean |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| 01001 | Ba Dinh | 225,910 | 0.2438 | 0.0405 | 0.2992 | -0.0267 |
| 01271 | Ba Vi | 246,120 | 0.5089 | -0.1563 | 0.6145 | -0.2231 |
| 01005 | Cau Giay | 225,643 | 0.2339 | 0.0610 | 0.2562 | -0.0249 |
| 01277 | Chuong My | 286,359 | 0.4353 | -0.1609 | 0.4968 | -0.2225 |
| 01273 | Dan Phuong | 142,480 | 0.3715 | -0.1215 | 0.4920 | -0.1628 |
| 01017 | Dong Anh | 333,337 | 0.4029 | -0.1015 | 0.4153 | -0.1028 |
| 01006 | Dong Da | 370,117 | 0.1939 | 0.1327 | 0.2076 | 0.0356 |
| 01018 | Gia Lam | 229,735 | 0.3976 | -0.1159 | 0.4567 | -0.1591 |
| 01268 | Ha Dong | 233,126 | 0.3510 | -0.0140 | 0.3955 | -0.0986 |
| 01007 | Hai Ba Trung | 295,726 | 0.1400 | 0.0613 | 0.2390 | 0.0231 |
| 01274 | Hoai Duc | 191,106 | 0.4283 | -0.0737 | 0.4641 | -0.1403 |
| 01002 | Hoan Kiem | 147,334 | 0.1960 | 0.0257 | 0.2792 | -0.0174 |
| 01008 | Hoang Mai | 335,509 | 0.2906 | -0.0101 | 0.3550 | -0.0877 |
| 01004 | Long Bien | 226,913 | 0.3149 | -0.0502 | 0.3876 | -0.0969 |
| 01250 | Me Linh | 191,490 | 0.3745 | -0.1332 | 0.4267 | -0.1452 |
| 01282 | My Duc | 169,999 | 0.4646 | -0.1967 | 0.5602 | -0.2771 |
| 01280 | Phu Xuyen | 181,388 | 0.3626 | -0.2088 | 0.4307 | -0.2419 |
| 01272 | Phuc Tho | 159,484 | 0.4459 | -0.1435 | 0.5072 | -0.1760 |
| 01275 | Quoc Oai | 160,190 | 0.4518 | -0.1407 | 0.5016 | -0.2097 |
| 01016 | Soc Son | 282,536 | 0.4683 | -0.1122 | 0.4640 | -0.1106 |
| 01269 | Son Tay | 125,749 | 0.4635 | -0.1270 | 0.5543 | -0.1852 |
| 01003 | Tay Ho | 130,639 | 0.2075 | -0.1226 | 0.3572 | -0.0868 |
| 01276 | Thach That | 177,545 | 0.5217 | -0.1191 | 0.5671 | -0.1924 |
| 01278 | Thanh Oai | 167,250 | 0.3925 | -0.1663 | 0.4568 | -0.2130 |
| 01020 | Thanh Tri | 198,706 | 0.3704 | -0.0820 | 0.4270 | -0.1537 |
| 01009 | Thanh Xuan | 223,694 | 0.2327 | 0.0788 | 0.2919 | -0.0141 |
| 01279 | Thuong Tin | 219,246 | 0.3958 | -0.1420 | 0.4486 | -0.2011 |
| 01019 | Tu Liem | 392,558 | 0.3358 | -0.0444 | 0.4036 | -0.1112 |
| 01281 | Ung Hoa | 182,008 | 0.3617 | -0.2288 | 0.4331 | -0.2816 |

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
