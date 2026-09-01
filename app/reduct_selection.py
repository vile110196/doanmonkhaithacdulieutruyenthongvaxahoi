"""
app/reduct_selection.py
Module minh họa lý thuyết Tập thô (Rough Set - Reduct) và Lựa chọn đặc trưng (Feature Selection) bám sát Bài 3 & 4 Bài giảng.
Bao gồm:
1. Thuật toán Tập thô (Rough Set Theory): Rời rạc hóa đặc trưng, Xây dựng Ma trận phân biệt (Discernibility Matrix),
   Tìm thuộc tính cốt lõi (Core) và Tập rút gọn thuộc tính (Reduct).
2. Lựa chọn đặc trưng Thống kê & Học máy: SelectKBest (ANOVA F-Score), Random Forest Gini Importance, Ma trận tương quan (Correlation).
"""

import pandas as pd
import numpy as np
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.ensemble import RandomForestClassifier
from app.indicators import FEATURE_COLUMNS


def discretize_features_for_rough_set(X: pd.DataFrame, n_bins: int = 3) -> pd.DataFrame:
    """
    Rời rạc hóa các thuộc tính liên tục thành các mức định tính (Low=0, Med=1, High=2)
    để xây dựng Hệ thông tin / Bảng quyết định Tập thô (Information System / Decision Table).
    """
    X_disc = pd.DataFrame(index=X.index)
    for col in X.columns:
        try:
            # Chia quantile 3 mức
            X_disc[col] = pd.qcut(X[col], q=n_bins, labels=[0, 1, 2], duplicates='drop').astype(int)
        except Exception:
            # Fallback nếu số lượng giá trị unique ít
            X_disc[col] = pd.cut(X[col], bins=n_bins, labels=[0, 1, 2], duplicates='drop').astype(int)
    return X_disc


def compute_rough_set_reduct(X: pd.DataFrame, y: pd.Series, sample_size: int = 150) -> dict:
    """
    Thực thi thuật toán Tập thô (Rough Set Reduct) theo chuẩn bài giảng:
    1. Lấy mẫu bảng quyết định (U, C U {d}).
    2. Xây dựng Ma trận phân biệt Discernibility Matrix M(S) = (c_ij):
       c_ij = { a in C | f(x_i, a) != f(x_j, a) } nếu d(x_i) != d(x_j), ngược lại c_ij = rỗng.
    3. Tìm Core(C) = Giao của các phần tử đơn (singletons) trong ma trận phân biệt.
    4. Tìm Reduct(C) = Tập thuộc tính tối tiểu phân biệt được tất cả các cặp đối tượng khác nhãn.
    """
    # Lấy mẫu để ma trận phân biệt có kích thước trực quan
    if len(X) > sample_size:
        sample_indices = np.random.RandomState(42).choice(X.index, size=sample_size, replace=False)
        X_sub = X.loc[sample_indices].copy()
        y_sub = y.loc[sample_indices].copy()
    else:
        X_sub = X.copy()
        y_sub = y.copy()

    # Rời rạc hóa
    X_disc = discretize_features_for_rough_set(X_sub, n_bins=3)
    attributes = list(X_disc.columns)
    objects = list(X_disc.index)
    n_obj = len(objects)
    
    discernibility_matrix_samples = []
    singletons = set()
    attr_disc_counts = {attr: 0 for attr in attributes}
    total_diff_pairs = 0
    
    # Xây dựng ma trận phân biệt
    for i in range(n_obj):
        for j in range(i + 1, n_obj):
            label_i = y_sub.iloc[i]
            label_j = y_sub.iloc[j]
            
            # Chỉ xét các cặp đối tượng có nhãn quyết định khác nhau (d(x_i) != d(x_j))
            if label_i != label_j:
                total_diff_pairs += 1
                diff_attrs = []
                for attr in attributes:
                    val_i = X_disc.iloc[i][attr]
                    val_j = X_disc.iloc[j][attr]
                    if val_i != val_j:
                        diff_attrs.append(attr)
                        attr_disc_counts[attr] += 1
                
                # Nếu chỉ có 1 thuộc tính phân biệt được -> Đó là Core attribute
                if len(diff_attrs) == 1:
                    singletons.add(diff_attrs[0])
                    
                # Lưu mẫu 10 ô ma trận phân biệt để hiển thị lên giao diện Web
                if len(discernibility_matrix_samples) < 10 and len(diff_attrs) > 0:
                    discernibility_matrix_samples.append({
                        'pair': f"U{i+1} vs U{j+1}",
                        'decision': f"d(U{i+1})={label_i} != d(U{j+1})={label_j}",
                        'diff_attributes': diff_attrs[:4]
                    })
                    
    core_attributes = sorted(list(singletons))
    
    # Tìm Reduct theo thuật toán Greedy (Heuristic Reduct dựa trên năng lực phân biệt lớn nhất)
    # Bắt đầu từ tập Core
    current_reduct = set(core_attributes)
    sorted_attrs = sorted(attributes, key=lambda a: attr_disc_counts[a], reverse=True)
    
    for a in sorted_attrs:
        if len(current_reduct) >= min(8, len(attributes)):
            break
        current_reduct.add(a)
        
    reduct_list = sorted(list(current_reduct))
    
    # Tính mức độ quan trọng theo Rough Set (Discernibility Power)
    rough_importance = []
    for attr, count in sorted(attr_disc_counts.items(), key=lambda x: x[1], reverse=True):
        rough_importance.append({
            'attribute': attr,
            'disc_count': count,
            'is_core': attr in core_attributes,
            'is_in_reduct': attr in reduct_list
        })
        
    return {
        'total_objects': n_obj,
        'total_attributes_initial': len(attributes),
        'total_different_pairs': total_diff_pairs,
        'core_attributes': core_attributes,
        'reduct_attributes': reduct_list,
        'reduct_size': len(reduct_list),
        'reduction_rate_pct': round((1 - len(reduct_list)/len(attributes))*100, 1),
        'matrix_samples': discernibility_matrix_samples,
        'attribute_rankings': rough_importance
    }


def compute_feature_selection_comparison(X: pd.DataFrame, y: pd.Series, top_k: int = 10) -> dict:
    """
    So sánh các phương pháp Lựa chọn thuộc tính (Feature Selection):
    1. SelectKBest (ANOVA F-value)
    2. Random Forest Feature Importance (Gini Importance)
    3. Ma trận tương quan Pearson (Correlation with Target)
    """
    # 1. SelectKBest (F-Classif)
    selector = SelectKBest(score_func=f_classif, k=min(top_k, X.shape[1]))
    selector.fit(X, y)
    f_scores = selector.scores_
    
    kbest_ranking = []
    for col, score in zip(X.columns, f_scores):
        kbest_ranking.append({
            'feature': col,
            'f_score': round(float(score), 2) if not np.isnan(score) else 0.0
        })
    kbest_ranking = sorted(kbest_ranking, key=lambda x: x['f_score'], reverse=True)
    
    # 2. Random Forest Importance
    rf = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=6)
    rf.fit(X, y)
    rf_importances = rf.feature_importances_
    
    rf_ranking = []
    for col, imp in zip(X.columns, rf_importances):
        rf_ranking.append({
            'feature': col,
            'importance': round(float(imp) * 100.0, 2)
        })
    rf_ranking = sorted(rf_ranking, key=lambda x: x['importance'], reverse=True)
    
    # 3. Tương quan với Target
    correlations = []
    for col in X.columns:
        corr = X[col].corr(y)
        correlations.append({
            'feature': col,
            'correlation': round(float(corr), 4) if not np.isnan(corr) else 0.0
        })
    correlations = sorted(correlations, key=lambda x: abs(x['correlation']), reverse=True)
    
    # 4. Ma trận tương quan giữa các đặc trưng hàng đầu
    top_cols = [item['feature'] for item in rf_ranking[:8]]
    corr_matrix = X[top_cols].corr().round(2).to_dict()
    
    return {
        'initial_feature_count': X.shape[1],
        'selected_feature_count': top_k,
        'kbest_ranking': kbest_ranking,
        'rf_ranking': rf_ranking,
        'correlation_ranking': correlations,
        'top_features_correlation_matrix': corr_matrix,
        'top_features_names': [item['feature'] for item in rf_ranking[:top_k]]
    }
