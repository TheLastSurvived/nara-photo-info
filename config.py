import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    SECRET_KEY = 'super-secret-key'
    
    UPLOAD_FOLDER = 'static/img/upload'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    FLASK_ADMIN_SWATCH = 'cerulean'
    DEBUG = True