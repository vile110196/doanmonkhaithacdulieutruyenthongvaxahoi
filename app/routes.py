"""
app/routes.py
Định nghĩa toàn bộ các Web Routes và REST API Endpoints cho ứng dụng Web Dashboard.
"""

import os
import json
import pandas as pd
import numpy as np
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, current_app

from config import Config
from app.data_loader import (
    load_stock_data, get_available_symbols, normalize_and_save_uploaded_csv
)
from app.preprocessing import (
    clean_raw_data, prepare_dataset_for_modeling, chronological_train_test_split, scale_features_anti_leakage
)
from app.indicators import (
    calculate_all_features_and_target, FEATURE_COLUMNS
)
from app.models import (
    AVAILABLE_MODELS, create_model_instance, train_single_model, 
    save_model_bundle, load_model_bundle, get_model_explanation_details
)
from app.evaluation import (
    evaluate_classification_model, compare_all_models_performance
)
from app.prediction import (
    predict_next_trading_day, predict_custom_scenario, ensure_model_is_trained, DISCLAIMER_TEXT
)
from app.clustering import (
    perform_hose_stocks_clustering
)
from app.reduct_selection import (
    compute_rough_set_reduct, compute_feature_selection_comparison
)
from app.sentiment import (
    analyze_social_sentiment_for_stock
)
from utils.helpers import logger, NpEncoder, format_currency_vnd, format_percent


main_bp = Blueprint('main', __name__)


# -------------------------------------------------------------
# 1. TRANG DASHBOARD (TỔNG QUAN)
# -------------------------------------------------------------
@main_bp.route('/')
def dashboard():
    symbol = request.args.get('symbol', 'FPT').upper()
    model_type = request.args.get('model', 'random_forest').lower()
    
    symbols = get_available_symbols()
    if symbol not in symbols:
        symbols.insert(0, symbol)
        
    try:
        pred_data = predict_next_trading_day(symbol, model_type)
    except Exception as e:
        logger.error(f"Lỗi dự đoán trên Dashboard: {e}")
        pred_data = None
        
    return render_template(
        'dashboard.html',
        active_page='dashboard',
        symbols=symbols,
        current_symbol=symbol,
        current_model=model_type,
        models_list=AVAILABLE_MODELS,
        prediction=pred_data,
        disclaimer=DISCLAIMER_TEXT
    )


# -------------------------------------------------------------
# 2. TRANG DỮ LIỆU LỊCH SỬ (HISTORICAL DATA)
# -------------------------------------------------------------
@main_bp.route('/historical')
def historical():
    symbol = request.args.get('symbol', 'FPT').upper()
    symbols = get_available_symbols()
    
    df_raw, source_desc = load_stock_data(symbol, use_online_if_possible=False)
    df_clean, stats = clean_raw_data(df_raw)
    
    # Lấy 100 dòng gần nhất để hiển thị bảng dữ liệu
    table_data = df_clean.tail(100).to_dict(orient='records')
    table_data.reverse()
    
    return render_template(
        'historical.html',
        active_page='historical',
        symbols=symbols,
        current_symbol=symbol,
        data_source=source_desc,
        stats=stats,
        table_data=table_data,
        total_rows=len(df_clean)
    )


# -------------------------------------------------------------
# 3. TRANG CHỈ SỐ KỸ THUẬT (TECHNICAL INDICATORS)
# -------------------------------------------------------------
@main_bp.route('/indicators')
def indicators():
    symbol = request.args.get('symbol', 'FPT').upper()
    symbols = get_available_symbols()
    
    df_raw, _ = load_stock_data(symbol, use_online_if_possible=False)
    df_clean, _ = clean_raw_data(df_raw)
    df_feat = calculate_all_features_and_target(df_clean)
    
    latest_row = df_feat.iloc[-1].to_dict()
    
    return render_template(
        'indicators.html',
        active_page='indicators',
        symbols=symbols,
        current_symbol=symbol,
        latest_indicators=latest_row
    )


# -------------------------------------------------------------
# 4. TRANG RÚT GỌN ĐẶC TRƯNG & TẬP THÔ (REDUCT & SELECTION)
# -------------------------------------------------------------
@main_bp.route('/reduct')
def reduct():
    symbol = request.args.get('symbol', 'FPT').upper()
    symbols = get_available_symbols()
    
    df_raw, _ = load_stock_data(symbol, use_online_if_possible=False)
    df_clean, _ = clean_raw_data(df_raw)
    df_feat, X, y, _ = prepare_dataset_for_modeling(df_clean)
    
    # Tính toán Reduct và Lựa chọn đặc trưng
    rough_results = compute_rough_set_reduct(X, y)
    selection_results = compute_feature_selection_comparison(X, y, top_k=10)
    
    return render_template(
        'reduct.html',
        active_page='reduct',
        symbols=symbols,
        current_symbol=symbol,
        rough=rough_results,
        selection=selection_results
    )


# -------------------------------------------------------------
# 5. TRANG HUẤN LUYỆN MÔ HÌNH (MODEL TRAINING)
# -------------------------------------------------------------
@main_bp.route('/training')
def training():
    symbol = request.args.get('symbol', 'FPT').upper()
    symbols = get_available_symbols()
    
    return render_template(
        'training.html',
        active_page='training',
        symbols=symbols,
        current_symbol=symbol,
        models_list=AVAILABLE_MODELS
    )


# -------------------------------------------------------------
# 6. TRANG SO SÁNH THUẬT TOÁN (MODEL COMPARISON)
# -------------------------------------------------------------
@main_bp.route('/comparison')
def comparison():
    symbol = request.args.get('symbol', 'FPT').upper()
    symbols = get_available_symbols()
    
    # Đảm bảo cả 4 mô hình đều đã được huấn luyện
    models_dict = {}
    for m_key in AVAILABLE_MODELS.keys():
        bundle = ensure_model_is_trained(symbol, m_key)
        models_dict[m_key] = bundle
        
    df_raw, _ = load_stock_data(symbol, use_online_if_possible=False)
    df_clean, _ = clean_raw_data(df_raw)
    df_feat, X, y, _ = prepare_dataset_for_modeling(df_clean)
    
    X_train, X_test, y_train, y_test, split_idx = chronological_train_test_split(X, y, train_ratio=0.70)
    _, X_test_scaled, _, _ = scale_features_anti_leakage(X_train, X_test)
    
    comparison_data = compare_all_models_performance(models_dict, X_test_scaled, y_test)
    
    return render_template(
        'comparison.html',
        active_page='comparison',
        symbols=symbols,
        current_symbol=symbol,
        comparison=comparison_data,
        models_dict=models_dict,
        train_samples=len(X_train),
        test_samples=len(X_test)
    )


# -------------------------------------------------------------
# 7. TRANG DỰ ĐOÁN & MÔ PHỎNG WHAT-IF (PREDICTION)
# -------------------------------------------------------------
@main_bp.route('/prediction')
def prediction():
    symbol = request.args.get('symbol', 'FPT').upper()
    model_type = request.args.get('model', 'random_forest').lower()
    symbols = get_available_symbols()
    
    pred_data = predict_next_trading_day(symbol, model_type)
    
    # Giải thích chi tiết mô hình
    bundle = load_model_bundle(symbol, model_type)
    model_explanation = get_model_explanation_details(
        bundle['model'], model_type, bundle.get('feature_columns', FEATURE_COLUMNS)
    )
    
    return render_template(
        'prediction.html',
        active_page='prediction',
        symbols=symbols,
        current_symbol=symbol,
        current_model=model_type,
        models_list=AVAILABLE_MODELS,
        prediction=pred_data,
        model_explanation=model_explanation,
        disclaimer=DISCLAIMER_TEXT
    )


# -------------------------------------------------------------
# 8. TRANG GOM CỤM K-MEANS (CLUSTERING)
# -------------------------------------------------------------
@main_bp.route('/clustering')
def clustering():
    n_clusters = int(request.args.get('k', 3))
    clustering_results = perform_hose_stocks_clustering(n_clusters)
    
    return render_template(
        'clustering.html',
        active_page='clustering',
        results=clustering_results,
        current_k=n_clusters
    )


# -------------------------------------------------------------
# 9. TRANG TRUYỀN THÔNG XÃ HỘI (SOCIAL SENTIMENT)
# -------------------------------------------------------------
@main_bp.route('/sentiment')
def sentiment():
    symbol = request.args.get('symbol', 'FPT').upper()
    symbols = get_available_symbols()
    
    sentiment_data = analyze_social_sentiment_for_stock(symbol)
    
    return render_template(
        'sentiment.html',
        active_page='sentiment',
        symbols=symbols,
        current_symbol=symbol,
        sentiment=sentiment_data
    )


# -------------------------------------------------------------
# 10. TRANG HƯỚNG DẪN LÝ THUYẾT & BẢO VỆ ĐỒ ÁN (THEORY GUIDE)
# -------------------------------------------------------------
@main_bp.route('/theory')
def theory():
    return render_template(
        'theory_guide.html',
        active_page='theory'
    )


# =============================================================
# REST API ENDPOINTS (CHO AJAX & DYNAMIC CHARTS)
# =============================================================

@main_bp.route('/api/train', methods=['POST'])
def api_train_model():
    """API Huấn luyện mô hình phân lớp."""
    data = request.get_json() or {}
    symbol = data.get('symbol', 'FPT').upper()
    model_type = data.get('model_type', 'random_forest').lower()
    train_ratio = float(data.get('train_ratio', 0.70))
    params = data.get('params', {})
    
    try:
        df_raw, _ = load_stock_data(symbol, use_online_if_possible=False)
        df_clean, stats = clean_raw_data(df_raw)
        df_feat, X, y, latest_candle = prepare_dataset_for_modeling(df_clean)
        
        X_train, X_test, y_train, y_test, split_idx = chronological_train_test_split(X, y, train_ratio=train_ratio)
        X_train_scaled, X_test_scaled, _, scaler = scale_features_anti_leakage(X_train, X_test)
        
        # Huấn luyện
        model = train_single_model(model_type, X_train_scaled, y_train, params)
        metrics = evaluate_classification_model(model, X_test_scaled, y_test)
        
        # Lưu mô hình
        save_path = save_model_bundle(symbol, model_type, model, scaler, FEATURE_COLUMNS, metrics)
        
        # Trích xuất giải thích mô hình
        explanation = get_model_explanation_details(model, model_type, FEATURE_COLUMNS)
        
        return json.dumps({
            'status': 'success',
            'symbol': symbol,
            'model_type': model_type,
            'model_name': AVAILABLE_MODELS.get(model_type, {}).get('name', model_type),
            'metrics': metrics,
            'explanation': explanation,
            'split_info': {
                'total_samples': len(X),
                'train_samples': len(X_train),
                'test_samples': len(X_test),
                'train_ratio': train_ratio,
                'train_period': f"{df_clean['Date'].iloc[0]} -> {df_clean['Date'].iloc[split_idx-1]}",
                'test_period': f"{df_clean['Date'].iloc[split_idx]} -> {df_clean['Date'].iloc[-2]}"
            }
        }, cls=NpEncoder), 200, {'Content-Type': 'application/json'}
        
    except Exception as e:
        logger.error(f"Lỗi trong api_train_model: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 400


@main_bp.route('/api/simulate', methods=['POST'])
def api_simulate_prediction():
    """API Mô phỏng What-If kịch bản tùy biến."""
    data = request.get_json() or {}
    symbol = data.get('symbol', 'FPT').upper()
    model_type = data.get('model_type', 'random_forest').lower()
    custom_params = data.get('custom_params', {})
    
    try:
        res = predict_custom_scenario(symbol, model_type, custom_params)
        return json.dumps({'status': 'success', 'data': res}, cls=NpEncoder), 200, {'Content-Type': 'application/json'}
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


@main_bp.route('/api/upload_csv', methods=['POST'])
def api_upload_csv():
    """API Tiếp nhận file CSV cổ phiếu người dùng tải lên."""
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': 'Không tìm thấy file tải lên.'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'Chưa chọn file CSV.'}), 400
        
    custom_symbol = request.form.get('symbol', '').strip().upper()
    
    try:
        sym, path, count = normalize_and_save_uploaded_csv(file, custom_symbol if custom_symbol else None)
        flash(f"Tải lên thành công mã {sym} với {count} dòng dữ liệu!", "success")
        return redirect(url_for('main.historical', symbol=sym))
    except Exception as e:
        logger.error(f"Lỗi upload CSV: {e}")
        flash(f"Lỗi khi xử lý file CSV: {str(e)}", "danger")
        return redirect(url_for('main.historical'))


@main_bp.route('/api/upload_social_csv', methods=['POST'])
def api_upload_social_csv():
    """API Tiếp nhận file CSV bình luận truyền thông xã hội."""
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': 'Không tìm thấy file tải lên.'}), 400
        
    file = request.files['file']
    symbol = request.form.get('symbol', 'FPT').strip().upper()
    
    try:
        os.makedirs(Config.SOCIAL_DATA_DIR, exist_ok=True)
        save_path = os.path.join(Config.SOCIAL_DATA_DIR, f"{symbol}_social_sentiment.csv")
        file.save(save_path)
        flash(f"Tải lên thành công dữ liệu bình luận cho mã {symbol}!", "success")
        return redirect(url_for('main.sentiment', symbol=symbol))
    except Exception as e:
        flash(f"Lỗi khi lưu file bình luận: {str(e)}", "danger")
        return redirect(url_for('main.sentiment', symbol=symbol))


@main_bp.route('/api/chart/historical/<symbol>')
def api_chart_historical(symbol):
    """API Cung cấp dữ liệu vẽ biểu đồ nến OHLCV & Volume cho Plotly."""
    symbol = symbol.upper()
    df_raw, _ = load_stock_data(symbol, use_online_if_possible=False)
    df_clean, _ = clean_raw_data(df_raw)
    
    # Giới hạn 300 phiên gần nhất cho mượt mà
    df_view = df_clean.tail(300)
    
    chart_data = {
        'dates': df_view['Date'].tolist(),
        'open': df_view['Open'].tolist(),
        'high': df_view['High'].tolist(),
        'low': df_view['Low'].tolist(),
        'close': df_view['Close'].tolist(),
        'volume': df_view['Volume'].tolist(),
    }
    return json.dumps(chart_data, cls=NpEncoder), 200, {'Content-Type': 'application/json'}


@main_bp.route('/api/chart/indicators/<symbol>')
def api_chart_indicators(symbol):
    """API Cung cấp dữ liệu đầy đủ các đường chỉ báo kỹ thuật cho Plotly."""
    symbol = symbol.upper()
    df_raw, _ = load_stock_data(symbol, use_online_if_possible=False)
    df_clean, _ = clean_raw_data(df_raw)
    df_feat = calculate_all_features_and_target(df_clean)
    
    df_view = df_feat.tail(250)
    
    chart_data = {
        'dates': df_view['Date'].tolist(),
        'close': df_view['Close'].tolist(),
        'sma_5': df_view['SMA_5'].tolist(),
        'sma_10': df_view['SMA_10'].tolist(),
        'sma_20': df_view['SMA_20'].tolist(),
        'ema_12': df_view['EMA_12'].tolist(),
        'ema_26': df_view['EMA_26'].tolist(),
        'bb_upper': df_view['BB_Upper'].tolist(),
        'bb_middle': df_view['BB_Middle'].tolist(),
        'bb_lower': df_view['BB_Lower'].tolist(),
        'rsi_14': df_view['RSI_14'].tolist(),
        'macd': df_view['MACD'].tolist(),
        'macd_signal': df_view['MACD_Signal'].tolist(),
        'macd_hist': df_view['MACD_Hist'].tolist(),
    }
    return json.dumps(chart_data, cls=NpEncoder), 200, {'Content-Type': 'application/json'}
