"""
utils/test_system.py
Script kiểm thử tự động toàn diện toàn bộ các module và API endpoints của hệ thống.
"""

import sys
import os

# Cấu hình UTF-8 cho Windows Console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Đảm bảo đường dẫn root có trong sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.data_loader import load_stock_data, get_available_symbols
from app.preprocessing import clean_raw_data, prepare_dataset_for_modeling, chronological_train_test_split, scale_features_anti_leakage
from app.indicators import calculate_all_features_and_target, FEATURE_COLUMNS
from app.reduct_selection import compute_rough_set_reduct, compute_feature_selection_comparison
from app.models import AVAILABLE_MODELS, train_single_model, save_model_bundle, load_model_bundle, get_model_explanation_details
from app.evaluation import evaluate_classification_model, compare_all_models_performance
from app.prediction import predict_next_trading_day, predict_custom_scenario
from app.clustering import perform_hose_stocks_clustering
from app.sentiment import analyze_social_sentiment_for_stock
from app import create_app


def run_all_tests():
    print("\n=======================================================")
    print(" BẮT ĐẦU KIỂM THỬ TOÀN DIỆN HỆ THỐNG DATA MINING HOSE")
    print("=======================================================\n")
    
    # 1. Kiểm tra Data Loader
    print("[1/8] Kiểm tra Data Loader...")
    symbols = get_available_symbols()
    assert len(symbols) >= 10, f"Số lượng mã cổ phiếu quá ít: {len(symbols)}"
    df_raw, src = load_stock_data('FPT', use_online_if_possible=False)
    assert len(df_raw) > 500, f"Dữ liệu FPT quá ngắn: {len(df_raw)}"
    print(f" -> Tải thành công mã FPT ({len(df_raw)} dòng) từ nguồn: {src}")

    # 2. Kiểm tra Preprocessing & Indicators
    print("\n[2/8] Kiểm tra Preprocessing & Indicators (Chống Data Leakage)...")
    df_clean, stats = clean_raw_data(df_raw)
    df_feat, X, y, latest_candle = prepare_dataset_for_modeling(df_clean)
    assert len(X) == len(y), "X và y không khớp số lượng dòng!"
    assert len(latest_candle) == 1, "Nến mới nhất không đúng kích thước 1 dòng!"
    assert not X.isna().any().any(), "Ma trận X còn chứa giá trị NaN!"
    
    X_train, X_test, y_train, y_test, split_idx = chronological_train_test_split(X, y, train_ratio=0.70)
    assert len(X_train) + len(X_test) == len(X), "Tổng số mẫu Train và Test không khớp!"
    
    X_train_scaled, X_test_scaled, X_latest_scaled, scaler = scale_features_anti_leakage(X_train, X_test, latest_candle[FEATURE_COLUMNS])
    assert X_train_scaled.shape[1] == len(FEATURE_COLUMNS), "Số thuộc tính sau scale bị sai lệch!"
    print(f" -> Tập Train: {len(X_train)} mẫu | Tập Test: {len(X_test)} mẫu | Thuộc tính: {X.shape[1]}")

    # 3. Kiểm tra Rough Set (Reduct) & Feature Selection
    print("\n[3/8] Kiểm tra Module Tập thô (Reduct) & Lựa chọn đặc trưng...")
    rough_res = compute_rough_set_reduct(X, y)
    assert 'reduct_attributes' in rough_res, "Không tìm thấy tập Reduct!"
    assert len(rough_res['reduct_attributes']) > 0, "Tập Reduct rỗng!"
    
    feat_sel_res = compute_feature_selection_comparison(X, y, top_k=8)
    assert len(feat_sel_res['rf_ranking']) > 0, "Không có kết quả xếp hạng Random Forest!"
    print(f" -> Thuộc tính ban đầu: {rough_res['total_attributes_initial']} -> Reduct: {rough_res['reduct_size']} (Giảm {rough_res['reduction_rate_pct']}%)")

    # 4. Kiểm tra Huấn Luyện 4 Mô Hình & Đánh Giá Metrics
    print("\n[4/8] Kiểm tra Huấn Luyện 4 Thuật Toán & Đánh Giá Metrics...")
    trained_models = {}
    for m_key in AVAILABLE_MODELS.keys():
        m = train_single_model(m_key, X_train_scaled, y_train)
        metrics = evaluate_classification_model(m, X_test_scaled, y_test)
        trained_models[m_key] = {'model': m, 'model_name': AVAILABLE_MODELS[m_key]['name'], 'metrics': metrics}
        save_model_bundle('FPT', m_key, m, scaler, FEATURE_COLUMNS, metrics)
        print(f" -> {AVAILABLE_MODELS[m_key]['name']}: Accuracy = {metrics['accuracy']}%, F1 = {metrics['f1_score']}%")

    comp_res = compare_all_models_performance(trained_models, X_test_scaled, y_test)
    print(f" -> [BEST MODEL ĐƯỢC CHỌN]: {comp_res['best_model_name']}")

    # 5. Kiểm tra Module Dự Đoán & Mô Phỏng What-If
    print("\n[5/8] Kiểm tra Module Dự Đoán Phiên Tiếp Theo & Mô Phỏng What-If...")
    pred_res = predict_next_trading_day('FPT', 'random_forest')
    assert pred_res['prediction_label'] in [0, 1], "Nhãn dự đoán không hợp lệ!"
    assert 0 <= pred_res['prob_up'] <= 100, "Xác suất TĂNG không hợp lệ!"
    print(f" -> Kết quả dự đoán FPT: {pred_res['prediction_text']} (Xác suất TĂNG: {pred_res['prob_up']}%, GIẢM: {pred_res['prob_down']}%)")
    
    sim_res = predict_custom_scenario('FPT', 'random_forest', {'rsi': 78, 'macd': 150, 'daily_return': 2.5})
    print(f" -> Mô phỏng kịch bản RSI=78, Return=+2.5%: {sim_res['prediction_text']} (P(TĂNG)={sim_res['prob_up']}%)")

    # 6. Kiểm tra Gom Cụm K-Means
    print("\n[6/8] Kiểm tra Module Gom Cụm K-Means...")
    cluster_res = perform_hose_stocks_clustering(n_clusters=3)
    assert len(cluster_res['cluster_profiles']) == 3, "Số cụm không đúng 3 cụm!"
    print(f" -> Phân cụm thành công {cluster_res['total_stocks']} mã cổ phiếu HOSE thành 3 nhóm thị trường.")

    # 7. Kiểm tra Khai Thác Cảm Xúc Mạng Xã Hội
    print("\n[7/8] Kiểm tra Module Khai Thác Cảm Xúc Truyền Thông Xã Hội...")
    sentiment_res = analyze_social_sentiment_for_stock('FPT')
    assert sentiment_res['total_comments'] > 0, "Không có bình luận mạng xã hội!"
    print(f" -> Phân tích {sentiment_res['total_comments']} bình luận: Tích cực {sentiment_res['positive_pct']}%, Trung lập {sentiment_res['neutral_pct']}%, Tiêu cực {sentiment_res['negative_pct']}%")

    # 8. Kiểm tra Flask Web App Routes
    print("\n[8/8] Kiểm tra Flask Web App Routes & API Client...")
    app = create_app()
    client = app.test_client()
    
    routes_to_test = [
        ('/', 200),
        ('/historical?symbol=FPT', 200),
        ('/indicators?symbol=FPT', 200),
        ('/reduct?symbol=FPT', 200),
        ('/training?symbol=FPT', 200),
        ('/comparison?symbol=FPT', 200),
        ('/prediction?symbol=FPT', 200),
        ('/clustering?k=3', 200),
        ('/sentiment?symbol=FPT', 200),
        ('/theory', 200),
        ('/api/chart/historical/FPT', 200),
        ('/api/chart/indicators/FPT', 200),
    ]
    
    for r, expected_status in routes_to_test:
        resp = client.get(r)
        assert resp.status_code == expected_status, f"Route {r} trả về status {resp.status_code}, mong đợi {expected_status}"
        print(f" -> Route {r} : [OK HTTP {resp.status_code}]")

    print("\n=======================================================")
    print(" TẤT CẢ 8/8 HẠNG MỤC KIỂM THỬ ĐÃ VƯỢT QUA 100% THÀNH CÔNG!")
    print("=======================================================\n")


if __name__ == '__main__':
    run_all_tests()
