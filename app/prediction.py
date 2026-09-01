"""
app/prediction.py
Module thực thi dự đoán xu hướng phiên giao dịch tiếp theo:
1. Dự đoán phiên tiếp theo theo dữ liệu thực tế mới nhất của mã cổ phiếu.
2. Mô phỏng kịch bản tùy biến (What-If Interactive Simulation Playground).
3. Đảm bảo tuân thủ nguyên tắc học thuật: Dự đoán xu hướng nhị phân TĂNG/GIẢM, kèm xác suất và cảnh báo rủi ro.
"""

import numpy as np
import pandas as pd
from app.data_loader import load_stock_data
from app.indicators import calculate_all_features_and_target, FEATURE_COLUMNS
from app.preprocessing import clean_raw_data, prepare_dataset_for_modeling, chronological_train_test_split, scale_features_anti_leakage
from app.models import train_single_model, save_model_bundle, load_model_bundle, AVAILABLE_MODELS
from app.evaluation import evaluate_classification_model
from utils.helpers import logger, format_currency_vnd, format_percent


DISCLAIMER_TEXT = "Kết quả chỉ mang mục đích học tập và minh họa mô hình khai thác dữ liệu, không phải khuyến nghị đầu tư."


def ensure_model_is_trained(symbol: str, model_type: str = 'random_forest'):
    """
    Đảm bảo mô hình cho mã chỉ định đã được huấn luyện và lưu trữ.
    Nếu chưa có, tự động nạp dữ liệu, huấn luyện và lưu lại.
    """
    symbol = symbol.upper()
    model_type = model_type.lower()
    
    bundle = load_model_bundle(symbol, model_type)
    if bundle is not None:
        return bundle
        
    logger.info(f"Mô hình {model_type} cho mã {symbol} chưa tồn tại. Đang tự động huấn luyện...")
    df_raw, _ = load_stock_data(symbol, use_online_if_possible=False)
    df_clean, _ = clean_raw_data(df_raw)
    df_feat, X, y, latest_candle = prepare_dataset_for_modeling(df_clean)
    
    X_train, X_test, y_train, y_test, _ = chronological_train_test_split(X, y, train_ratio=0.70)
    X_train_scaled, X_test_scaled, _, scaler = scale_features_anti_leakage(X_train, X_test)
    
    model = train_single_model(model_type, X_train_scaled, y_train)
    metrics = evaluate_classification_model(model, X_test_scaled, y_test)
    
    save_model_bundle(symbol, model_type, model, scaler, FEATURE_COLUMNS, metrics)
    return load_model_bundle(symbol, model_type)


def predict_next_trading_day(symbol: str, model_type: str = 'random_forest') -> dict:
    """
    Dự đoán xu hướng phiên giao dịch tiếp theo cho mã cổ phiếu:
    - Nạp bản ghi thị trường mới nhất.
    - Tính toán toàn bộ đặc trưng kỹ thuật.
    - Scale bằng scaler đã fit trên tập Train.
    - Dự đoán: TĂNG / GIẢM kèm xác suất (%).
    """
    symbol = symbol.upper()
    model_type = model_type.lower()
    
    # 1. Đảm bảo mô hình đã sẵn sàng
    bundle = ensure_model_is_trained(symbol, model_type)
    model = bundle['model']
    scaler = bundle['scaler']
    feature_cols = bundle.get('feature_columns', FEATURE_COLUMNS)
    metrics = bundle.get('metrics', {})
    
    # 2. Lấy dữ liệu nến mới nhất
    df_raw, data_source = load_stock_data(symbol, use_online_if_possible=False)
    df_clean, _ = clean_raw_data(df_raw)
    df_feat, X, y, latest_candle = prepare_dataset_for_modeling(df_clean, feature_cols)
    
    if latest_candle is None or len(latest_candle) == 0:
        raise ValueError(f"Không thể trích xuất nến mới nhất cho mã {symbol}.")
        
    latest_features = latest_candle[feature_cols].copy()
    latest_features_scaled = scaler.transform(latest_features)
    
    # 3. Thực hiện dự đoán
    pred_label = int(model.predict(latest_features_scaled)[0])
    
    if hasattr(model, 'predict_proba'):
        probabilities = model.predict_proba(latest_features_scaled)[0]
        prob_down = round(float(probabilities[0]) * 100.0, 2)
        prob_up = round(float(probabilities[1]) * 100.0, 2)
    elif hasattr(model, 'decision_function'):
        score = model.decision_function(latest_features_scaled)[0]
        prob_up = round(float(1 / (1 + np.exp(-score))) * 100.0, 2)
        prob_down = round(100.0 - prob_up, 2)
    else:
        prob_up = 100.0 if pred_label == 1 else 0.0
        prob_down = 100.0 - prob_up
        
    # Thông tin phiên mới nhất
    latest_row = latest_candle.iloc[0]
    latest_date = str(latest_row['Date'])
    latest_close = float(latest_row['Close'])
    latest_open = float(latest_row['Open'])
    latest_high = float(latest_row['High'])
    latest_low = float(latest_row['Low'])
    latest_volume = float(latest_row['Volume'])
    
    # Các chỉ số kỹ thuật chính hiện tại
    current_rsi = round(float(latest_row.get('RSI_14', 50)), 2)
    current_macd = round(float(latest_row.get('MACD', 0)), 2)
    current_macd_signal = round(float(latest_row.get('MACD_Signal', 0)), 2)
    current_sma20 = round(float(latest_row.get('SMA_20', latest_close)), 0)
    current_return = round(float(latest_row.get('Daily_Return', 0)) * 100.0, 2)
    
    result_text = "TĂNG ↑" if pred_label == 1 else "GIẢM ↓"
    result_color = "success" if pred_label == 1 else "danger"
    result_icon = "bi-arrow-up-circle-fill" if pred_label == 1 else "bi-arrow-down-circle-fill"
    
    return {
        'symbol': symbol,
        'model_type': model_type,
        'model_name': AVAILABLE_MODELS.get(model_type, {}).get('name', model_type),
        'prediction_label': pred_label, # 1: TĂNG, 0: GIẢM
        'prediction_text': result_text,
        'prediction_color': result_color,
        'prediction_icon': result_icon,
        'prob_up': prob_up,
        'prob_down': prob_down,
        'confidence': max(prob_up, prob_down),
        'test_accuracy': metrics.get('accuracy', 'N/A'),
        'test_f1': metrics.get('f1_score', 'N/A'),
        'test_precision': metrics.get('precision', 'N/A'),
        'test_recall': metrics.get('recall', 'N/A'),
        'latest_candle': {
            'date': latest_date,
            'close': latest_close,
            'close_formatted': format_currency_vnd(latest_close),
            'open': latest_open,
            'high': latest_high,
            'low': latest_low,
            'volume': latest_volume,
            'volume_formatted': f"{latest_volume:,.0f}",
            'price_change_pct': format_percent(current_return),
        },
        'key_indicators': {
            'rsi_14': current_rsi,
            'rsi_status': 'Quá mua (>70)' if current_rsi > 70 else ('Quá bán (<30)' if current_rsi < 30 else 'Trung tính'),
            'macd': current_macd,
            'macd_signal': current_macd_signal,
            'macd_status': 'Cắt lên Signal (Mua)' if current_macd > current_macd_signal else 'Cắt xuống Signal (Bán)',
            'sma_20': format_currency_vnd(current_sma20),
            'trend_vs_sma20': 'Trên MA20 (Xu hướng tăng)' if latest_close >= current_sma20 else 'Dưới MA20 (Xu hướng giảm)'
        },
        'data_source': data_source,
        'disclaimer': DISCLAIMER_TEXT
    }


def predict_custom_scenario(symbol: str, model_type: str, custom_params: dict) -> dict:
    """
    Mô phỏng kịch bản giả định (What-If Simulation Playground):
    Người dùng điều chỉnh thanh trượt RSI, MACD, Return, Price để kiểm tra phản ứng của mô hình.
    """
    symbol = symbol.upper()
    model_type = model_type.lower()
    bundle = ensure_model_is_trained(symbol, model_type)
    
    model = bundle['model']
    scaler = bundle['scaler']
    feature_cols = bundle.get('feature_columns', FEATURE_COLUMNS)
    
    # Nạp bản ghi cơ sở gần nhất
    df_raw, _ = load_stock_data(symbol, use_online_if_possible=False)
    df_feat, X, y, latest_candle = prepare_dataset_for_modeling(df_raw, feature_cols)
    
    sim_row = latest_candle[feature_cols].copy()
    
    # Ghi đè các tham số tùy chỉnh nếu người dùng cung cấp
    if 'rsi' in custom_params:
        sim_row['RSI_14'] = float(custom_params['rsi'])
    if 'macd' in custom_params:
        sim_row['MACD'] = float(custom_params['macd'])
    if 'daily_return' in custom_params:
        sim_row['Daily_Return'] = float(custom_params['daily_return']) / 100.0
    if 'price_change_pct' in custom_params:
        sim_row['Price_Change_Pct'] = float(custom_params['price_change_pct'])
        
    sim_scaled = scaler.transform(sim_row)
    pred_label = int(model.predict(sim_scaled)[0])
    
    if hasattr(model, 'predict_proba'):
        probs = model.predict_proba(sim_scaled)[0]
        prob_down = round(float(probs[0]) * 100.0, 2)
        prob_up = round(float(probs[1]) * 100.0, 2)
    else:
        prob_up = 100.0 if pred_label == 1 else 0.0
        prob_down = 100.0 - prob_up
        
    return {
        'symbol': symbol,
        'model_name': AVAILABLE_MODELS.get(model_type, {}).get('name', model_type),
        'prediction_text': "TĂNG ↑" if pred_label == 1 else "GIẢM ↓",
        'prediction_color': "success" if pred_label == 1 else "danger",
        'prob_up': prob_up,
        'prob_down': prob_down,
        'simulated_inputs': custom_params
    }
