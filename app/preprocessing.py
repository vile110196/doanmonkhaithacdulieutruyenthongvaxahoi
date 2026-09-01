"""
app/preprocessing.py
Module tiền xử lý dữ liệu chuẩn quy trình KDD (Knowledge Discovery in Databases) bám sát Bài giảng:
1. Data Cleaning (Làm sạch dữ liệu, xử lý trùng lặp, missing values, dữ liệu không hợp lệ).
2. Data Transformation & Feature Engineering.
3. Chronological Train/Test Split (Phân chia tập huấn luyện/kiểm thử theo chuỗi thời gian).
4. Feature Scaling (Chuẩn hóa dữ liệu bằng StandardScaler CHỈ FIT TRÊN TẬP TRAIN - Tránh Data Leakage).
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from app.indicators import calculate_all_features_and_target, FEATURE_COLUMNS
from utils.helpers import logger


def clean_raw_data(df: pd.DataFrame) -> (pd.DataFrame, dict):
    """
    Tiền xử lý làm sạch dữ liệu thô (Bài 1 & 2 Bài giảng):
    - Loại bỏ hàng trùng lặp theo Date.
    - Sắp xếp tăng dần theo thời gian.
    - Kiểm tra và loại bỏ các giá trị không hợp lệ (High < Low, Close <= 0, Volume < 0).
    - Thống kê các thông số chất lượng dữ liệu.
    """
    initial_rows = len(df)
    
    # 1. Loại bỏ trùng lặp theo ngày
    df = df.drop_duplicates(subset=['Date']).copy()
    duplicates_removed = initial_rows - len(df)
    
    # 2. Ép kiểu dữ liệu và sắp xếp theo ngày
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date').reset_index(drop=True)
    df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
    
    for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
    # 3. Loại bỏ bản ghi không hợp lệ
    valid_mask = (
        (df['Close'] > 0) & 
        (df['Open'] > 0) & 
        (df['High'] >= df['Low']) & 
        (df['Volume'] >= 0)
    )
    invalid_count = (~valid_mask).sum()
    df = df[valid_mask].reset_index(drop=True)
    
    stats = {
        'initial_rows': initial_rows,
        'duplicates_removed': duplicates_removed,
        'invalid_rows_removed': invalid_count,
        'clean_rows': len(df),
        'start_date': df['Date'].iloc[0] if len(df) > 0 else "N/A",
        'end_date': df['Date'].iloc[-1] if len(df) > 0 else "N/A",
    }
    
    return df, stats


def prepare_dataset_for_modeling(df: pd.DataFrame, feature_cols: list = None) -> (pd.DataFrame, pd.DataFrame, pd.Series, pd.DataFrame):
    """
    Tạo đặc trưng và phân tách dữ liệu huấn luyện/dự đoán:
    - Tính toàn bộ Indicators & Lag features.
    - Loại bỏ các dòng NaN ở đầu (do cửa sổ trượt của MA26, MACD).
    - Tách riêng hàng cuối cùng (Latest Row) để dùng cho DỰ ĐOÁN PHIÊN KẾ TIẾP.
    - Dữ liệu lịch sử còn lại (có nhãn Target) dùng cho Train/Test.
    
    Trả về:
    - full_df: DataFrame đầy đủ kèm features
    - X: Ma trận đặc trưng lịch sử
    - y: Vector nhãn Target lịch sử
    - latest_candle: Bản ghi phiên giao dịch mới nhất
    """
    if feature_cols is None:
        feature_cols = FEATURE_COLUMNS
        
    # Tính toán đặc trưng
    df_feat = calculate_all_features_and_target(df)
    
    # Tách bản ghi mới nhất (Latest Candle - dùng để predict phiên tương lai)
    latest_candle = df_feat.iloc[[-1]].copy()
    
    # Dữ liệu huấn luyện: loại bỏ bản ghi cuối cùng (chưa có kết quả tương lai)
    df_trainable = df_feat.iloc[:-1].copy()
    
    # Loại bỏ các dòng có NaN ở đầu do cửa sổ trượt
    df_clean = df_trainable.dropna(subset=feature_cols + ['Target']).copy()
    
    X = df_clean[feature_cols].copy()
    y = df_clean['Target'].astype(int).copy()
    
    return df_feat, X, y, latest_candle


def chronological_train_test_split(X: pd.DataFrame, y: pd.Series, train_ratio: float = 0.70):
    """
    Chia tập Train / Test theo chuỗi thời gian (Bài 7 Bài giảng & Yêu cầu đề tài):
    - 70% đầu tiên theo thời gian -> TẬP HUẤN LUYỆN (TRAIN)
    - 30% sau cùng theo thời gian -> TẬP KIỂM THỬ (TEST)
    - Tuyệt đối KHÔNG SHUFFLE ngẫu nhiên.
    """
    n = len(X)
    split_idx = int(n * train_ratio)
    
    X_train = X.iloc[:split_idx].copy()
    X_test = X.iloc[split_idx:].copy()
    y_train = y.iloc[:split_idx].copy()
    y_test = y.iloc[split_idx:].copy()
    
    return X_train, X_test, y_train, y_test, split_idx


def scale_features_anti_leakage(X_train: pd.DataFrame, X_test: pd.DataFrame, X_latest: pd.DataFrame = None, method: str = 'standard'):
    """
    Chuẩn hóa đặc trưng CHỐNG DATA LEAKAGE:
    - Scaler CHỈ ĐƯỢC FIT trên X_train.
    - Dùng scaler đã fit để transform X_train, X_test và X_latest.
    """
    if method == 'minmax':
        scaler = MinMaxScaler()
    else:
        scaler = StandardScaler()
        
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    X_latest_scaled = None
    if X_latest is not None and len(X_latest) > 0:
        X_latest_scaled = scaler.transform(X_latest)
        
    return X_train_scaled, X_test_scaled, X_latest_scaled, scaler
