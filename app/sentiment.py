"""
app/sentiment.py
Module khai thác dữ liệu truyền thông xã hội (Social Media Sentiment Analysis):
- Phân tích cảm xúc bài đăng / bình luận của cộng đồng nhà đầu tư chứng khoán.
- Phân loại: Tích cực (Positive), Trung lập (Neutral), Tiêu cực (Negative).
- Thống kê tỷ lệ phân bổ cảm xúc & tương quan giữa Chỉ số cảm xúc (Sentiment Score) và Biến động giá cổ phiếu.
- Hỗ trợ tải lên file CSV bình luận tùy chỉnh.
"""

import os
import re
import pandas as pd
import numpy as np
from config import Config
from utils.mock_generator import generate_sample_social_sentiment
from app.data_loader import load_stock_data


# Từ điển cảm xúc tài chính chứng khoán tiếng Việt
VN_FINANCIAL_LEXICON = {
    'positive': [
        'tăng', 'bứt phá', 'vượt đỉnh', 'múc', 'gom', 'siêu cổ', 'mua ròng', 'lợi nhuận khủng',
        'doanh thu tăng', 'cổ tức', 'tiềm năng', 'xuất sắc', 'hồi phục', 'đáy', 'dòng tiền vào',
        'xanh', 'tím', 'trần', 'target', 'kỳ vọng', 'ủng hộ', 'uy tín', 'lệnh to', 'tốt', 'vững'
    ],
    'negative': [
        'giảm', 'thủng', 'gãy', 'xả', 'bán ròng', 'sập', 'chốt lời', 'đu đỉnh', 'lỗ', 'thua lỗ',
        'cảnh báo', 'tiêu cực', 'xấu', 'rủi ro', 'áp lực', 'bán tháo', 'sàn', 'đỏ', 'gãy trend',
        'phân kỳ âm', 'yếu', 'thất vọng', 'kém', 'tháo chạy', 'call margin'
    ]
}


def rule_based_sentiment_score(text: str) -> (str, float):
    """
    Tính điểm cảm xúc (Sentiment Score từ -1.0 đến +1.0) và phân loại nhãn.
    """
    text_lower = str(text).lower()
    
    pos_count = sum(1 for word in VN_FINANCIAL_LEXICON['positive'] if word in text_lower)
    neg_count = sum(1 for word in VN_FINANCIAL_LEXICON['negative'] if word in text_lower)
    
    total = pos_count + neg_count
    if total == 0:
        return 'Neutral', 0.0
        
    score = (pos_count - neg_count) / total
    
    if score > 0.15:
        return 'Positive', round(float(score), 3)
    elif score < -0.15:
        return 'Negative', round(float(score), 3)
    else:
        return 'Neutral', round(float(score), 3)


def load_or_generate_social_data(symbol: str) -> pd.DataFrame:
    """Tải file dữ liệu bình luận mạng xã hội hoặc sinh file mẫu."""
    os.makedirs(Config.SOCIAL_DATA_DIR, exist_ok=True)
    file_path = os.path.join(Config.SOCIAL_DATA_DIR, f"{symbol.upper()}_social_sentiment.csv")
    
    if not os.path.exists(file_path):
        generate_sample_social_sentiment(symbol.upper(), Config.SOCIAL_DATA_DIR)
        
    df = pd.read_csv(file_path)
    df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')
    return df


def analyze_social_sentiment_for_stock(symbol: str, df_social: pd.DataFrame = None) -> dict:
    """
    Phân tích toàn diện dữ liệu truyền thông xã hội cho một mã cổ phiếu:
    1. Thống kê tỷ lệ phân bổ nhãn cảm xúc (Positive, Neutral, Negative).
    2. Điểm cảm xúc trung bình theo ngày.
    3. Ghép nối với biến động giá cổ phiếu để tạo biểu đồ tương quan Price vs Sentiment.
    """
    symbol = symbol.upper()
    if df_social is None or len(df_social) == 0:
        df_social = load_or_generate_social_data(symbol)
        
    # Tính điểm cảm xúc nếu chưa có
    if 'Sentiment' not in df_social.columns or 'SentimentScore' not in df_social.columns:
        sentiments = []
        scores = []
        for content in df_social['Content']:
            sent, sc = rule_based_sentiment_score(content)
            sentiments.append(sent)
            scores.append(sc)
        df_social['Sentiment'] = sentiments
        df_social['SentimentScore'] = scores
        
    total_comments = len(df_social)
    pos_count = int((df_social['Sentiment'] == 'Positive').sum())
    neu_count = int((df_social['Sentiment'] == 'Neutral').sum())
    neg_count = int((df_social['Sentiment'] == 'Negative').sum())
    
    pos_pct = round(pos_count / (total_comments + 1e-9) * 100.0, 1)
    neu_pct = round(neu_count / (total_comments + 1e-9) * 100.0, 1)
    neg_pct = round(neg_count / (total_comments + 1e-9) * 100.0, 1)
    
    avg_score = round(float(df_social['SentimentScore'].mean()), 3)
    
    # 2. Tổng hợp theo ngày
    daily_sentiment = df_social.groupby('Date').agg(
        avg_sentiment=('SentimentScore', 'mean'),
        comment_count=('Content', 'count'),
        positive_count=('Sentiment', lambda s: (s == 'Positive').sum()),
        negative_count=('Sentiment', lambda s: (s == 'Negative').sum())
    ).reset_index()
    
    # 3. Lấy chuỗi giá cổ phiếu để đối sánh
    df_price, _ = load_stock_data(symbol, use_online_if_possible=False)
    if df_price is not None and len(df_price) > 0:
        df_price['Date'] = pd.to_datetime(df_price['Date']).dt.strftime('%Y-%m-%d')
        # Merge trên Date
        merged = pd.merge(df_price[['Date', 'Close', 'Volume']], daily_sentiment, on='Date', how='inner')
        merged = merged.sort_values('Date').reset_index(drop=True)
    else:
        merged = daily_sentiment
        
    # Mẫu bình luận gần đây
    recent_comments = df_social.tail(15).to_dict(orient='records')
    recent_comments.reverse()
    
    return {
        'symbol': symbol,
        'total_comments': total_comments,
        'positive_count': pos_count,
        'neutral_count': neu_count,
        'negative_count': neg_count,
        'positive_pct': pos_pct,
        'neutral_pct': neu_pct,
        'negative_pct': neg_pct,
        'overall_sentiment_score': avg_score,
        'sentiment_label': 'Lạc quan / Tích cực' if avg_score > 0.1 else ('Bi quan / Tiêu cực' if avg_score < -0.1 else 'Trung lập'),
        'timeline_data': merged.to_dict(orient='records'),
        'recent_comments': recent_comments
    }
