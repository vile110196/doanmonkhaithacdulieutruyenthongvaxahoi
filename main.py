"""
main.py
Điểm khởi chạy chính của ứng dụng Flask Web Dashboard.
"""

from app import create_app

app = create_app()

if __name__ == '__main__':
    # Chạy trên cổng 5000 với chế độ debug tắt để tối ưu hiệu năng
    app.run(host='127.0.0.1', port=5000, debug=False)
