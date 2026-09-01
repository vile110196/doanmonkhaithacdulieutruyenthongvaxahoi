"""
app/models.py
Module xây dựng và quản lý 4 thuật toán phân lớp trọng tâm theo đúng bài giảng môn học:
1. Decision Tree (Cây quyết định - Gini / Entropy, Node, Branch, Leaf).
2. Naive Bayes (GaussianNB - Định lý Bayes, Giả định độc lập điều kiện, Hàm mật độ Gauss).
3. Logistic Regression (Hồi quy Logistic - Hàm Sigmoid, Ngưỡng phân lớp nhị phân).
4. Random Forest (Rừng ngẫu nhiên - Ensemble Bagging, Biểu quyết đa số, Feature Importance).
Lưu trữ và tái sử dụng mô hình bằng `joblib`.
"""

import os
import joblib
import numpy as np
import pandas as pd
from datetime import datetime
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier

from config import Config
from utils.helpers import logger


AVAILABLE_MODELS = {
    'decision_tree': {
        'name': 'Decision Tree (Cây Quyết Định)',
        'description': 'Mô hình phân nhánh phân cấp dựa trên chỉ số Entropy / Gini Index để chia tách không gian đặc trưng.',
        'class': DecisionTreeClassifier
    },
    'naive_bayes': {
        'name': 'Gaussian Naive Bayes (Bayes Ngây Thơ)',
        'description': 'Mô hình xác suất có điều kiện dựa trên Định lý Bayes với giả định các đặc trưng độc lập thống kê.',
        'class': GaussianNB
    },
    'logistic_regression': {
        'name': 'Logistic Regression (Hồi Quy Logistic)',
        'description': 'Mô hình phân loại tuyến tính ánh xạ qua hàm kích hoạt Sigmoid để ước tính xác suất TĂNG/GIẢM.',
        'class': LogisticRegression
    },
    'random_forest': {
        'name': 'Random Forest (Rừng Ngẫu Nhiên)',
        'description': 'Tập hợp Ensemble của nhiều cây quyết định độc lập kết hợp cơ chế lấy mẫu ngẫu nhiên (Bagging).',
        'class': RandomForestClassifier
    }
}


def create_model_instance(model_type: str, params: dict = None):
    """Khởi tạo thực thể mô hình tương ứng với tham số tùy chỉnh."""
    if params is None:
        params = {}
        
    model_type = model_type.lower()
    
    if model_type == 'decision_tree':
        criterion = params.get('criterion', 'gini')
        max_depth = int(params.get('max_depth', 5))
        min_samples_split = int(params.get('min_samples_split', 10))
        return DecisionTreeClassifier(
            criterion=criterion,
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            random_state=42
        )
        
    elif model_type == 'naive_bayes':
        var_smoothing = float(params.get('var_smoothing', 1e-9))
        return GaussianNB(var_smoothing=var_smoothing)
        
    elif model_type == 'logistic_regression':
        C = float(params.get('C', 1.0))
        max_iter = int(params.get('max_iter', 1000))
        return LogisticRegression(C=C, max_iter=max_iter, random_state=42)
        
    elif model_type == 'random_forest':
        n_estimators = int(params.get('n_estimators', 100))
        max_depth = int(params.get('max_depth', 6))
        min_samples_split = int(params.get('min_samples_split', 8))
        return RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            random_state=42,
            n_jobs=-1
        )
    else:
        raise ValueError(f"Không hỗ trợ loại mô hình: {model_type}")


def train_single_model(model_type: str, X_train, y_train, params: dict = None):
    """Huấn luyện một mô hình phân lớp đơn lẻ."""
    model = create_model_instance(model_type, params)
    model.fit(X_train, y_train)
    return model


def get_model_save_path(symbol: str, model_type: str) -> str:
    """Tạo đường dẫn lưu file model .pkl."""
    os.makedirs(Config.MODELS_DIR, exist_ok=True)
    return os.path.join(Config.MODELS_DIR, f"{symbol.upper()}_{model_type.lower()}.pkl")


def save_model_bundle(symbol: str, model_type: str, model, scaler, feature_columns: list, metrics: dict, extra_info: dict = None):
    """
    Lưu toàn bộ gói mô hình bao gồm Model, Scaler, Tên đặc trưng và Metrics bằng joblib.
    """
    save_path = get_model_save_path(symbol, model_type)
    bundle = {
        'symbol': symbol.upper(),
        'model_type': model_type.lower(),
        'model_name': AVAILABLE_MODELS.get(model_type.lower(), {}).get('name', model_type),
        'model': model,
        'scaler': scaler,
        'feature_columns': feature_columns,
        'metrics': metrics,
        'extra_info': extra_info or {},
        'saved_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    joblib.dump(bundle, save_path)
    logger.info(f"Đã lưu mô hình vào {save_path}")
    return save_path


def load_model_bundle(symbol: str, model_type: str):
    """Nạp gói mô hình đã lưu từ disk."""
    save_path = get_model_save_path(symbol, model_type)
    if os.path.exists(save_path):
        bundle = joblib.load(save_path)
        return bundle
    return None


def get_model_explanation_details(model, model_type: str, feature_names: list) -> dict:
    """
    Trích xuất giải thích cơ chế hoạt động của mô hình phục vụ báo cáo / bảo vệ đồ án:
    - Decision Tree: Độ sâu cây, số lá, luật phân nhánh rút gọn.
    - Naive Bayes: Giá trị trung bình (mu) và phương sai (sigma^2) của từng thuộc tính theo từng lớp TĂNG/GIẢM.
    - Logistic Regression: Trọng số (weights) của từng thuộc tính và hệ số chặn (bias).
    - Random Forest: Feature importance tổng hợp từ 100 cây.
    """
    details = {}
    model_type = model_type.lower()
    
    if model_type == 'decision_tree':
        details['tree_depth'] = int(model.get_depth())
        details['n_leaves'] = int(model.get_n_leaves())
        try:
            tree_rules = export_text(model, feature_names=feature_names, max_depth=3)
            details['tree_rules_text'] = tree_rules
        except Exception:
            details['tree_rules_text'] = "Không thể trích xuất text rules."
            
    elif model_type == 'naive_bayes':
        if hasattr(model, 'theta_') and hasattr(model, 'var_'):
            # theta_[0] là mean class 0 (GIẢM), theta_[1] là mean class 1 (TĂNG)
            nb_stats = []
            for i, feat in enumerate(feature_names[:8]):
                nb_stats.append({
                    'feature': feat,
                    'mean_down': round(float(model.theta_[0][i]), 4),
                    'mean_up': round(float(model.theta_[1][i]), 4),
                    'var_down': round(float(model.var_[0][i]), 4),
                    'var_up': round(float(model.var_[1][i]), 4),
                })
            details['gaussian_parameters'] = nb_stats
            details['class_prior'] = [round(float(p), 4) for p in model.class_prior_]
            
    elif model_type == 'logistic_regression':
        if hasattr(model, 'coef_'):
            coefs = model.coef_[0]
            lr_weights = []
            for feat, coef in zip(feature_names, coefs):
                lr_weights.append({
                    'feature': feat,
                    'weight': round(float(coef), 4),
                    'impact': 'Tích cực (Ủng hộ TĂNG)' if coef > 0 else 'Tiêu cực (Ủng hộ GIẢM)'
                })
            lr_weights = sorted(lr_weights, key=lambda x: abs(x['weight']), reverse=True)
            details['weights'] = lr_weights
            details['intercept'] = round(float(model.intercept_[0]), 4)
            
    elif model_type == 'random_forest':
        if hasattr(model, 'feature_importances_'):
            rf_imp = []
            for feat, imp in zip(feature_names, model.feature_importances_):
                rf_imp.append({
                    'feature': feat,
                    'importance_pct': round(float(imp) * 100.0, 2)
                })
            rf_imp = sorted(rf_imp, key=lambda x: x['importance_pct'], reverse=True)
            details['feature_importances'] = rf_imp
            details['n_estimators'] = model.n_estimators
            
    return details
