"""
utils/mock_generator.py
Tạo bộ dữ liệu lịch sử cổ phiếu HOSE thực tế (2018-2026) và dữ liệu bình luận mạng xã hội.
Đảm bảo hệ thống hoạt động ổn định 100% khi chạy offline hoặc khi API mạng bị giới hạn.
"""

import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Cấu hình giá cơ sở và đặc tính các mã cổ phiếu HOSE
HOSE_STOCKS_CONFIG = {
    'FPT': {'name': 'CTCP FPT', 'base_price': 35000, 'drift': 0.00045, 'volatility': 0.016, 'base_vol': 4500000},
    'VCB': {'name': 'Ngân hàng TMCP Ngoại thương VN (Vietcombank)', 'base_price': 55000, 'drift': 0.00030, 'volatility': 0.014, 'base_vol': 2500000},
    'VNM': {'name': 'CTCP Sữa Việt Nam (Vinamilk)', 'base_price': 120000, 'drift': -0.00010, 'volatility': 0.013, 'base_vol': 3200000},
    'HPG': {'name': 'CTCP Tập đoàn Hòa Phát', 'base_price': 22000, 'drift': 0.00035, 'volatility': 0.024, 'base_vol': 28000000},
    'MWG': {'name': 'CTCP Đầu tư Thế Giới Di Động', 'base_price': 42000, 'drift': 0.00025, 'volatility': 0.022, 'base_vol': 8500000},
    'VIC': {'name': 'Tập đoàn Vingroup', 'base_price': 75000, 'drift': -0.00015, 'volatility': 0.023, 'base_vol': 6000000},
    'SSI': {'name': 'CTCP Chứng khoán SSI', 'base_price': 18000, 'drift': 0.00038, 'volatility': 0.028, 'base_vol': 22000000},
    'VHM': {'name': 'CTCP Vinhomes', 'base_price': 65000, 'drift': -0.00012, 'volatility': 0.021, 'base_vol': 7000000},
    'TCB': {'name': 'Ngân hàng TMCP Kỹ thương VN (Techcombank)', 'base_price': 24000, 'drift': 0.00032, 'volatility': 0.020, 'base_vol': 15000000},
    'MBB': {'name': 'Ngân hàng TMCP Quân đội (MB Bank)', 'base_price': 16000, 'drift': 0.00030, 'volatility': 0.018, 'base_vol': 18000000},
    'STB': {'name': 'Ngân hàng TMCP Sài Gòn Thương Tín (Sacombank)', 'base_price': 14000, 'drift': 0.00040, 'volatility': 0.026, 'base_vol': 20000000},
    'CTG': {'name': 'Ngân hàng TMCP Công Thương VN (VietinBank)', 'base_price': 22000, 'drift': 0.00028, 'volatility': 0.019, 'base_vol': 12000000},
}


def generate_stock_history(symbol: str, start_date: str = '2018-01-01', end_date: str = '2026-08-31') -> pd.DataFrame:
    """
    Tạo dữ liệu chuỗi thời gian OHLCV mô phỏng chuẩn xác chuyển động hình học Brown (Geometric Brownian Motion)
    kết hợp dao động chu kỳ thị trường chứng khoán Việt Nam (Bull run 2020-2021, Downtrend 2022, Hồi phục 2023-2026).
    """
    config = HOSE_STOCKS_CONFIG.get(symbol, {
        'name': f'Doanh nghiệp {symbol}',
        'base_price': 30000,
        'drift': 0.0002,
        'volatility': 0.020,
        'base_vol': 5000000
    })
    
    # Tạo danh sách các ngày làm việc (Thứ 2 đến Thứ 6)
    dates = pd.date_range(start=start_date, end=end_date, freq='B')
    n = len(dates)
    
    # Seed theo mã để dữ liệu nhất quán qua các lần chạy
    seed = abs(hash(symbol)) % (2**32)
    np.random.seed(seed)
    
    # Chu kỳ thị trường chung VN-Index (Macro trend)
    t = np.linspace(0, 8.5, n)
    macro_wave = (
        0.15 * np.sin(2 * np.pi * t / 4.0) +      # Chu kỳ kinh tế 4 năm
        0.35 * np.sin(2 * np.pi * (t - 2.0) / 3.0) + # Chu kỳ bùng nổ 2020-2021
        0.05 * np.sin(2 * np.pi * t / 0.5)        # Biến động ngắn hạn
    )
    
    # Geometric Brownian Motion + Macro influence
    mu = config['drift']
    sigma = config['volatility']
    daily_returns = np.random.normal(mu, sigma, n) + np.gradient(macro_wave) * 0.02
    
    # Giới hạn biên độ trần/sàn HOSE (+/- 7%)
    daily_returns = np.clip(daily_returns, -0.069, 0.069)
    
    price_series = np.zeros(n)
    price_series[0] = config['base_price']
    
    for i in range(1, n):
        price_series[i] = price_series[i-1] * (1.0 + daily_returns[i])
    
    # Làm tròn giá thành đơn vị 50/100 VND (bước giá HOSE)
    price_series = np.round(price_series / 50.0) * 50.0
    
    # Sinh dữ liệu OHLCV
    opens = []
    highs = []
    lows = []
    closes = []
    volumes = []
    
    for i in range(n):
        c = price_series[i]
        # Open gần Close hôm trước với chút gap
        if i == 0:
            o = c * (1 + np.random.uniform(-0.005, 0.005))
        else:
            prev_c = closes[-1]
            o = prev_c * (1 + np.random.normal(0, 0.004))
            o = np.clip(o, prev_c * 0.931, prev_c * 1.069)
        
        # High và Low bao bọc Open và Close
        intra_max = max(o, c)
        intra_min = min(o, c)
        h = intra_max * (1 + abs(np.random.normal(0, 0.006)))
        l = intra_min * (1 - abs(np.random.normal(0, 0.006)))
        
        # Đảm bảo bước giá
        o = round(o / 50.0) * 50.0
        h = round(h / 50.0) * 50.0
        l = round(l / 50.0) * 50.0
        c = round(c / 50.0) * 50.0
        
        h = max(h, o, c)
        l = min(l, o, c)
        
        # Volume tỷ lệ thuận với độ biến động giá
        price_range = (h - l) / (c + 1e-6)
        vol_factor = 1.0 + price_range * 15.0 + np.random.uniform(-0.3, 0.5)
        vol = int(max(100000, config['base_vol'] * vol_factor))
        
        opens.append(o)
        highs.append(h)
        lows.append(l)
        closes.append(c)
        volumes.append(vol)
        
    df = pd.DataFrame({
        'Date': dates.strftime('%Y-%m-%d'),
        'Symbol': symbol,
        'Open': opens,
        'High': highs,
        'Low': lows,
        'Close': closes,
        'Volume': volumes
    })
    
    return df


def generate_all_sample_datasets(output_dir: str = 'data/raw'):
    """Tạo sẵn file CSV cho tất cả các mã HOSE cơ bản."""
    os.makedirs(output_dir, exist_ok=True)
    generated_files = []
    for symbol in HOSE_STOCKS_CONFIG.keys():
        file_path = os.path.join(output_dir, f'{symbol}.csv')
        df = generate_stock_history(symbol)
        df.to_csv(file_path, index=False)
        generated_files.append(file_path)
    return generated_files


def generate_sample_social_sentiment(symbol: str = 'FPT', output_dir: str = 'data/sample_social') -> str:
    """Tạo dữ liệu bình luận mạng xã hội mẫu (F319, Diễn đàn, Facebook) cho phân tích cảm xúc."""
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, f'{symbol}_social_sentiment.csv')
    
    templates_pos = [
        "Mã {s} kết quả kinh doanh quý này quá xuất sắc, doanh thu tăng trưởng 25%!",
        "Khối ngoại tiếp tục mua ròng mạnh {s}, tự tin nắm giữ trung hạn.",
        "Dòng tiền lớn đã nhập cuộc {s}, mục tiêu vượt đỉnh cũ sớm thôi anh em.",
        "Kỹ thuật tạo mô hình W đẹp tuyệt vời, RSI bứt phá ngưỡng 60, múc thôi.",
        "Ban lãnh đạo {s} công bố kế hoạch chia cổ tức tiền mặt 30%, quá uy tín.",
        "Công nghệ AI và Cloud của {s} ký thêm nhiều hợp đồng triệu đô từ Nhật Bản.",
        "Thị trường chỉnh nhưng {s} vẫn giữ sắc xanh vững vàng, cổ phiếu kim cương!",
        "Kỳ vọng {s} sẽ dẫn dắt VN-Index chinh phục mốc 1300 điểm.",
        "Xu hướng tăng trung dài hạn của {s} không thể cản phá, canh rung lắc gia tăng tỷ trọng.",
        "Lệnh to vào quét sạch lệnh bán của {s}, chuẩn bị đón cây CE rực rỡ!"
    ]
    
    templates_neu = [
        "Hôm nay {s} đi ngang tích lũy quanh vùng hỗ trợ, thanh khoản trung bình.",
        "Chờ đợi báo cáo tài chính kiểm toán của {s} để đánh giá chính xác hơn.",
        "Mã {s} đang kiểm tra lại đường MA20, chưa có tín hiệu bứt phá rõ rệt.",
        "Thị trường chung đang giằng co, {s} dao động trong biên độ hẹp 1-2%.",
        "Hôm nay là ngày giao dịch không hưởng quyền của {s}, giá điều chỉnh kỹ thuật.",
        "Khối tự doanh và khối ngoại mua bán cân bằng đối với mã {s}.",
        "Mức P/E của {s} hiện tại ở mức 18.5, tương đương mức định giá trung bình ngành.",
        "Thảo luận về tiềm năng mảng bán lẻ viễn thông của {s} trong giai đoạn tới.",
        "Tỷ lệ đòn bẩy margin của {s} tại các công ty chứng khoán vẫn ở mức an toàn."
    ]
    
    templates_neg = [
        "Áp lực chốt lời ngắn hạn đối với {s} đang tăng cao, cẩn trọng đu đỉnh.",
        "Khối ngoại quay đầu bán ròng {s} hơn 100 tỷ trong phiên sáng.",
        "Thủng mốc hỗ trợ cứng rồi, anh em nên hạ tỷ trọng {s} bảo toàn vốn.",
        "Thị trường xấu quá, {s} bị bán lan theo hiệu ứng tâm lý chung.",
        "Chỉ báo MACD của {s} phân kỳ âm, cảnh báo rủi ro điều chỉnh ngắn hạn.",
        "Tăng trưởng quý này có dấu hiệu chậm lại do chi phí vốn tăng cao.",
        "Tây xả ròng rã cả tuần, {s} gãy trend tăng ngắn hạn rồi.",
        "Thanh khoản sụt giảm nghiêm trọng, lực cầu bắt đáy {s} còn khá yếu."
    ]
    
    # Tạo các bình luận ngẫu nhiên gắn với ngày
    dates = pd.date_range(start='2025-01-01', end='2026-08-31', freq='D')
    rows = []
    np.random.seed(42)
    
    for d in dates:
        # Mỗi ngày có 3-8 bình luận
        num_comments = np.random.randint(3, 9)
        for _ in range(num_comments):
            r = np.random.rand()
            if r < 0.50:
                sentiment = 'Positive'
                score = np.random.uniform(0.5, 0.95)
                content = np.random.choice(templates_pos).format(s=symbol)
            elif r < 0.80:
                sentiment = 'Neutral'
                score = np.random.uniform(-0.1, 0.49)
                content = np.random.choice(templates_neu).format(s=symbol)
            else:
                sentiment = 'Negative'
                score = np.random.uniform(-0.95, -0.11)
                content = np.random.choice(templates_neg).format(s=symbol)
                
            author = f"investor_{np.random.randint(100, 999)}"
            channel = np.random.choice(['F319', 'FireAnt', 'Facebook Group', '24hMoney'])
            
            rows.append({
                'Date': d.strftime('%Y-%m-%d'),
                'StockCode': symbol,
                'Author': author,
                'Channel': channel,
                'Content': content,
                'Sentiment': sentiment,
                'SentimentScore': round(score, 3)
            })
            
    df_social = pd.DataFrame(rows)
    df_social.to_csv(file_path, index=False, encoding='utf-8-sig')
    return file_path


if __name__ == '__main__':
    print("Generating HOSE sample datasets...")
    files = generate_all_sample_datasets()
    print(f"Generated {len(files)} stock CSV files in data/raw/")
    soc_file = generate_sample_social_sentiment('FPT')
    print(f"Generated social sentiment sample in {soc_file}")
