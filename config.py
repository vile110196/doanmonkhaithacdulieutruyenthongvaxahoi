"""
config.py
Cấu hình hệ thống Ứng dụng Dự đoán Xu hướng Cổ phiếu HOSE.
Hỗ trợ cả môi trường phát triển và môi trường đóng gói PyInstaller EXE.
"""

import os
import sys

# Xử lý đường dẫn thư mục gốc khi chạy dưới dạng file .py hoặc file .exe đóng gói
if getattr(sys, 'frozen', False):
    # Khi chạy từ file EXE (PyInstaller)
    BASE_DIR = os.path.dirname(sys.executable)
    BUNDLE_DIR = sys._MEIPASS
else:
    # Khi chạy từ mã nguồn Python thông thường
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    BUNDLE_DIR = BASE_DIR


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hose-stock-data-mining-secret-2026'
    
    # Thư mục dữ liệu (Lưu trên thư mục ứng dụng để người dùng có thể đọc/ghi CSV)
    RAW_DATA_DIR = os.path.join(BASE_DIR, 'data', 'raw')
    PROCESSED_DATA_DIR = os.path.join(BASE_DIR, 'data', 'processed')
    UPLOADED_DATA_DIR = os.path.join(BASE_DIR, 'data', 'uploaded')
    SOCIAL_DATA_DIR = os.path.join(BASE_DIR, 'data', 'sample_social')
    MODELS_DIR = os.path.join(BASE_DIR, 'models')
    
    # Danh sách mã cổ phiếu HOSE mặc định
    DEFAULT_SYMBOLS = [
        'FPT', 'VCB', 'VNM', 'HPG', 'MWG', 
        'VIC', 'SSI', 'VHM', 'TCB', 'MBB', 
        'STB', 'CTG'
    ]
    
    # Cấu hình Train / Test mặc định (Chia chuỗi thời gian)
    DEFAULT_TRAIN_RATIO = 0.70
    
    # Giới hạn file upload (10 MB)
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}
