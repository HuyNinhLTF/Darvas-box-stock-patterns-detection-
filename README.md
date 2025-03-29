# Darvas-box-stock-patterns-detection-
# README - Công cụ tìm kiếm những cổ phiếu đang ở giai đoạn tích lũy dựa trên giá và khối lượng

## Giới thiệu
Chương trình này sử dụng thư viện `vnstock` để lấy dữ liệu giá cổ phiếu từ thị trường chứng khoán Việt Nam, phân tích mẫu hình nến, tìm kiếm những cổ phiếu đang trong giai đoạn tích lũy dựa trên giá và khối lượng.
## Cài đặt
Chương trình yêu cầu Python và các thư viện sau:
```bash
pip install vnstock mplfinance pandas numpy concurrent.futures
```

## Mô tả chi tiết các hàm

### 1. Lấy danh sách mã chứng khoán
Hàm `get_securities_list()` trả về danh sách các mã chứng khoán thuộc sàn HOSE và HNX, loại bỏ ETF.

### 2. Lấy dữ liệu giá cổ phiếu
- Hàm `fetch_data(symbol)`: Lấy dữ liệu giá cổ phiếu theo từng mã.
- Hàm `parallel_fetch_data(symbols)`: Lấy dữ liệu giá cổ phiếu cho nhiều mã cùng lúc bằng `ThreadPoolExecutor`.

### 3. Phân loại nến
Hàm `candle_type(ohlc_price)` phân loại nến thành 3 loại:
- "doji or red body": Thể hiện giá cao nhất cách xa giá đóng cửa.
- "hammer or green body": Giá thấp nhất cách xa giá đóng cửa.
- "normal": Các trường hợp khác.

### 4. Xác định breakout
Hàm `check_flat_base(row)` xác định xem cổ phiếu có phải trong giai đoạn tích lũy hay không dựa trên các tiêu chí:
- Biên độ giá trong 15 ngày < 8%.
- Khối lượng giao dịch trung bình > 15 tỷ VNĐ.
- Số nến xấu trong 15 ngày < 4.
- Giá đóng cửa > 10.000 VNĐ.

### 5. Xử lý và lưu trữ kết quả
Sau khi lấy dữ liệu và phân tích:
- Kết quả cổ phiếu cuối cùng được lưu vào danh sách `breakout_dates`.
- Những cổ phiếu tích lũy trong ngày giao dịch gần nhất được tìm và dùng để vẽ biểu đồ candlestick.

### 6. Vẽ biểu đồ candlestick
Chương trình sử dụng `mplfinance` để vẽ biểu đồ nến của những cổ phiếu tìm được ngày giao dịch gần nhất.

## Cách chạy chương trình
Chạy file Python với lệnh sau:
```bash
python 1. 'Flat base' tool'.py
```
Chương trình sẽ trả về danh sách cổ phiếu và vẽ biểu đồ candlestick.


