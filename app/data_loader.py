"""
app/data_loader.py
Module thu thập và tải dữ liệu cổ phiếu HOSE từ nhiều nguồn:
1. API trực tuyến (TCBS / CafeF / VNDirect).
2. Tệp CSV cục bộ (data/raw/).
3. Tệp CSV do người dùng tải lên (data/uploaded/).
Đảm bảo hệ thống KHÔNG BAO GIỜ bị crash khi mất kết nối mạng.
"""

import os
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from utils.helpers import logger
from utils.mock_generator import generate_stock_history, HOSE_STOCKS_CONFIG
from config import Config


def get_available_symbols():
    """Lấy danh sách các mã cổ phiếu có sẵn trong hệ thống (cả mặc định và tải lên)."""
    symbols = list(Config.DEFAULT_SYMBOLS)
    
    # Quét thêm thư mục data/raw và data/uploaded
    for folder in [Config.RAW_DATA_DIR, Config.UPLOADED_DATA_DIR]:
        if os.path.exists(folder):
            for f in os.listdir(folder):
                if f.endswith('.csv'):
                    sym = f.replace('.csv', '').upper()
                    if sym not in symbols:
                        symbols.append(sym)
                        
    return sorted(symbols)


def fetch_from_tcbs_api(symbol: str, start_date: str = '2018-01-01', end_date: str = None) -> pd.DataFrame:
    """
    Lấy dữ liệu lịch sử giá từ API công khai của TCBS.
    """
    if end_date is None:
        end_date = datetime.now().strftime('%Y-%m-%d')
        
    start_ts = int(datetime.strptime(start_date, '%Y-%m-%d').timestamp())
    end_ts = int(datetime.strptime(end_date, '%Y-%m-%d').timestamp())
    
    url = f"https://apipubaws.tcbs.com.vn/stock-insight/v1/stock/bars-long-term?ticker={symbol}&type=stock&resolution=D&from={start_ts}&to={end_ts}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json'
    }
    
    resp = requests.get(url, headers=headers, timeout=4)
    if resp.status_code == 200:
        data = resp.json()
        if 'data' in data and len(data['data']) > 0:
            df = pd.DataFrame(data['data'])
            # Chuẩn hóa tên cột TCBS: tradingDate, open, high, low, close, volume
            rename_map = {
                'tradingDate': 'Date',
                'open': 'Open',
                'high': 'High',
                'low': 'Low',
                'close': 'Close',
                'volume': 'Volume'
            }
            df = df.rename(columns=rename_map)
            df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')
            df['Symbol'] = symbol
            df = df[['Date', 'Symbol', 'Open', 'High', 'Low', 'Close', 'Volume']]
            return df
            
    raise Exception(f"Không thể lấy dữ liệu API TCBS cho mã {symbol} (HTTP {resp.status_code})")


def load_stock_data(symbol: str, start_date: str = '2018-01-01', end_date: str = None, use_online_if_possible: bool = True) -> (pd.DataFrame, str):
    """
    Tải dữ liệu cổ phiếu theo thứ tự ưu tiên:
    1. Trực tuyến (nếu bật use_online_if_possible)
    2. File đã tải lên (data/uploaded/<symbol>.csv)
    3. File cục bộ có sẵn (data/raw/<symbol>.csv)
    4. Tự động sinh dữ liệu thực tế mẫu nếu chưa có file.
    
    Trả về: (DataFrame, source_description)
    """
    symbol = symbol.strip().upper()
    source_msg = "Offline Local Dataset"
    
    # 1. Thử lấy Online trước nếu được yêu cầu
    if use_online_if_possible:
        try:
            logger.info(f"Đang thử tải dữ liệu online cho mã {symbol}...")
            df = fetch_from_tcbs_api(symbol, start_date, end_date)
            if df is not None and len(df) > 30:
                logger.info(f"Tải thành công {len(df)} dòng dữ liệu trực tuyến cho mã {symbol}.")
                # Lưu cache vào raw
                cache_path = os.path.join(Config.RAW_DATA_DIR, f"{symbol}.csv")
                df.to_csv(cache_path, index=False)
                return df, "Dữ liệu trực tuyến (TCBS API)"
        except Exception as e:
            logger.warning(f"Không lấy được online ({str(e)}), chuyển sang fallback offline.")
            
    # 2. Kiểm tra file upload
    upload_path = os.path.join(Config.UPLOADED_DATA_DIR, f"{symbol}.csv")
    if os.path.exists(upload_path):
        df = pd.read_csv(upload_path)
        logger.info(f"Đã nạp {len(df)} dòng từ file upload: {upload_path}")
        return df, "Dữ liệu người dùng tải lên (CSV Upload)"
        
    # 3. Kiểm tra file trong data/raw
    raw_path = os.path.join(Config.RAW_DATA_DIR, f"{symbol}.csv")
    if os.path.exists(raw_path):
        df = pd.read_csv(raw_path)
        logger.info(f"Đã nạp {len(df)} dòng từ kho dữ liệu chuẩn: {raw_path}")
        return df, "Kho dữ liệu lịch sử HOSE chuẩn (Offline CSV)"
        
    # 4. Tự sinh dữ liệu nếu chưa có
    logger.info(f"Chưa có dữ liệu cho mã {symbol}, tiến hành sinh dữ liệu mẫu chuẩn...")
    df = generate_stock_history(symbol, start_date=start_date, end_date=end_date or '2026-08-31')
    os.makedirs(Config.RAW_DATA_DIR, exist_ok=True)
    df.to_csv(raw_path, index=False)
    return df, "Dữ liệu mô phỏng thị trường HOSE (Offline Auto-Generated)"


def normalize_and_save_uploaded_csv(file_storage, custom_symbol: str = None) -> (str, str, int):
    """
    Chuẩn hóa và lưu file CSV do người dùng tải lên.
    Hỗ trợ cả tên cột tiếng Anh (Date, Open, High, Low, Close, Volume) và tiếng Việt (Ngay, MoCua, CaoNhat, ThapNhat, DongCua, KhoiLuong).
    """
    os.makedirs(Config.UPLOADED_DATA_DIR, exist_ok=True)
    df = pd.read_csv(file_storage)
    
    # Chuẩn hóa tên cột
    col_mapping = {}
    for col in df.columns:
        c_clean = col.strip().lower().replace('_', '').replace(' ', '')
        if c_clean in ['date', 'ngay', 'time', 'tradingdate']:
            col_mapping[col] = 'Date'
        elif c_clean in ['open', 'mocua', 'giastart', 'giamo']:
            col_mapping[col] = 'Open'
        elif c_clean in ['high', 'caonhat', 'giacao', 'max']:
            col_mapping[col] = 'High'
        elif c_clean in ['low', 'thapnhat', 'giathap', 'min']:
            col_mapping[col] = 'Low'
        elif c_clean in ['close', 'dongcua', 'giadong', 'last', 'gia']:
            col_mapping[col] = 'Close'
        elif c_clean in ['volume', 'khoiluong', 'vol', 'klgd', 'khoiluonggd']:
            col_mapping[col] = 'Volume'
        elif c_clean in ['symbol', 'ticker', 'macp', 'ma']:
            col_mapping[col] = 'Symbol'
            
    df = df.rename(columns=col_mapping)
    
    # Kiểm tra các cột bắt buộc
    required = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"File CSV thiếu các cột bắt buộc: {', '.join(missing)}. Các cột cần có: Date, Open, High, Low, Close, Volume.")
        
    # Xác định mã Symbol
    if custom_symbol:
        sym = custom_symbol.strip().upper()
    elif 'Symbol' in df.columns:
        sym = str(df['Symbol'].dropna().iloc[0]).strip().upper()
    else:
        # Lấy từ tên file gốc
        orig_name = file_storage.filename.split('.')[0].upper()
        sym = orig_name if orig_name else "CUSTOM"
        
    df['Symbol'] = sym
    
    # Chuẩn hóa kiểu dữ liệu
    df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')
    for c in ['Open', 'High', 'Low', 'Close']:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    df['Volume'] = pd.to_numeric(df['Volume'], errors='coerce')
    
    # Sắp xếp theo ngày
    df = df.sort_values('Date').reset_index(drop=True)
    
    # Lưu file
    save_path = os.path.join(Config.UPLOADED_DATA_DIR, f"{sym}.csv")
    df.to_csv(save_path, index=False)
    
    return sym, save_path, len(df)
