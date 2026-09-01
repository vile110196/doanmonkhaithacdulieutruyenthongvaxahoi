"""
app/__init__.py
Khởi tạo Flask Application và đăng ký Blueprints, cấu hình template filters.
"""

import os
from flask import Flask
from config import Config
from utils.helpers import format_currency_vnd, format_number, format_percent


def create_app(config_class=Config):
    app = Flask(
        __name__,
        template_folder=os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'templates'),
        static_folder=os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'static')
    )
    app.config.from_object(config_class)
    
    # Đăng ký template filters
    app.jinja_env.filters['vnd'] = format_currency_vnd
    app.jinja_env.filters['num'] = format_number
    app.jinja_env.filters['pct'] = format_percent
    
    # Đăng ký Blueprint
    from app.routes import main_bp
    app.register_blueprint(main_bp)
    
    # Đảm bảo các thư mục dữ liệu tồn tại
    for folder in [Config.RAW_DATA_DIR, Config.PROCESSED_DATA_DIR, Config.UPLOADED_DATA_DIR, Config.SOCIAL_DATA_DIR, Config.MODELS_DIR]:
        os.makedirs(folder, exist_ok=True)
        
    return app
