"""
app/indicators.py
Module tính toán các chỉ số kỹ thuật (Technical Indicators) và tạo biến mục tiêu (Target).
Bám sát lý thuyết Khai thác dữ liệu và Phân tích kỹ thuật tài chính.
Cam kết 100% KHÔNG DATA LEAKAGE (Không sử dụng dữ liệu tương lai để tính feature thời điểm hiện tại).
"""

import pandas as pd
import numpy as np


def compute_sma(series: pd.Series, period: int) -> pd.Series:
    """Đường trung bình động giản đơn (Simple Moving Average)."""
    return series.rolling(window=period).mean()


def compute_ema(series: pd.Series, period: int) -> pd.Series:
    """Đường trung bình động lũy thừa (Exponential Moving Average)."""
    return series.ewm(span=period, adjust=False).mean()


def compute_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """
    Chỉ số sức mạnh tương đối (Relative Strength Index - RSI).
    Công thức: RSI = 100 - (100 / (1 + RS))
    Trong đó RS = Average Gain / Average Loss qua period ngày.
    """
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).fillna(0)
    loss = (-delta.where(delta < 0, 0)).fillna(0)

    # Sử dụng phương pháp Wilder Smoothing (EWM alpha=1/period)
    avg_gain = gain.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, min_periods=period, adjust=False).mean()

    rs = avg_gain / (avg_loss + 1e-9)
    rsi = 100 - (100 / (1 + rs))
    return rsi


def compute_macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    """
    Chỉ báo Phân kỳ Hội tụ Trung bình Động (Moving Average Convergence Divergence - MACD).
    MACD Line = EMA(fast) - EMA(slow)
    Signal Line = EMA(MACD Line, signal)
    MACD Histogram = MACD Line - Signal Line
    """
    ema_fast = compute_ema(series, fast)
    ema_slow = compute_ema(series, slow)
    macd_line = ema_fast - ema_slow
    macd_signal = compute_ema(macd_line, signal)
    macd_hist = macd_line - macd_signal
    return macd_line, macd_signal, macd_hist


def compute_bollinger_bands(series: pd.Series, period: int = 20, num_std: float = 2.0):
    """
    Dải Bollinger Bands:
    Middle Band = SMA(period)
    Upper Band = Middle Band + num_std * StdDev(period)
    Lower Band = Middle Band - num_std * StdDev(period)
    Bandwidth = (Upper - Lower) / Middle
    """
    middle = compute_sma(series, period)
    std = series.rolling(window=period).std()
    upper = middle + (num_std * std)
    lower = middle - (num_std * std)
    bandwidth = (upper - lower) / (middle + 1e-9)
    return upper, middle, lower, bandwidth


def calculate_all_features_and_target(df: pd.DataFrame) -> pd.DataFrame:
    """
    Tạo toàn bộ các đặc trưng kỹ thuật và biến Target:
    1. Nhóm giá gốc: Open, High, Low, Close, Volume
    2. Moving Average: SMA 5, SMA 10, SMA 20, EMA 12, EMA 26
    3. Momentum: RSI 14, MACD, MACD Signal, MACD Hist
    4. Volatility: Bollinger Upper, Middle, Lower, Bandwidth
    5. Price Changes: Daily Return, Price Change %, Volume Change %
    6. Lag Features: Close_lag_1, Close_lag_2, Close_lag_3, Volume_lag_1
    7. Target: 1 nếu Close(t+1) > Close(t), ngược lại 0.
    
    LƯU Ý QUAN TRỌNG:
    - Close(t+1) chỉ được dùng để tạo Target(t).
    - Hàng cuối cùng (ngày mới nhất hiện tại) có Target = NaN vì chưa có phiên tiếp theo.
      Hàng này sẽ được giữ lại làm dữ liệu đầu vào cho phần DỰ ĐOÁN PHIÊN TIẾP THEO.
    """
    df = df.copy()
    
    # Đảm bảo sắp xếp đúng thứ tự thời gian
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date').reset_index(drop=True)
    df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
    
    close = df['Close'].astype(float)
    vol = df['Volume'].astype(float)
    
    # 1. Moving Averages
    df['SMA_5'] = compute_sma(close, 5)
    df['SMA_10'] = compute_sma(close, 10)
    df['SMA_20'] = compute_sma(close, 20)
    df['EMA_12'] = compute_ema(close, 12)
    df['EMA_26'] = compute_ema(close, 26)
    
    # 2. Momentum
    df['RSI_14'] = compute_rsi(close, 14)
    macd_line, macd_sig, macd_h = compute_macd(close, 12, 26, 9)
    df['MACD'] = macd_line
    df['MACD_Signal'] = macd_sig
    df['MACD_Hist'] = macd_h
    
    # 3. Volatility
    bb_upper, bb_mid, bb_lower, bb_width = compute_bollinger_bands(close, 20, 2.0)
    df['BB_Upper'] = bb_upper
    df['BB_Middle'] = bb_mid
    df['BB_Lower'] = bb_lower
    df['BB_Bandwidth'] = bb_width
    
    # 4. Price & Volume Changes (Tại thời điểm t)
    df['Daily_Return'] = close.pct_change()
    df['Price_Change_Pct'] = (close - df['Open']) / (df['Open'] + 1e-9) * 100.0
    df['Volume_Change_Pct'] = vol.pct_change() * 100.0
    
    # 5. Lag Features (Thông tin lịch sử t-1, t-2, t-3)
    df['Close_lag_1'] = close.shift(1)
    df['Close_lag_2'] = close.shift(2)
    df['Close_lag_3'] = close.shift(3)
    df['Volume_lag_1'] = vol.shift(1)
    
    # 6. Biến Mục Tiêu: Target = 1 nếu Close(t+1) > Close(t) else 0
    # Next_Close chỉ tồn tại trong bước tính nhãn tạm thời
    next_close = close.shift(-1)
    # Target: 1 (TĂNG), 0 (GIẢM)
    df['Target'] = np.where(next_close > close, 1, 0)
    # Hàng cuối cùng: chưa có next_close -> set Target là NaN
    df.loc[df.index[-1], 'Target'] = np.nan
    
    return df


# Danh sách các đặc trưng phục vụ huấn luyện (Feature Columns)
FEATURE_COLUMNS = [
    'Open', 'High', 'Low', 'Close', 'Volume',
    'SMA_5', 'SMA_10', 'SMA_20', 'EMA_12', 'EMA_26',
    'RSI_14', 'MACD', 'MACD_Signal', 'MACD_Hist',
    'BB_Upper', 'BB_Middle', 'BB_Lower', 'BB_Bandwidth',
    'Daily_Return', 'Price_Change_Pct', 'Volume_Change_Pct',
    'Close_lag_1', 'Close_lag_2', 'Close_lag_3', 'Volume_lag_1'
]
