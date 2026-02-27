import os

class Config:
    # Secret key for session security
    SECRET_KEY = 'vally-divine-hair-2024-secret-key-change-in-production'
    
    # Database configuration for XAMPP - USING hair_salon_db
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost/hair_salon_db'  # CHANGED
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True  # Shows SQL queries for debugging
    
    # Application settings
    APP_NAME = "Vally's Divine Hair"
    APP_CONTACT = "066 403 6257"
    APP_EMAIL = "valenciaalice@gmail.com"
    
    # File upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = 'static/uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    # Business hours
    BUSINESS_HOURS = {
        'weekdays': '9:00 AM - 7:00 PM',
        'saturday': '9:00 AM - 5:00 PM',
        'sunday': 'Closed'
    }