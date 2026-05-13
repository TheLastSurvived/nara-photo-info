import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    SECRET_KEY = 'super-secret-key'
    
    UPLOAD_FOLDER = 'static/img/upload'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    FLASK_ADMIN_SWATCH = 'cerulean'
    DEBUG = True

    ORDER_UPLOAD_FOLDER = 'static/uploads/orders'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'zip'}
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB максимум