"""
config.py
Cấu hình hệ thống Ứng dụng Dự đoán Xu hướng Cổ phiếu HOSE.
"""

import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hose-stock-data-mining-secret-2026'
    
    # Thư mục dữ liệu
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
