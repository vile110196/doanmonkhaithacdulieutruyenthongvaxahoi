"""
desktop_launcher.py
Trình khởi chạy 1-Click: Tự động khởi động Flask Server và tự động mở Trình duyệt Web.
Không yêu cầu người dùng phải gõ lệnh vào Terminal/CMD.
"""

import os
import sys
import time
import webbrowser
import threading
from app import create_app

def open_browser():
    """Chờ 1.2 giây cho Flask khởi động rồi tự động bật trình duyệt."""
    time.sleep(1.2)
    url = "http://127.0.0.1:5000"
    print(f"\n=======================================================")
    print(f" [OK] HE THONG DANG CHAY TAI: {url}")
    print(f" [OK] DANG TU DONG MO TRINH DUYET...")
    print(f"=======================================================\n")
    webbrowser.open(url)

if __name__ == '__main__':
    app = create_app()
    
    # Khởi chạy thread mở trình duyệt
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Chạy Flask Server
    app.run(host='127.0.0.1', port=5000, debug=False)
