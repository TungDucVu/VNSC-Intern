# Quy trình Phân loại Lớp phủ LULC Hà Nội Cấp học thuật (Kế hoạch Thay thế)

Thư mục này chứa mã nguồn triển khai quy trình phân loại lớp phủ bề mặt (Land Use / Land Cover - LULC) cấp học thuật cho thành phố Hà Nội. Quy trình này chuyển đổi phương pháp từ lấy mẫu đa giác thủ công sang lấy mẫu phân tầng tự động dựa trên bộ dữ liệu **ESA WorldCover 2021**, tích hợp các đặc trưng địa hình (Độ cao, Độ dốc) từ dữ liệu **ALOS AW3D30 DEM**, và huấn luyện mô hình Random Forest kết hợp với các bộ lọc hậu xử lý giảm nhiễu.

---

## 1. Phương pháp Phân loại

Quy trình phân loại thay thế bao gồm 5 giai đoạn chính:

### Giai đoạn 1: Thu thập & Tiền xử lý dữ liệu
* **Ảnh vệ tinh**: Ảnh độ phản xạ bề mặt Sentinel-2 (Level-2A) được tổng hợp (composite) cho mùa khô (từ 01/01 đến 15/02) của năm 2021 (năm cơ sở để lấy mẫu) và năm 2024 (năm mục tiêu phân loại).
* **Lọc mây**: Áp dụng mặt nạ mây QA60 để loại bỏ mây dày và mây tích (cirrus).
* **Nội suy lại (Resampling)**: Áp dụng phương pháp `.resample('bicubic')` trên từng ảnh đơn lẻ trong ImageCollection trước khi tính median composite nhằm giữ nguyên hệ tọa độ chiếu UTM bản địa và kích thước lưới, tránh lỗi tự động chuyển về độ phân giải thô 1 độ của GEE.
* **Đặc trưng Địa hình**: Tích hợp dữ liệu độ cao và độ dốc từ **ALOS AW3D30 DEM** của JAXA ở độ phân giải 30m, được nội suy về 10m.

### Giai đoạn 2: Lựa chọn Thuộc tính (Feature Engineering)
Tổng cộng **16 thuộc tính dự báo** được đưa vào bộ phân loại:
* **Các kênh phổ**: Xanh dương (`B2`), Xanh lá (`B3`), Đỏ (`B4`), Cận hồng ngoại (`B8`), SWIR-1 (`B11`), và SWIR-2 (`B12`).
* **Các chỉ số phổ phụ trợ**:
  * NDVI (Chỉ số thực vật): để nhận diện cây xanh.
  * NDBI (Chỉ số đất xây dựng): để nhận diện bề mặt đô thị/bê tông hóa.
  * MNDWI (Chỉ số nước cải tiến): để nhận diện các vùng nước mặt.
  * EVI (Chỉ số thực vật tăng cường): tăng khả năng phân biệt cấu trúc thực vật rậm rạp.
  * SAVI (Chỉ số thực vật hiệu chỉnh đất): hiệu chỉnh độ sáng của nền đất trống.
  * BSI (Chỉ số đất trống): nâng cao nhận diện công trường và đất canh tác khô.
* **Chỉ số địa hình**: Độ cao (DSM) và Độ dốc (Slope).
* **Đặc trưng Biến động Thời gian**: `NDVI_stdDev` (Độ lệch chuẩn thời gian của NDVI cả năm) giúp phân tách rõ rệt đất nông nghiệp có chu kỳ sinh trưởng khỏi đất trống đô thị/cát sông ổn định.
* **Đặc trưng Kết cấu Không gian**: `B8_contrast` (Độ tương phản GLCM của kênh Cận hồng ngoại B8) giúp phân biệt bề mặt mịn của bãi cát sông Hồng với cấu trúc phức tạp, đứt gãy của các tòa nhà đô thị.

### Giai đoạn 3: Lấy mẫu Phân tầng Tự động & Lọc sạch nhãn nhiễu
* **Nhãn tham chiếu**: Bộ dữ liệu **ESA WorldCover 2021 (10m)** được phân loại lại từ 11 lớp toàn cầu thành 5 lớp địa phương:
  * `0`: Nước (Open water - lớp 80)
  * `1`: Đô thị (Built-up - lớp 50)
  * `2`: Nông nghiệp (Cropland - lớp 40)
  * `3`: Cây xanh (Trees, Shrubland, Grassland, Herbaceous wetland - các lớp 10, 20, 30, 90, 95)
  * `4`: Đất trống (Barren / sparse vegetation - các lớp 60, 100)
* **Lấy mẫu**: Thực thi hàm `.stratifiedSample()` trên ảnh tổng hợp Sentinel-2 năm 2021 của Hà Nội dựa trên bản đồ ESA đã phân loại lại:
  * Tổng điểm mẫu phân tầng: **2500 điểm** (phân bổ tối đa: [2000, 1500, 1500, 1500, 2500])
* **Lọc sạch nhãn nhiễu (Spectral Filtering)**: Để loại bỏ sai lệch nhãn do sai khác mùa (ví dụ: bãi cát khô ven sông Hồng mùa khô bị bản đồ tham chiếu ESA gán nhãn tĩnh là Nước), ta áp dụng các bộ lọc vật lý:
  * Mẫu Nước phải có `MNDWI > -0.05`.
  * Mẫu Cây xanh phải có `NDVI > 0.25`.
  * Mẫu Đất trống phải có `MNDWI < 0` và `NDVI < 0.3`.
* **Cập nhật phổ vùng nước**: Lấy thêm 50 pixel mẫu nước số hóa thủ công trên sông Hồng năm 2024.

### Giai đoạn 4: Huấn luyện & Đánh giá mô hình
* **Mô hình**: Bộ phân loại Random Forest cấu hình **200 cây quyết định** (`ee.Classifier.smileRandomForest(200)`).
* **Chia tách dữ liệu**: 70% lượng mẫu sạch dùng để huấn luyện mô hình, 30% giữ làm tập kiểm thử (validation).

### Giai đoạn 5: Hậu xử lý
Để loại bỏ các sai số phân loại cục bộ và nhiễu không gian, hai bộ lọc đã được áp dụng:
1. **Lọc trung vị không gian (Focal Mode)**: Áp dụng bộ lọc Focal Mode hình tròn bán kính 1 pixel (`.focalMode(1, 'circle')`) để làm mịn các pixel nhiễu đơn lẻ ("nhiễu muối tiêu").
2. **Ép mặt nạ nước (Water Masking)**: Ép các vùng nước mặt vĩnh cửu từ lớp 80 của ESA WorldCover vào bản đồ phân loại LULC cuối cùng bằng hàm `.where()` để đảm bảo hình dáng dòng sông Hồng chính xác 100%.

---

## 2. Kết quả Đánh giá Độ chính xác (Chia tách 70/30)

Sau khi tích hợp 3 chỉ số phổ EVI, SAVI, BSI và lọc sạch nhãn nhiễu khỏi dữ liệu mẫu:

* **Độ chính xác toàn cục (Overall Accuracy - OA)**: **83.48%**
* **Hệ số Kappa (Kappa Coefficient)**: **0.7930**

### Ma trận nhầm lẫn (Confusion Matrix)
```text
Thực tế \ Dự báo | Nước (0) | Đô thị (1) | Nông nghiệp (2) | Cây xanh (3) | Đất trống (4)
Nước (0)        |   533    |     0      |      18        |      0       |      5
Đô thị (1)      |     2    |   353      |      18        |     34       |     61
Nông nghiệp (2)  |    16    |    16      |     344        |     54       |     11
Cây xanh (3)    |     1    |    32      |      57        |    347       |      2
Đất trống (4)   |     1    |    41      |      17        |      0       |    383
```

---

## 3. Các sản phẩm đầu ra trong thư mục
* 📄 **[classify_hanoi.py](classify_hanoi.py)**: Tập lệnh Python chạy quy trình phân loại từ đầu đến cuối và xuất báo cáo tự động.
* 📄 **[classify_hanoi.ipynb](classify_hanoi.ipynb)**: Jupyter Notebook chi tiết, lưu vết đầy đủ đầu ra thực thi của mô hình.
* 📄 **[hanoi_lulc_district_areas.csv](hanoi_lulc_district_areas.csv)**: Bảng thống kê diện tích ($km^2$) các lớp phủ LULC cho 29 quận/huyện của Hà Nội được tính ở độ phân giải 10m.
* 📄 **[hanoi_lulc_interactive.html](hanoi_lulc_interactive.html)**: Bản đồ tương tác Folium chứa ranh giới quận huyện, chú thích 5 lớp phủ, và tooltip thông minh hiển thị tỷ lệ đô thị hóa khi di chuột.

---

## 4. Hướng dẫn chạy chương trình

Đảm bảo môi trường conda `hanoi_gis` đã được kích hoạt:

```bash
# Cách 1: Chạy trực tiếp kịch bản Python để xuất file
python LULC_Hanoi_2021_2024/classify_hanoi.py

# Cách 2: Mở Jupyter Notebook để xem phân tích trực quan
jupyter notebook LULC_Hanoi_2021_2024/classify_hanoi.ipynb
```
