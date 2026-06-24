# Báo cáo Phân tích NDVI & NDBI của Hà Nội cấp Quận/Huyện (2023-2024)

Báo cáo này tóm tắt kết quả phân tích các chỉ số **NDVI** (Chỉ số Thực vật) và **NDBI** (Chỉ số Xây dựng/Đô thị) trung bình cho từng Quận/Huyện tại Hà Nội trong giai đoạn 2023-2024 sử dụng ảnh vệ tinh **Sentinel-2** (độ phân giải 10m) và **Landsat 8** (độ phân giải 30m).

## 1. Phương pháp thực hiện
- **Ranh giới Vector**: Sử dụng ranh giới hành chính cấp huyện của Việt Nam từ Open Development Mekong, lọc riêng 29 Quận/Huyện/Thị xã của Thành phố Hà Nội.
- **Dữ liệu Raster**:
  - **Sentinel-2**: Sử dụng kho ảnh `COPERNICUS/S2_SR_HARMONIZED`, lọc mây bằng kênh `QA60` (ngưỡng mây < 10%).
  - **Landsat 8**: Sử dụng kho ảnh `LANDSAT/LC08/C02/T1_L2`, lọc mây bằng kênh `QA_PIXEL` và hiệu chỉnh hệ số tỷ lệ phản xạ.
- **Tính toán chỉ số**:
  - $\text{NDVI} = \frac{\text{NIR} - \text{Red}}{\text{NIR} + \text{Red}}$ (S2: B8 & B4, L8: B5 & B4)
  - $\text{NDBI} = \frac{\text{SWIR1} - \text{NIR}}{\text{SWIR1} + \text{NIR}}$ (S2: B11 & B8, L8: B6 & B5)
- **Tổng hợp dữ liệu**: Tạo ảnh Median Composite của các chỉ số trong giai đoạn 2023-2024, sau đó dùng `reduceRegions` để tính giá trị trung bình trên từng Quận/Huyện.

---

## 2. Kết quả tính toán chi tiết

Dưới đây là bảng kết quả tổng hợp giá trị trung bình NDVI và NDBI cho từng Quận/Huyện:

| Tên Quận/Huyện | S2 NDVI Mean | S2 NDBI Mean | L8 NDVI Mean | L8 NDBI Mean | Nhận xét địa lý |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Ba Dinh** | 0.2438 | 0.0405 | 0.2595 | -0.0588 | Nội thành, mật độ đô thị cao, thực vật trung bình thấp |
| **Ba Vi** | 0.5089 | -0.1563 | 0.5574 | -0.2359 | Ngoại thành bán sơn địa, độ che phủ cây xanh lớn |
| **Cau Giay** | 0.2339 | 0.0610 | 0.2496 | -0.0337 | Nội thành, mật độ xây dựng cao |
| **Chuong My** | 0.4353 | -0.1609 | 0.4853 | -0.2214 | Ngoại thành, nông nghiệp và đồi núi thấp |
| **Dan Phuong** | 0.3715 | -0.1215 | 0.3923 | -0.1955 | Ngoại thành ven sông Hồng |
| **Dong Anh** | 0.4029 | -0.1015 | 0.3843 | -0.1200 | Huyện đang đô thị hoá nhanh |
| **Dong Da** | 0.1939 | 0.1327 | 0.2022 | 0.0268 | Trung tâm nội thành, bê tông hóa mạnh nhất |
| **Gia Lam** | 0.3976 | -0.1159 | 0.4064 | -0.1758 | Ngoại thành phía Đông |
| **Ha Dong** | 0.3510 | -0.0140 | 0.3939 | -0.0988 | Quận mới phát triển đô thị |
| **Hai Ba Trung** | 0.1400 | 0.0613 | 0.1522 | -0.0470 | Nội thành lõi, ít cây xanh |
| **Hoai Duc** | 0.4283 | -0.0737 | 0.4628 | -0.1406 | Ven đô, đang chuyển đổi đất nông nghiệp |
| **Hoan Kiem** | 0.1960 | 0.0257 | 0.2063 | -0.0690 | Trung tâm lịch sử, mật độ xây dựng cao |
| **Hoang Mai** | 0.2906 | -0.0101 | 0.3225 | -0.1008 | Đô thị hoá cao xen lẫn mặt nước |
| **Long Bien** | 0.3149 | -0.0502 | 0.3106 | -0.1322 | Đô thị mới phía bên kia sông Hồng |
| **Me Linh** | 0.3745 | -0.1332 | 0.3788 | -0.1651 | Vùng trồng hoa và nông nghiệp ngoại ô |
| **My Duc** | 0.4646 | -0.1967 | 0.5396 | -0.2777 | Vùng núi và nông nghiệp phía Nam |
| **Phu Xuyen** | 0.3626 | -0.2088 | 0.4186 | -0.2437 | Huyện nông nghiệp phía Nam |
| **Phuc Tho** | 0.4459 | -0.1435 | 0.4646 | -0.1907 | Vùng nông nghiệp đệm phía Tây |
| **Quoc Oai** | 0.4518 | -0.1407 | 0.4862 | -0.2092 | Ngoại thành phía Tây |
| **Soc Son** | 0.4683 | -0.1122 | 0.4501 | -0.1174 | Vùng đồi núi phía Bắc, diện tích rừng lớn |
| **Son Tay** | 0.4635 | -0.1270 | 0.5079 | -0.1968 | Thị xã ngoại thành |
| **Tay Ho** | 0.2075 | -0.1226 | 0.1986 | -0.1875 | Quận có Hồ Tây lớn nên chỉ số phản xạ bị ảnh hưởng |
| **Thach That** | 0.5217 | -0.1191 | 0.5611 | -0.1925 | Khu vực đồi núi và vườn rừng nhiều cây xanh nhất |
| **Thanh Oai** | 0.3925 | -0.1663 | 0.4537 | -0.2134 | Vùng đồng bằng nông nghiệp |
| **Thanh Tri** | 0.3704 | -0.0820 | 0.4060 | -0.1616 | Huyện ven đô phía Nam |
| **Thanh Xuan** | 0.2327 | 0.0788 | 0.2849 | -0.0149 | Nội thành, trục đô thị hoá mạnh |
| **Thuong Tin** | 0.3958 | -0.1420 | 0.4362 | -0.2044 | Huyện phía Nam |
| **Tu Liem** | 0.3358 | -0.0444 | 0.3649 | -0.1294 | Vùng đô thị hoá Nam/Bắc Từ Liêm |
| **Ung Hoa** | 0.3617 | -0.2288 | 0.4234 | -0.2822 | Huyện thuần nông nghiệp phía Nam |

---

## 3. Nhận xét & Đánh giá
1. **Sự phân hóa Đông - Tây & Nội - Ngoại thành**:
   - Các quận nội thành cũ như **Đống Đa (NDVI ~ 0.19, NDBI ~ 0.13)** và **Hai Bà Trưng (NDVI ~ 0.14, NDBI ~ 0.06)** thể hiện đặc điểm đô thị cực kỳ điển hình: chỉ số xây dựng (NDBI) dương và chỉ số thực vật (NDVI) rất thấp.
   - Các huyện bán sơn địa phía Tây và Bắc như **Thạch Thất (NDVI ~ 0.52)** và **Ba Vì (NDVI ~ 0.51)** có độ bao phủ cây xanh dồi dào, NDBI âm rất sâu biểu thị hầu như không bị bê tông hóa trên diện rộng.
2. **So sánh Sentinel-2 và Landsat 8**:
   - Nhìn chung, xu hướng tính toán của 2 vệ tinh là tương đương nhau.
   - Sentinel-2 có độ phân giải không gian cao hơn (10m so với 30m của Landsat 8), giúp phân tách các ranh giới đô thị nhỏ/kênh rạch sông ngòi chi tiết hơn.
   - Giá trị NDBI của Landsat 8 dịch chuyển âm nhiều hơn Sentinel-2. Điều này thường do sự khác biệt về bước sóng và hiệu ứng phản xạ phổ của các cảm biến đối với đất trống và bê tông.
3. **Ảnh hưởng của mặt nước**:
   - Quận **Tây Hồ** có giá trị NDVI và NDBI khá thấp (lần lượt ~0.20 và ~-0.12) do phần lớn diện tích là mặt nước (Hồ Tây). Nước hấp thụ mạnh ở cả dải hồng ngoại gần (NIR) và hồng ngoại sóng ngắn (SWIR), làm sai lệch tương đối các chỉ số này so với đất liền thông thường.

---
> [!NOTE]
> Bảng dữ liệu thô đã được lưu tại tập tin `hanoi_district_indices.csv` trong thư mục làm việc của bạn.
