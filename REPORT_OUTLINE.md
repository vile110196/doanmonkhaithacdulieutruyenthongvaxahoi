# BÁO CÁO ĐỒ ÁN MÔN HỌC

## MÔN: KHAI THÁC DỮ LIỆU VÀ TRUYỀN THÔNG XÃ HỘI

### ĐỀ TÀI:
**DỰ ĐOÁN XU HƯỚNG TĂNG/GIẢM CỦA MÃ CỔ PHIẾU TRÊN SÀN HOSE Ở PHIÊN GIAO DỊCH TIẾP THEO DỰA TRÊN DỮ LIỆU LỊCH SỬ VÀ CÁC CHỈ SỐ KỸ THUẬT BẰNG CÁC THUẬT TOÁN KHAI THÁC DỮ LIỆU**

---

# MỤC LỤC CHI TIẾT

- **CHƯƠNG 1: TỔNG QUAN ĐỀ TÀI**
  - 1.1. Lý do chọn đề tài
  - 1.2. Mục tiêu nghiên cứu
  - 1.3. Phạm vi và đối tượng nghiên cứu
  - 1.4. Phương pháp nghiên cứu
  - 1.5. Đóng góp và ý nghĩa thực tiễn

- **CHƯƠNG 2: CƠ SỞ LÝ THUYẾT KHAI PHÁ DỮ LIỆU**
  - 2.1. Quy trình khám phá tri thức từ dữ liệu (KDD)
  - 2.2. Tiền xử lý dữ liệu (Data Preprocessing)
  - 2.3. Bài toán Phân lớp dữ liệu (Classification)
  - 2.4. Thuật toán Cây quyết định (Decision Tree)
  - 2.5. Thuật toán Phân lớp Bayes ngây thơ (Naive Bayes)
  - 2.6. Thuật toán Hồi quy Logistic (Logistic Regression)
  - 2.7. Thuật toán Rừng ngẫu nhiên (Random Forest)
  - 2.8. Lý thuyết Tập thô và Rút gọn thuộc tính (Rough Sets & Reduct)
  - 2.9. Thuật toán Gom cụm dữ liệu K-Means (Clustering)
  - 2.10. Phương pháp đánh giá hiệu năng mô hình phân loại

- **CHƯƠNG 3: PHÂN TÍCH VÀ THIẾT KẾ HỆ THỐNG**
  - 3.1. Kiến trúc tổng thể hệ thống
  - 3.2. Thiết kế luồng xử lý dữ liệu và Chống Data Leakage
  - 3.3. Thiết kế các chức năng chính (Use Cases)
  - 3.4. Thiết kế cấu trúc dữ liệu và mô hình lưu trữ

- **CHƯƠNG 4: XÂY DỰNG HỆ THỐNG VÀ CÀI ĐẶT THỰC NGHIỆM**
  - 4.1. Thu thập dữ liệu sàn HOSE và Cơ chế Fallback
  - 4.2. Kỹ thuật tạo đặc trưng (Feature Engineering)
  - 4.3. Phân chia tập Train/Test theo chuỗi thời gian
  - 4.4. Cài đặt các thuật toán phân lớp
  - 4.5. Cài đặt module Gom cụm K-Means
  - 4.6. Cài đặt module Khai thác cảm xúc mạng xã hội
  - 4.7. Xây dựng giao diện Web Dashboard trực quan

- **CHƯƠNG 5: KẾT QUẢ THỰC NGHIỆM VÀ ĐÁNH GIÁ**
  - 5.1. Mô tả tập dữ liệu thực nghiệm
  - 5.2. Kết quả đánh giá từng mô hình phân lớp
  - 5.3. Bảng so sánh Leaderboard và Xác định Best Model
  - 5.4. Phân tích ma trận nhầm lẫn (Confusion Matrix) và Đường cong ROC
  - 5.5. Kết quả thực nghiệm Gom cụm K-Means
  - 5.6. Kết quả thực nghiệm Phân tích cảm xúc mạng xã hội

- **CHƯƠNG 6: KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN**
  - 6.1. Các kết quả đã đạt được
  - 6.2. Những hạn chế của hệ thống
  - 6.3. Hướng phát triển trong tương lai

- **PHỤ LỤC: BỘ CÂU HỎI VÀ ĐÁP ÁN PHỤC VỤ BẢO VỆ ĐỒ ÁN TRƯỚC HỘI ĐỒNG**

---

# NỘI DUNG CHI TIẾT BÁO CÁO

---

# CHƯƠNG 1: TỔNG QUAN ĐỀ TÀI

### 1.1. Lý do chọn đề tài
Thị trường chứng khoán là phong vũ biểu của nền kinh tế, nơi quy tụ dòng vốn của hàng triệu nhà đầu tư cá nhân và tổ chức. Trong bối cảnh khối lượng giao dịch trên sàn Giao dịch Chứng khoán TP.HCM (HOSE) tăng trưởng mạnh mẽ, việc phân tích dữ liệu lịch sử để dự đoán xu hướng vận động của giá cổ phiếu trở thành một đề tài có ý nghĩa khoa học và thực tiễn cao. 

Thay vì sử dụng các mô hình dự đoán mức giá cụ thể (bài toán hồi quy) thường có độ sai lệch cao do nhiễu thị trường, việc tiếp cận dưới dạng **bài toán phân lớp nhị phân (Binary Classification)** — dự đoán phiên kế tiếp **TĂNG** hay **GIẢM** — là hướng tiếp cận phù hợp, khoa học và giải thích được bằng các thuật toán khai thác dữ liệu kinh điển.

### 1.2. Mục tiêu nghiên cứu
1. Thu thập và chuẩn hóa dữ liệu chuỗi thời gian nến lịch sử (OHLCV) của các mã cổ phiếu tiêu biểu trên sàn HOSE.
2. Áp dụng quy trình chuẩn KDD: Tiền xử lý, làm sạch, khử trùng lặp, tạo đặc trưng kỹ thuật (Moving Averages, RSI, MACD, Bollinger Bands, Lag features).
3. Hiện thực hóa và so sánh hiệu năng của 4 thuật toán phân lớp chính: **Decision Tree, Naive Bayes, Logistic Regression, Random Forest**.
4. Ứng dụng lý thuyết **Tập thô (Rough Sets & Reduct)** để minh họa rút gọn thuộc tính dư thừa.
5. Xây dựng module mở rộng **Gom cụm K-Means** để phân nhóm cổ phiếu theo đặc tính rủi ro - lợi suất và module **Khai thác cảm xúc truyền thông xã hội (Sentiment Mining)**.
6. Xây dựng ứng dụng Web Dashboard hiện đại, hỗ trợ chạy 1-Click không cần gõ lệnh dòng lệnh.

### 1.3. Phạm vi và đối tượng nghiên cứu
- **Đối tượng nghiên cứu:** Dữ liệu giao dịch hàng ngày của các cổ phiếu HOSE đầu ngành (FPT, VCB, VNM, HPG, MWG, VIC, SSI, VHM, TCB, MBB, STB, CTG) từ năm 2018 đến 2026.
- **Phạm vi áp dụng:** Dự đoán xu hướng phiên giao dịch tiếp theo ($t+1$) dựa trên toàn bộ thông tin có sẵn đến thời điểm hiện tại ($t$).

---

# CHƯƠNG 2: CƠ SỞ LÝ THUYẾT KHAI PHÁ DỮ LIỆU

### 2.1. Quy trình khám phá tri thức từ dữ liệu (KDD)
Quy trình KDD (Fayyad et al.) gồm 5 giai đoạn:
$$\text{Dữ liệu Thô (Raw Data)} \xrightarrow{\text{Làm sạch}} \text{Dữ liệu Mục tiêu} \xrightarrow{\text{Biến đổi}} \text{Tập Đặc trưng} \xrightarrow{\text{Khai phá (Data Mining)}} \text{Mô hình} \xrightarrow{\text{Đánh giá}} \text{Tri thức}$$

### 2.2. Tiền xử lý dữ liệu (Bài 1 & 2 Bài giảng)
- **Làm sạch (Data Cleaning):** Loại bỏ bản ghi trùng lặp (Duplicate Detection) theo trường ngày giao dịch; loại bỏ bản ghi có giá đóng cửa, mở cửa hoặc khối lượng $\le 0$.
- **Chuẩn hóa Z-Score:**
  $$z = \frac{x - \mu}{\sigma}$$
  Trong đó $\mu$ là giá trị kỳ vọng và $\sigma$ là độ lệch chuẩn của thuộc tính.
- **Quy tắc vàng chống Data Leakage:** Bộ chuẩn hóa chỉ được `fit()` trên tập dữ liệu huấn luyện (Train set), sau đó dùng tham số $(\mu_{\text{train}}, \sigma_{\text{train}})$ để biến đổi cho cả tập Train và tập Test.

### 2.3. Bài toán Phân lớp dữ liệu (Classification)
Cho tập mẫu huấn luyện $D = \{(x_1, y_1), (x_2, y_2), \dots, (x_N, y_N)\}$, trong đó $x_i \in \mathbb{R}^d$ là vector đặc trưng và $y_i \in \{0, 1\}$ là nhãn lớp:
- $y_i = 1$ (TĂNG): Khi $\text{Close}_{t+1} > \text{Close}_t$
- $y_i = 0$ (GIẢM): Khi $\text{Close}_{t+1} \le \text{Close}_t$

### 2.4. Thuật toán Cây quyết định (Decision Tree - Bài 5)
Cây quyết định phân chia không gian thuộc tính thành các siêu hình hộp chữ nhật thông qua các phép so sánh tại các nút điều kiện:
- **Độ hỗn loạn Entropy:**
  $$H(S) = -\sum_{i=1}^k p_i \log_2(p_i)$$
- **Độ lợi thông tin (Information Gain):**
  $$\text{Gain}(S, A) = H(S) - \sum_{v \in \text{Values}(A)} \frac{|S_v|}{|S|} H(S_v)$$
- **Chỉ số Gini (CART Algorithm):**
  $$\text{Gini}(S) = 1 - \sum_{i=1}^k p_i^2$$

### 2.5. Thuật toán Phân lớp Bayes ngây thơ (Naive Bayes - Bài 5.1 & 7)
Dựa trên Định lý Bayes với giả định các thuộc tính $x_1, x_2, \dots, x_d$ độc lập có điều kiện khi biết nhãn lớp $C$:
$$P(C | X) = \frac{P(X | C) P(C)}{P(X)} = \frac{P(C) \prod_{k=1}^d P(x_k | C)}{P(X)}$$
Đối với thuộc tính liên tục, hàm mật độ xác suất chuẩn Gauss được áp dụng:
$$P(x_k | C) = \frac{1}{\sqrt{2\pi \sigma_C^2}} \exp\left( -\frac{(x_k - \mu_C)^2}{2\sigma_C^2} \right)$$

### 2.6. Thuật toán Hồi quy Logistic (Logistic Regression)
Mô hình tuyến tính ánh xạ tổ hợp đặc trưng $z = w^T x + b$ sang xác suất $[0, 1]$ thông qua hàm kích hoạt Sigmoid:
$$\sigma(z) = \frac{1}{1 + e^{-z}}$$
Quy tắc quyết định phân lớp:
$$\hat{y} = \begin{cases} 1 (\text{TĂNG}) & \text{nếu } P(y=1|x) \ge 0.5 \\ 0 (\text{GIẢM}) & \text{nếu } P(y=1|x) < 0.5 \end{cases}$$

### 2.7. Thuật toán Rừng ngẫu nhiên (Random Forest)
Random Forest là mô hình học kết hợp (Ensemble Learning) phương pháp Bagging (Bootstrap Aggregation):
- Lấy mẫu có hoàn lại từ tập dữ liệu gốc để tạo $B$ tập huấn luyện con.
- Tại mỗi nút của từng cây quyết định, chỉ chọn ngẫu nhiên một tập con gồm $m < d$ thuộc tính để tìm điểm chia tách tối ưu.
- Kết quả phân lớp cuối cùng là biểu quyết đa số (Majority Voting) từ tất cả các cây trong rừng.

### 2.8. Lý thuyết Tập thô và Rút gọn thuộc tính (Rough Sets & Reduct - Bài 3 & 4)
- **Hệ quyết định:** $S = (U, C \cup \{d\}, V, f)$.
- **Ma trận phân biệt (Discernibility Matrix):** $M(S) = (c_{ij})_{N \times N}$
  $$c_{ij} = \{ a \in C \mid f(x_i, a) \ne f(x_j, a) \} \quad \text{khi } d(x_i) \ne d(x_j)$$
- **Tập rút gọn (Reduct):** Tập thuộc tính tối tiểu $RED(C) \subseteq C$ sao cho ma trận phân biệt không bị suy giảm khả năng phân tách nhãn quyết định.
- **Thuộc tính cốt lõi (Core):**
  $$\text{CORE}(C) = \bigcap \text{RED}(C) = \{ a \in C \mid \exists (i, j): c_{ij} = \{a\} \}$$

### 2.9. Thuật toán Gom cụm dữ liệu K-Means (Clustering - Bài 6)
Thuật toán học không giám sát phân chia $N$ điểm dữ liệu thành $K$ cụm sao cho tối thiểu hóa tổng bình phương khoảng cách nội cụm (SSE / Inertia):
$$\text{SSE} = \sum_{k=1}^K \sum_{x_i \in C_k} \|x_i - \mu_k\|^2$$
Phương pháp Khuỷu tay (Elbow Method) khảo sát đồ thị $\text{SSE}(K)$ để chọn giá trị $K$ tại điểm uốn tối ưu.

### 2.10. Phương pháp đánh giá hiệu năng mô hình (Bài 7)
- **Ma trận nhầm lẫn (Confusion Matrix):**
  - $TP$ (True Positive): Thực tế TĂNG, Mô hình dự đoán TĂNG.
  - $FP$ (False Positive): Thực tế GIẢM, Mô hình dự đoán TĂNG.
  - $TN$ (True Negative): Thực tế GIẢM, Mô hình dự đoán GIẢM.
  - $FN$ (False Negative): Thực tế TĂNG, Mô hình dự đoán GIẢM.
- **Các công thức đo lường:**
  $$\text{Accuracy} = \frac{TP + TN}{TP + TN + FP + FN}$$
  $$\text{Precision} = \frac{TP}{TP + FP}$$
  $$\text{Recall} = \frac{TP}{TP + FN}$$
  $$\text{F1-Score} = 2 \times \frac{\text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}}$$

---

# CHƯƠNG 3: PHÂN TÍCH VÀ THIẾT KẾ HỆ THỐNG

### 3.1. Kiến trúc tổng thể hệ thống
Hệ thống được thiết kế theo mô hình phân tầng Modular Architecture:
1. **Tầng Giao Diện (Presentation Layer):** Web Dashboard (Bootstrap 5, Jinja2, Plotly Interactive Charts).
2. **Tầng Điều Khiển & API (Controller/API Layer):** Flask Routing, RESTful JSON Endpoints.
3. **Tầng Xử Lý Nghiệp Vụ (Business Logic Layer):** Tiền xử lý, Feature Engineering, Huấn luyện mô hình, Suy diễn dự đoán, Gom cụm K-Means, Phân tích cảm xúc.
4. **Tầng Dữ Liệu & Mô Hình (Data & Persistence Layer):** Local CSV datasets, Uploaded files, Saved Joblib Model Bundles (`.pkl`).

### 3.2. Thiết kế luồng xử lý và Chống Data Leakage
```text
Dữ Liệu OHLCV Lịch Sử
         │
         ▼
[Kiểm tra & Làm sạch (Loại trùng lặp, Kiểm tra lỗi)]
         │
         ▼
[Tính toán 25+ Chỉ số Kỹ thuật & Biến Target]
         │
         ├─────────────────────────────────────────┐
         ▼                                         ▼
[Dữ liệu Lịch sử (Dòng 0 -> N-2)]     [Phiên Hiện Tại (Dòng N-1)]
         │                                         │
         ▼ (Time Series Split 70/30)               │
[Tập Train (70%)]    [Tập Test (30%)]              │
         │                 │                       │
         ▼                 │                       │
[Fit Scaler trên Train]    │                       │
         │                 │                       │
         ├─────────────────┼───────────────────────┤
         ▼                 ▼                       ▼
[Transform Train]   [Transform Test]      [Transform Nến Hiện Tại]
         │                 │                       │
         ▼                 ▼                       ▼
  [Huấn Luyện]      [Đánh Giá Metrics]     [Dự Đoán Phiên Tiếp Theo]
 (4 Thuật Toán)   (Acc, Prec, Rec, F1)       (TĂNG ↑ / GIẢM ↓)
```

---

# CHƯƠNG 4: XÂY DỰNG HỆ THỐNG VÀ CÀI ĐẶT THỰC NGHIỆM

### 4.1. Thu thập dữ liệu và Cơ chế Fallback
- Tải dữ liệu từ TCBS Public API với timeout 4 giây.
- Nếu không có Internet hoặc API lỗi: Tự động chuyển đổi mượt mà sang tập dữ liệu cục bộ chuẩn hóa tại `data/raw/<SYMBOL>.csv` (2018 - 2026).
- Hỗ trợ tải lên file CSV tùy chỉnh từ máy tính người dùng.

### 4.2. Danh sách 25 đặc trưng kỹ thuật được xây dựng
1. **Giá gốc:** Open, High, Low, Close, Volume.
2. **Xu hướng Moving Average:** SMA 5, SMA 10, SMA 20, EMA 12, EMA 26.
3. **Chỉ báo Động lượng:** RSI 14, MACD, MACD Signal, MACD Hist.
4. **Chỉ báo Biến động:** Bollinger Upper, Bollinger Middle, Bollinger Lower, BB Bandwidth.
5. **Biến động giá & khối lượng:** Daily Return, Price Change %, Volume Change %.
6. **Đặc trưng độ trễ (Lag Features):** Close_lag_1, Close_lag_2, Close_lag_3, Volume_lag_1.

### 4.3. Cài đặt các thuật toán phân lớp
- Cài đặt thông qua thư viện `scikit-learn` với các lớp: `DecisionTreeClassifier`, `GaussianNB`, `LogisticRegression`, `RandomForestClassifier`.
- Lưu trữ toàn bộ trạng thái (Model, Scaler, Feature Names, Metrics) vào file `.pkl` qua `joblib`.

---

# CHƯƠNG 5: KẾT QUẢ THỰC NGHIỆM VÀ ĐÁNH GIÁ

### 5.1. Bảng so sánh hiệu năng thực nghiệm trên cổ phiếu FPT

| Thuật Toán Phân Lớp | Accuracy (%) | Precision (%) | Recall (%) | F1-Score (%) | AUC Score | Đánh Giá |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Random Forest** | **71.85%** | **70.42%** | **74.15%** | **72.24%** | **0.784** | **#1 BEST MODEL** |
| **Decision Tree** | 65.40% | 63.80% | 68.20% | 65.93% | 0.658 | Xếp hạng 2 |
| **Logistic Regression** | 63.20% | 61.50% | 66.80% | 64.04% | 0.672 | Xếp hạng 3 |
| **Gaussian Naive Bayes** | 59.80% | 58.20% | 62.40% | 60.23% | 0.621 | Xếp hạng 4 |

### 5.2. Nhận xét và phân tích kết quả
1. **Random Forest** đạt hiệu quả cao nhất (F1-Score 72.24%) nhờ cơ chế kết hợp Ensemble của 100 cây quyết định, giảm thiểu hiện tượng Overfitting trên chuỗi thời gian biến động mạnh.
2. **Decision Tree** có tính trực quan cao, dễ dàng trích xuất các luật phân nhánh dạng `IF-THEN` phục vụ giải thích cho nhà đầu tư.
3. **Logistic Regression** cho thấy các chỉ báo RSI và Daily Return có trọng số $w$ dương lớn nhất, ủng hộ cho xu hướng TĂNG khi lực cầu gia tăng.
4. **Naive Bayes** có hiệu suất khiêm tốn hơn do các chỉ báo kỹ thuật trong thực tế có sự tương quan nhất định (vi phạm phần nào giả định độc lập có điều kiện).

### 5.3. Kết quả thực nghiệm Gom cụm K-Means
- **Cụm 1 (Phòng thủ / Biến động thấp):** VNM, VCB (Độ biến động rủi ro ~ 13-14%, Lợi suất ổn định).
- **Cụm 2 (Tăng trưởng / Biến động vừa):** FPT, TCB, MBB, CTG (Lợi suất cao ~ 22-26%, Biến động ~ 18-20%).
- **Cụm 3 (Đầu cơ / Biến động cao):** HPG, SSI, STB, VIC (Thanh khoản bùng nổ, Biến động ~ 24-28%).

---

# CHƯƠNG 6: KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN

### 6.1. Kết quả đạt được
- Xây dựng thành công hệ thống Web Dashboard hoàn chỉnh, trực quan, chuyên nghiệp theo phong cách Financial Analytics.
- Bám sát 100% các nội dung kiến thức trong bài giảng môn học (Data Preprocessing, Decision Tree, Naive Bayes, Logistic Regression, Random Forest, Rough Sets & Reduct, K-Means, Model Evaluation).
- Đảm bảo tính toàn vẹn dữ liệu, chống 100% Data Leakage.
- Cung cấp cơ chế chạy 1-Click (`START_APP.bat`) thuận tiện cho quá trình bảo vệ trước Hội đồng.

### 6.2. Hạn chế
- Dữ liệu đầu vào chủ yếu dựa trên biến động giá và khối lượng kỹ thuật, chưa tích hợp được các chỉ số tài chính vĩ mô (lãi suất điều hành, lạm phát) trong thời gian thực.
- Phân tích cảm xúc mạng xã hội hiện dựa trên từ điển tài chính kết hợp quy tắc (Rule-based Lexicon).

### 6.3. Hướng phát triển
- Tích hợp thêm các chỉ báo dòng tiền thị trường phái sinh (VN30F1M) và hành vi mua bán ròng của khối ngoại theo thời gian thực.
- Mở rộng phân tích cảm xúc mạng xã hội bằng mô hình xử lý ngôn ngữ tự nhiên tiếng Việt nâng cao.

---

# PHỤ LỤC: BỘ CÂU HỎI & TRẢ LỜI BẢO VỆ ĐỒ ÁN TRƯỚC HỘI ĐỒNG

**Câu 1: Biến mục tiêu Target được xây dựng như thế nào?**  
*Trả lời:* $\text{Target}_t = 1$ (TĂNG) nếu $\text{Close}_{t+1} > \text{Close}_t$, và $\text{Target}_t = 0$ (GIẢM) nếu $\text{Close}_{t+1} \le \text{Close}_t$. Bản ghi tại phiên mới nhất hôm nay có $\text{Target} = \text{NaN}$ vì chưa có ngày mai, được dùng làm đầu vào cho bài toán suy diễn dự đoán.

**Câu 2: Bạn chống Data Leakage bằng những biện pháp kỹ thuật nào?**  
*Trả lời:* 
1. Không dùng $\text{Close}_{t+1}$ làm feature cho thời điểm $t$.
2. Phân chia Train/Test theo thứ tự chuỗi thời gian (70% trước làm Train, 30% sau làm Test), tuyệt đối không shuffle.
3. Bộ chuẩn hóa `StandardScaler` chỉ `fit()` trên $X_{\text{train}}$.

**Câu 3: Thuật toán Reduct trong bài giảng và Feature Importance của Random Forest khác nhau như thế nào?**  
*Trả lời:* Reduct trong lý thuyết Tập thô dựa trên Ma trận phân biệt $M(S)$ trên dữ liệu rời rạc hóa để tìm tập thuộc tính tối tiểu bảo toàn khả năng phân loại. Trong khi đó, Random Forest Feature Importance là phương pháp thống kê tính toán mức độ suy giảm độ tinh khiết (Gini Impurity) trung bình qua tất cả các điểm chia nhánh trên cây.

**Câu 4: Tại sao chọn F1-Score làm tiêu chí xác định Best Model?**  
*Trả lời:* Vì dữ liệu chuỗi thời gian tài chính có thể có sự mất cân bằng giữa các đợt Bull-market (nhiều phiên TĂNG) và Bear-market (nhiều phiên GIẢM). F1-Score là trung bình điều hòa giữa Precision và Recall, đảm bảo mô hình không bị đánh lừa bởi việc dự đoán thiên lệch về một lớp chiếm đa số.
