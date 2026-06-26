# Quy trình Phân loại Lớp phủ LULC Hà Nội Cấp học thuật (Kế hoạch Thay thế)

Thư mục này chứa mã nguồn triển khai quy trình phân loại lớp phủ bề mặt (Land Use / Land Cover - LULC) cấp học thuật cho thành phố Hà Nội. Quy trình này chuyển đổi phương pháp từ lấy mẫu đa giác thủ công sang lấy mẫu phân tầng tự động dựa trên bộ dữ liệu **ESA WorldCover 2021**, tích hợp các đặc trưng địa hình (Độ cao, Độ dốc) từ dữ liệu **ALOS AW3D30 DEM**, và huấn luyện mô hình Random Forest kết hợp với các bộ lọc hậu xử lý giảm nhiễu.

---

## 1. Phương pháp Phân loại

Quy trình phân loại thay thế bao gồm 5 giai đoạn chính:

### Giai đoạn 1: Thu thập & Tiền xử lý dữ liệu
* **Ảnh vệ tinh**: Ảnh độ phản xạ bề mặt Sentinel-2 (Level-2A) được tổng hợp (composite) cho mùa khô (từ 01/01 đến 31/03) của năm 2021 (năm cơ sở để lấy mẫu) và năm 2024 (năm mục tiêu phân loại).
* **Lọc mây**: Áp dụng mặt nạ mây QA60 để loại bỏ mây dày và mây tích (cirrus).
* **Nội suy lại (Resampling)**: Áp dụng phương pháp `.resample('bicubic')` trên từng ảnh đơn lẻ trong ImageCollection trước khi tính median composite nhằm giữ nguyên hệ tọa độ chiếu UTM bản địa và kích thước lưới, tránh lỗi tự động chuyển về độ phân giải thô 1 độ của GEE.
* **Đặc trưng Địa hình**: Tích hợp dữ liệu độ cao và độ dốc từ **ALOS AW3D30 DEM** của JAXA ở độ phân giải 30m, được nội suy về 10m.

### Giai đoạn 2: Lựa chọn Thuộc tính (Feature Engineering)
Tổng cộng **11 thuộc tính dự báo** được đưa vào bộ phân loại:
* **Các kênh phổ**: Xanh dương (`B2`), Xanh lá (`B3`), Đỏ (`B4`), Cận hồng ngoại (`B8`), SWIR-1 (`B11`), và SWIR-2 (`B12`).
* **Các chỉ số phổ phụ trợ**:
  * NDVI (Chỉ số thực vật): để nhận diện cây xanh.
  * NDBI (Chỉ số đất xây dựng): để nhận diện bề mặt đô thị/bê tông hóa.
  * MNDWI (Chỉ số nước cải tiến): để nhận diện các vùng nước mặt.
* **Chỉ số địa hình**: Độ cao (DSM) và Độ dốc (Slope).

### Giai đoạn 3: Lấy mẫu Phân tầng Tự động
* **Nhãn tham chiếu**: Bộ dữ liệu **ESA WorldCover 2021 (10m)** được phân loại lại từ 11 lớp toàn cầu thành 5 lớp địa phương:
  * `0`: Nước (Open water - lớp 80)
  * `1`: Đô thị (Built-up - lớp 50)
  * `2`: Nông nghiệp (Cropland - lớp 40)
  * `3`: Cây xanh (Trees, Shrubland, Grassland, Herbaceous wetland - các lớp 10, 20, 30, 90, 95)
  * `4`: Đất trống (Barren / sparse vegetation - các lớp 60, 100)
* **Lấy mẫu**: Thực thi hàm `.stratifiedSample()` trên ảnh tổng hợp Sentinel-2 năm 2021 của Hà Nội dựa trên bản đồ ESA đã phân loại lại. Thu thập ngẫu nhiên **800 điểm mẫu cho mỗi lớp**.
* **Cập nhật phổ vùng nước**: Lấy thêm 50 pixel mẫu nước số hóa thủ công trên sông Hồng năm 2024 để mô hình nhận diện chính xác phổ nước đục của sông Hồng năm 2024.

### Giai đoạn 4: Huấn luyện & Đánh giá mô hình
* **Mô hình**: Bộ phân loại Random Forest cấu hình **150 cây quyết định** (`ee.Classifier.smileRandomForest`).
* **Chia tách dữ liệu**: 70% lượng mẫu dùng để huấn luyện mô hình, 30% mẫu còn lại được giữ làm tập kiểm thử (validation).

### Giai đoạn 5: Hậu xử lý
Để loại bỏ các sai số phân loại cục bộ và nhiễu không gian, hai bộ lọc đã được áp dụng:
1. **Lọc trung vị không gian (Focal Mode)**: Áp dụng bộ lọc Focal Mode hình tròn bán kính 1 pixel (`.focalMode(1, 'circle')`) để làm mịn các pixel nhiễu đơn lẻ ("nhiễu muối tiêu").
2. **Ép mặt nạ nước (Water Masking)**: Ép các vùng nước mặt vĩnh cửu từ lớp 80 của ESA WorldCover vào bản đồ phân loại LULC cuối cùng bằng hàm `.where()` để đảm bảo hình dáng dòng sông Hồng chính xác 100%.

---

## 2. Kết quả Đánh giá Độ chính xác (Chia tách 70/30)

* **Độ chính xác toàn cục (Overall Accuracy - OA)**: **74.31%**
* **Hệ số Kappa (Kappa Coefficient)**: **0.6786**

### Ma trận nhầm lẫn (Confusion Matrix)
```text
Thực tế \ Dự báo | Nước (0) | Đô thị (1) | Nông nghiệp (2) | Cây xanh (3) | Đất trống (4)
Nước (0)        |   187    |     1      |       11       |      4       |      31
Đô thị (1)      |     0    |   174      |       19       |     16       |      26
Nông nghiệp (2)  |     5    |    23      |      165       |     30       |      22
Cây xanh (3)    |     2    |    23      |       31       |    207       |       4
Đất trống (4)   |    14    |    20      |       30       |      3       |     178
```

*Lưu ý: Sự nhầm lẫn giữa Nước/Đất trống và Đô thị/Đất trống phản ánh đúng thực tế thực địa vào mùa khô (lòng sông Hồng cạn trơ bãi cát, các công trường đang san lấp và ruộng đồng bỏ hoang sau thu hoạch).*

---

## 3. Các sản phẩm đầu ra trong thư mục
* 📄 **[classify_hanoi.py](classify_hanoi.py)**: Tập lệnh Python thực thi toàn bộ quy trình GEE, tính toán diện tích và xây dựng bản đồ tương tác Folium.
* 📄 **[hanoi_lulc_district_areas.csv](hanoi_lulc_district_areas.csv)**: Bảng thống kê diện tích ($km^2$) các lớp phủ LULC cho 29 quận/huyện của Hà Nội được tính ở độ phân giải 10m.
* 📄 **[hanoi_lulc_interactive.html](hanoi_lulc_interactive.html)**: Bản đồ tương tác Folium chứa ranh giới quận huyện, chú thích 5 lớp phủ, và tooltip thông minh hiển thị tỷ lệ đô thị hóa khi di chuột.

---

## 4. Hướng dẫn chạy chương trình

Đảm bảo môi trường conda `hanoi_gis` đã được kích hoạt, sau đó chạy lệnh:

```bash
python LULC_Alternative/classify_hanoi.py
```
