# ỨNG DỤNG DỰ ĐOÁN XU HƯỚNG CỔ PHIẾU HOSE BẰNG CÁC THUẬT TOÁN KHAI THÁC DỮ LIỆU

**Môn học:** Khai thác dữ liệu và truyền thông xã hội  
**Đề tài:** Dự đoán xu hướng tăng/giảm của mã cổ phiếu trên sàn HOSE ở phiên giao dịch tiếp theo dựa trên dữ liệu lịch sử và các chỉ số kỹ thuật bằng các thuật toán khai thác dữ liệu.

---

## 1. Giới Thiệu Đề Tài

Thị trường chứng khoán Việt Nam (đặc biệt là sàn Giao dịch Chứng khoán TP.HCM - HOSE) là một môi trường đầu tư tài chính biến động phức tạp và chịu ảnh hưởng của nhiều yếu tố. Mục tiêu của đồ án này là ứng dụng các kiến thức và thuật toán khai thác dữ liệu (Data Mining) kinh điển được giảng dạy trong học phần để xây dựng hệ thống phân lớp nhị phân dự đoán xu hướng phiên giao dịch tiếp theo:
- **TĂNG ($\text{Target} = 1$):** Nếu $\text{Close}_{t+1} > \text{Close}_t$
- **GIẢM ($\text{Target} = 0$):** Nếu $\text{Close}_{t+1} \le \text{Close}_t$

---

## 2. Kiến Thức Bài Giảng Môn Học Được Áp Dụng

Đồ án tuân thủ chặt chẽ và thể hiện đầy đủ các chuyên đề trong bài giảng của giảng viên:

1. **Tiền xử lý dữ liệu (Bài 1 & 2):**
   - Làm sạch dữ liệu, khử trùng lặp (Duplicate Detection) theo Date.
   - Kiểm tra và loại bỏ các phiên giao dịch có dữ liệu không hợp lệ (Close &le; 0, High < Low, Volume &le; 0).
   - Biến đổi dữ liệu (Feature Engineering): Moving Averages (SMA 5, 10, 20; EMA 12, 26), Momentum (RSI 14, MACD, Signal, Hist), Volatility (Bollinger Upper/Middle/Lower), Lag Features ($t-1, t-2, t-3$).
   - Chuẩn hóa dữ liệu (StandardScaler) **chống Data Leakage** (chỉ `fit` trên tập Train).

2. **Lý thuyết Tập thô & Rút gọn thuộc tính (Bài 3 & 4 - Rough Sets & Reduct):**
   - Xây dựng Bảng quyết định và Ma trận phân biệt (Discernibility Matrix $M(S)$).
   - Xác định tập thuộc tính cốt lõi $\text{CORE}(C)$ và tập rút gọn $\text{RED}(C)$.
   - So sánh trực quan với các phương pháp lựa chọn đặc trưng: SelectKBest (ANOVA F-value) và Random Forest Gini Importance.

3. **Các mô hình phân lớp (Bài 5, 5.1, 7):**
   - **Decision Tree (`DecisionTreeClassifier`):** Phân chia không gian đặc trưng theo tiêu chuẩn Gini Index / Entropy.
   - **Naive Bayes (`GaussianNB`):** Ước lượng xác suất có điều kiện dựa trên Định lý Bayes và phân phối chuẩn Gauss.
   - **Logistic Regression (`LogisticRegression`):** Mô hình phân loại tuyến tính ánh xạ qua hàm kích hoạt Sigmoid.
   - **Random Forest (`RandomForestClassifier`):** Ensemble kết hợp nhiều cây quyết định độc lập (Bagging) và biểu quyết đa số.

4. **Đánh giá hiệu năng mô hình (Bài 7):**
   - Ma trận nhầm lẫn (Confusion Matrix): $TP, FP, TN, FN$.
   - Các chỉ số: $\text{Accuracy}, \text{Error Rate}, \text{Precision}, \text{Recall}, \text{Specificity}, \text{F1-Score}$.
   - Đường cong ROC (Receiver Operating Characteristic) và chỉ số AUC.
   - Tự động xếp hạng và xác định **Best Model** theo F1-Score.

5. **Gom cụm dữ liệu (Bài 6 - Clustering K-Means):**
   - Phân nhóm toàn bộ các mã cổ phiếu HOSE theo đặc điểm thị trường (Lợi suất, Độ biến động rủi ro, Khối lượng giao dịch bình quân, RSI).
   - Phương pháp Elbow (Inertia/SSE) xác định số cụm tối ưu ($k=3$).

6. **Khai thác truyền thông xã hội (Social Media Sentiment):**
   - Thu thập và phân loại cảm xúc (Tích cực / Trung lập / Tiêu cực) từ diễn đàn chứng khoán (F319, FireAnt).
   - Đo lường mức độ tương quan giữa chỉ số tâm lý nhà đầu tư và biến động giá cổ phiếu.

---

## 3. Cấu Trúc Thư Mục

```text
stock_prediction_project/
├── app/
│   ├── __init__.py          # Khởi tạo Flask App và template filters
│   ├── routes.py            # Web Routes & REST API Endpoints
│   ├── data_loader.py       # Tải dữ liệu (API Online, CSV Offline, Upload)
│   ├── preprocessing.py     # Tiền xử lý KDD & Chống Data Leakage
│   ├── indicators.py        # Tính toán 25+ chỉ số kỹ thuật & Target
│   ├── reduct_selection.py  # Thuật toán Tập thô (Reduct) & Lựa chọn đặc trưng
│   ├── models.py            # Huấn luyện 4 thuật toán & Lưu trữ Joblib
│   ├── evaluation.py        # Đánh giá Accuracy, Precision, Recall, F1, Confusion Matrix, ROC
│   ├── clustering.py        # Gom cụm K-Means thị trường cổ phiếu
│   └── sentiment.py         # Khai thác cảm xúc mạng xã hội
├── data/
│   ├── raw/                 # File CSV lịch sử chuẩn cho 12 mã HOSE (2018-2026)
│   ├── sample_social/       # File CSV bình luận mạng xã hội mẫu
│   └── uploaded/            # Thư mục chứa file CSV do người dùng tải lên
├── models/                  # Lưu trữ các file mô hình đã huấn luyện (.pkl)
├── static/
│   ├── css/style.css        # Giao diện Financial Dark Theme & Glassmorphism
│   └── js/main.js           # AJAX & Plotly Interactive Chart Renderers
├── templates/               # 11 Giao diện HTML Web Dashboard hoàn chỉnh
├── utils/
│   ├── helpers.py           # Tiện ích định dạng tiền tệ, JSON Encoder, Logger
│   └── mock_generator.py    # Bộ sinh dữ liệu mẫu thực tế
├── START_APP.bat            # File khởi chạy 1-Click (Tự tìm Python & Mở trình duyệt)
├── desktop_launcher.py      # Script khởi chạy desktop
├── requirements.txt         # Danh sách thư viện phụ thuộc
├── config.py                # Cấu hình hệ thống
├── main.py                  # Entry point
├── README.md                # Hướng dẫn sử dụng và tài liệu kỹ thuật
└── REPORT_OUTLINE.md        # Đề cương chi tiết báo cáo đồ án đại học (6 Chương)
```

---

## 4. Hướng Dẫn Cài Đặt & Khởi Chạy

### Cách 1: Khởi chạy 1-Click (Không dùng Command Line)
Chỉ cần **Double Click** vào file:
```text
START_APP.bat
```
File này sẽ tự động:
1. Tìm kiếm đường dẫn Python 3.11 trên hệ thống.
2. Khởi động Flask Server ngầm.
3. Tự động bật trình duyệt Web mặc định truy cập `http://127.0.0.1:5000`.

### Cách 2: Khởi chạy thủ công bằng Terminal (Dành cho nhà phát triển)
1. Cài đặt các thư viện cần thiết:
   ```bash
   pip install -r requirements.txt
   ```
2. Chạy ứng dụng:
   ```bash
   python main.py
   ```
3. Mở trình duyệt và truy cập: `http://127.0.0.1:5000`

---

## 5. Danh Sách Các Mã Cổ Phiếu HOSE Có Sẵn

Hệ thống cung cấp sẵn dữ liệu lịch sử đầy đủ từ 2018 đến 2026 cho 12 mã cổ phiếu đầu ngành:
- **FPT:** CTCP FPT (Công nghệ thông tin, Viễn thông)
- **VCB:** Ngân hàng TMCP Ngoại thương Việt Nam (Vietcombank)
- **VNM:** CTCP Sữa Việt Nam (Vinamilk)
- **HPG:** CTCP Tập đoàn Hòa Phát (Thép & Công nghiệp)
- **MWG:** CTCP Đầu tư Thế Giới Di Động (Bán lẻ)
- **VIC:** Tập đoàn Vingroup (Bất động sản, Công nghiệp)
- **SSI:** CTCP Chứng khoán SSI (Tài chính chứng khoán)
- **VHM:** CTCP Vinhomes (Bất động sản)
- **TCB:** Ngân hàng TMCP Kỹ thương Việt Nam (Techcombank)
- **MBB:** Ngân hàng TMCP Quân đội (MB Bank)
- **STB:** Ngân hàng TMCP Sài Gòn Thương Tín (Sacombank)
- **CTG:** Ngân hàng TMCP Công Thương Việt Nam (VietinBank)

Người dùng cũng có thể tải lên file CSV của bất kỳ mã cổ phiếu nào khác thông qua nút **"Nạp Dữ Liệu CSV"** trên thanh điều hướng.

---

## 6. Cam Kết Không Data Leakage

Hệ thống cam kết 100% không xảy ra hiện tượng rò rỉ dữ liệu (Data Leakage):
- Không đưa $\text{Close}_{t+1}$ vào tập đặc trưng tại thời điểm $t$.
- Phân chia tập Train/Test theo chuỗi thời gian (70% đầu làm Train, 30% sau làm Test), không shuffle ngẫu nhiên.
- Bộ chuẩn hóa `StandardScaler` chỉ được `fit()` trên dữ liệu $X_{\text{train}}$.

---

## 7. Khuyến Cáo Học Thuật

> **Lưu ý:** Kết quả dự đoán của hệ thống chỉ mang mục đích học tập, nghiên cứu khoa học và minh họa ứng dụng của các thuật toán khai thác dữ liệu, không phải là lời khuyên hay khuyến nghị đầu tư tài chính.
