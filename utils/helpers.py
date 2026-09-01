"""
utils/helpers.py
Các hàm tiện ích bổ trợ định dạng, logging, và xử lý dữ liệu.
"""

import os
import json
import logging
import pandas as pd
import numpy as np

# Thiết lập Logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger('StockDataMining')


def format_currency_vnd(val):
    """Định dạng tiền tệ VNĐ (ví dụ: 125,000 VNĐ)."""
    try:
        val = float(val)
        return f"{val:,.0f} đ"
    except Exception:
        return "N/A"


def format_number(val, decimals=2):
    """Định dạng số thập phân."""
    try:
        val = float(val)
        return f"{val:,.{decimals}f}"
    except Exception:
        return "N/A"


def format_percent(val, decimals=2):
    """Định dạng số phần trăm."""
    try:
        val = float(val)
        prefix = "+" if val > 0 else ""
        return f"{prefix}{val:.{decimals}f}%"
    except Exception:
        return "N/A"


class NpEncoder(json.JSONEncoder):
    """JSON Encoder hỗ trợ các kiểu dữ liệu của numpy & pandas."""
    def default(self, obj):
        if isinstance(obj, (np.integer, np.int64, np.int32, np.int16, np.int8)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64, np.float32, np.float16)):
            if np.isnan(obj) or np.isinf(obj):
                return None
            return float(obj)
        elif isinstance(obj, (np.ndarray,)):
            return obj.tolist()
        elif isinstance(obj, (pd.Timestamp, np.datetime64)):
            return str(obj)
        return super(NpEncoder, self).default(obj)
