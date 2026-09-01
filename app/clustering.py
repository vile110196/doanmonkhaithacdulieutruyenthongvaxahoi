"""
app/clustering.py
Module gom cụm cổ phiếu (Stock Market Clustering) bám sát 100% nội dung Bài 6 Bài giảng:
- Thuật toán K-Means (Khởi tạo tâm cụm K-Means++, Cập nhật khoảng cách Euclid, Tối thiểu hóa hàm mục tiêu SSE / Inertia).
- Phương pháp chọn số cụm tối ưu: Biểu đồ khuỷu tay (Elbow Method).
- Ứng dụng thực tế: Phân nhóm các cổ phiếu HOSE theo đặc điểm thị trường (Lợi suất, Độ biến động, Thanh khoản, RSI).
"""

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from app.data_loader import load_stock_data, get_available_symbols
from app.indicators import compute_rsi


def extract_stock_market_features(symbol: str) -> dict:
    """
    Trích xuất các đặc trưng thị trường tổng quát của một mã cổ phiếu:
    1. Lợi suất trung bình năm (Annualized Return).
    2. Độ biến động rủi ro (Annualized Volatility - Độ lệch chuẩn lợi suất).
    3. Khối lượng giao dịch trung bình (Average Daily Volume).
    4. Chỉ số sức mạnh RSI trung bình (Average RSI).
    5. Hệ số biến thiên giá (Price Coefficient of Variation).
    """
    df, _ = load_stock_data(symbol, use_online_if_possible=False)
    if df is None or len(df) < 50:
        return None
        
    df['Close'] = pd.to_numeric(df['Close'], errors='coerce')
    df['Volume'] = pd.to_numeric(df['Volume'], errors='coerce')
    
    # Tính lợi suất hàng ngày
    returns = df['Close'].pct_change().dropna()
    
    # 1. Lợi suất trung bình năm (252 ngày giao dịch)
    annual_return = float(returns.mean() * 252 * 100.0)
    
    # 2. Độ biến động năm (Annualized Volatility)
    annual_volatility = float(returns.std() * np.sqrt(252) * 100.0)
    
    # 3. Khối lượng giao dịch trung bình
    avg_volume = float(df['Volume'].tail(100).mean())
    
    # 4. RSI trung bình 100 phiên gần nhất
    rsi = compute_rsi(df['Close'], 14).dropna()
    avg_rsi = float(rsi.tail(100).mean()) if len(rsi) > 0 else 50.0
    
    latest_price = float(df['Close'].iloc[-1])
    
    return {
        'symbol': symbol,
        'latest_price': latest_price,
        'annual_return': round(annual_return, 2),
        'annual_volatility': round(annual_volatility, 2),
        'avg_volume': round(avg_volume, 0),
        'avg_rsi': round(avg_rsi, 2),
    }


def perform_hose_stocks_clustering(n_clusters: int = 3) -> dict:
    """
    Thực hiện gom cụm toàn bộ các mã cổ phiếu HOSE bằng thuật toán K-Means:
    1. Trích xuất ma trận đặc trưng các mã.
    2. Tính toán đường cong Elbow (Inertia từ k=2 đến k=6).
    3. Huấn luyện mô hình K-Means với n_clusters chỉ định.
    4. Gán nhãn và diễn giải ý nghĩa kinh tế từng cụm.
    """
    symbols = get_available_symbols()
    data_list = []
    
    for sym in symbols:
        feats = extract_stock_market_features(sym)
        if feats:
            data_list.append(feats)
            
    df_cluster = pd.DataFrame(data_list)
    if len(df_cluster) < 3:
        raise ValueError("Không đủ dữ liệu cổ phiếu để thực hiện phân cụm.")
        
    feature_cols = ['annual_return', 'annual_volatility', 'avg_volume', 'avg_rsi']
    X = df_cluster[feature_cols].copy()
    
    # Chuẩn hóa đặc trưng Z-Score
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # 1. Tính toán Elbow Curve (Inertia cho k từ 2 đến min(6, len(df_cluster)-1))
    max_k = min(6, len(df_cluster) - 1)
    elbow_points = []
    for k in range(2, max_k + 1):
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        km.fit(X_scaled)
        elbow_points.append({'k': k, 'inertia': round(float(km.inertia_), 2)})
        
    # 2. Huấn luyện K-Means với n_clusters
    n_clusters = max(2, min(n_clusters, len(df_cluster) - 1))
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    cluster_labels = kmeans.fit_predict(X_scaled)
    
    df_cluster['cluster'] = cluster_labels
    
    # 3. Phân tích đặc điểm và đặt tên cho từng cụm
    cluster_profiles = []
    cluster_names_map = {}
    
    # Sắp xếp các cụm theo độ biến động tăng dần
    cluster_vol_means = df_cluster.groupby('cluster')['annual_volatility'].mean()
    sorted_clusters = cluster_vol_means.sort_values().index.tolist()
    
    profile_descriptions = [
        {
            'name': 'Cụm Cổ Phiếu Phòng Thủ (Defensive / Biến Động Thấp)',
            'desc': 'Các doanh nghiệp đầu ngành, dòng tiền ổn định, độ biến động giá thấp, rủi ro điều chỉnh thấp.',
            'badge_color': 'success'
        },
        {
            'name': 'Cụm Cổ Phiếu Tăng Trưởng (Growth / Biến Động Trung Bình)',
            'desc': 'Các doanh nghiệp có tốc độ tăng trưởng doanh thu lợi nhuận tốt, thanh khoản và biến động ở mức cân bằng.',
            'badge_color': 'primary'
        },
        {
            'name': 'Cụm Cổ Phiếu Đầu Cơ / Sóng Ngành (High Volatility / Biến Động Cao)',
            'desc': 'Các mã cổ phiếu có độ nhạy cảm cao với thị trường, thanh khoản bùng nổ, biên độ giao động mạnh.',
            'badge_color': 'warning'
        }
    ]
    
    for rank_idx, c_id in enumerate(sorted_clusters):
        c_desc = profile_descriptions[min(rank_idx, len(profile_descriptions)-1)]
        cluster_names_map[c_id] = c_desc['name']
        
        c_stocks = df_cluster[df_cluster['cluster'] == c_id]
        cluster_profiles.append({
            'cluster_id': int(c_id),
            'cluster_name': c_desc['name'],
            'description': c_desc['desc'],
            'badge_color': c_desc['badge_color'],
            'stock_count': len(c_stocks),
            'stocks': c_stocks['symbol'].tolist(),
            'avg_return': round(float(c_stocks['annual_return'].mean()), 2),
            'avg_volatility': round(float(c_stocks['annual_volatility'].mean()), 2),
            'avg_volume': round(float(c_stocks['avg_volume'].mean()), 0),
            'avg_rsi': round(float(c_stocks['avg_rsi'].mean()), 2),
        })
        
    df_cluster['cluster_name'] = df_cluster['cluster'].map(cluster_names_map)
    
    # 4. Trích xuất tâm cụm (Centroids)
    centroids_orig = scaler.inverse_transform(kmeans.cluster_centers_)
    centroids_data = []
    for c_id in range(n_clusters):
        centroids_data.append({
            'cluster_id': c_id,
            'cluster_name': cluster_names_map.get(c_id, f"Cụm {c_id}"),
            'annual_return': round(float(centroids_orig[c_id][0]), 2),
            'annual_volatility': round(float(centroids_orig[c_id][1]), 2),
            'avg_volume': round(float(centroids_orig[c_id][2]), 0),
            'avg_rsi': round(float(centroids_orig[c_id][3]), 2),
        })
        
    return {
        'n_clusters': n_clusters,
        'stocks_data': df_cluster.to_dict(orient='records'),
        'cluster_profiles': cluster_profiles,
        'centroids': centroids_data,
        'elbow_points': elbow_points,
        'total_stocks': len(df_cluster)
    }
