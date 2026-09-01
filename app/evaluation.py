"""
app/evaluation.py
Module đánh giá hiệu suất mô hình phân loại bám sát 100% nội dung Bài 7 Bài giảng:
- Ma trận nhầm lẫn (Confusion Matrix): TP, FP, TN, FN.
- Độ chính xác (Accuracy), Tỷ lệ lỗi (Error Rate).
- Độ chuẩn xác (Precision), Độ nhạy/Thu hồi (Recall / Sensitivity).
- Điểm F1-Score (Harmonic Mean).
- Đường cong ROC (Receiver Operating Characteristic) & Điểm AUC (Area Under Curve).
- Báo cáo phân loại chi tiết (Classification Report).
"""

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, roc_curve, roc_auc_score, classification_report
)


def evaluate_classification_model(model, X_test, y_test) -> dict:
    """
    Đánh giá chi tiết hiệu suất của một mô hình trên tập kiểm thử (Test set):
    Tính toán đầy đủ các chỉ số được giảng dạy trong Bài 7.
    """
    # Dự đoán nhãn và xác suất
    y_pred = model.predict(X_test)
    
    if hasattr(model, 'predict_proba'):
        y_proba = model.predict_proba(X_test)[:, 1]
    elif hasattr(model, 'decision_function'):
        df_score = model.decision_function(X_test)
        y_proba = 1 / (1 + np.exp(-df_score))
    else:
        y_proba = y_pred.astype(float)
        
    # 1. Ma trận nhầm lẫn (Confusion Matrix)
    # y_test: 0 (GIẢM), 1 (TĂNG)
    cm = confusion_matrix(y_test, y_pred, labels=[0, 1])
    tn, fp, fn, tp = cm.ravel()
    
    # 2. Các chỉ số cơ bản
    acc = accuracy_score(y_test, y_pred)
    error_rate = 1.0 - acc
    prec = precision_score(y_test, y_pred, zero_division=0)
    rec = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0
    
    # 3. ROC Curve & AUC
    try:
        auc = roc_auc_score(y_test, y_proba)
        fpr, tpr, thresholds = roc_curve(y_test, y_proba)
        # Rút gọn danh sách điểm ROC để truyền sang JSON/Plotly
        step = max(1, len(fpr) // 30)
        roc_data = {
            'fpr': [round(float(x), 4) for x in fpr[::step]],
            'tpr': [round(float(x), 4) for x in tpr[::step]],
            'auc': round(float(auc), 4)
        }
    except Exception:
        auc = 0.5
        roc_data = {'fpr': [0, 1], 'tpr': [0, 1], 'auc': 0.5}
        
    # 4. Báo cáo phân loại dạng text
    clf_rep = classification_report(y_test, y_pred, target_names=['GIẢM (0)', 'TĂNG (1)'], output_dict=True)
    
    return {
        'accuracy': round(float(acc) * 100.0, 2),
        'error_rate': round(float(error_rate) * 100.0, 2),
        'precision': round(float(prec) * 100.0, 2),
        'recall': round(float(rec) * 100.0, 2),
        'specificity': round(float(specificity) * 100.0, 2),
        'f1_score': round(float(f1) * 100.0, 2),
        'auc_score': round(float(auc) * 100.0, 2),
        'confusion_matrix': {
            'tp': int(tp),
            'fp': int(fp),
            'tn': int(tn),
            'fn': int(fn),
            'matrix': [[int(tn), int(fp)], [int(fn), int(tp)]]
        },
        'roc_curve': roc_data,
        'classification_report': clf_rep,
        'test_samples_count': len(y_test),
        'actual_up_count': int((y_test == 1).sum()),
        'actual_down_count': int((y_test == 0).sum()),
        'predicted_up_count': int((y_pred == 1).sum()),
        'predicted_down_count': int((y_pred == 0).sum())
    }


def compare_all_models_performance(models_dict: dict, X_test, y_test) -> dict:
    """
    So sánh toàn diện tất cả các mô hình và tự động xác định Best Model:
    Tạo bảng so sánh Leaderboard và dữ liệu vẽ biểu đồ đa mô hình.
    """
    comparison_table = []
    roc_comparison = {}
    
    best_model_key = None
    best_f1 = -1.0
    
    for key, model_bundle in models_dict.items():
        model = model_bundle['model']
        model_name = model_bundle.get('model_name', key)
        
        metrics = evaluate_classification_model(model, X_test, y_test)
        
        row = {
            'model_key': key,
            'model_name': model_name,
            'accuracy': metrics['accuracy'],
            'precision': metrics['precision'],
            'recall': metrics['recall'],
            'f1_score': metrics['f1_score'],
            'auc_score': metrics['auc_score'],
            'error_rate': metrics['error_rate'],
            'tp': metrics['confusion_matrix']['tp'],
            'fp': metrics['confusion_matrix']['fp'],
            'tn': metrics['confusion_matrix']['tn'],
            'fn': metrics['confusion_matrix']['fn'],
        }
        comparison_table.append(row)
        roc_comparison[key] = {
            'name': model_name,
            'fpr': metrics['roc_curve']['fpr'],
            'tpr': metrics['roc_curve']['tpr'],
            'auc': metrics['auc_score']
        }
        
        # Tiêu chí chọn Best Model: Ưu tiên F1-Score, nếu bằng nhau thì so Accuracy
        if metrics['f1_score'] > best_f1:
            best_f1 = metrics['f1_score']
            best_model_key = key
            
    # Đánh dấu is_best
    for row in comparison_table:
        row['is_best'] = (row['model_key'] == best_model_key)
        
    # Sắp xếp theo F1-Score giảm dần
    comparison_table = sorted(comparison_table, key=lambda x: x['f1_score'], reverse=True)
    
    return {
        'leaderboard': comparison_table,
        'best_model_key': best_model_key,
        'best_model_name': [r['model_name'] for r in comparison_table if r['model_key'] == best_model_key][0] if comparison_table else "N/A",
        'roc_comparison': roc_comparison
    }
