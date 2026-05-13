from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.now)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    
    # Накопительная система
    loyalty_points = db.Column(db.Integer, default=0)
    total_spent = db.Column(db.Float, default=0.0)
    loyalty_level = db.Column(db.String(20), default='regular')  # regular, silver, gold
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def update_loyalty(self, amount_spent):
        """Обновление накопительной системы после заказа"""
        self.total_spent += amount_spent
        self.loyalty_points += int(amount_spent)  # 1 балл за каждую единицу валюты
        
        # Автоматическое повышение уровня
        if self.total_spent >= 5000:
            self.loyalty_level = 'gold'
        elif self.total_spent >= 1000:
            self.loyalty_level = 'silver'
        else:
            self.loyalty_level = 'regular'
    
    def get_discount_percent(self):
        """Получение скидки в зависимости от уровня"""
        if self.loyalty_level == 'gold':
            return 15
        elif self.loyalty_level == 'silver':
            return 10
        elif self.loyalty_level == 'regular':
            return 5  # минимальная скидка для всех
        return 0
    
    def can_use_points(self):
        """Может ли использовать баллы (минимальный порог)"""
        return self.loyalty_points >= 100  # можно использовать от 100 баллов
    
    def __repr__(self):
        return f'<User {self.username} | ID {self.id} | Level {self.loyalty_level}>'


class Service(db.Model):

    __tablename__ = 'services'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # 'printing', 'photo_session', 'special_offers'
    subcategory = db.Column(db.String(50))  # Для дополнительной фильтрации
    price_from = db.Column(db.String(20))
    price_period = db.Column(db.String(50))
    image_url = db.Column(db.String(200))
    features = db.Column(db.Text)
    description = db.Column(db.Text)
    order_button_text = db.Column(db.String(50), default="Заказать")
    is_popular = db.Column(db.Boolean, default=False)
    price_value = db.Column(db.Float)  # Для сортировки по цене
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    def __repr__(self):
        return f'<Service {self.title}>'
    

class Messages(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    surname = db.Column(db.String(100))
    message = db.Column(db.Text)
    email = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    def __repr__(self):
        return f'<Message {self.id}>'
    

class Review(db.Model):
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    rating = db.Column(db.Integer, default=5)
    
    # Связи
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=True)
    
    # Отношения
    user = db.relationship('User', backref=db.backref('reviews', lazy=True))
    service = db.relationship('Service', backref=db.backref('reviews', lazy=True))
    
    def __repr__(self):
        return f'<Review {self.id} by {self.user_id}>'
    

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')
    original_price = db.Column(db.Float, nullable=False)  # исходная цена
    discount_percent = db.Column(db.Float, default=0.0)    # процент скидки
    points_used = db.Column(db.Integer, default=0)         # использовано баллов
    final_price = db.Column(db.Float, nullable=False)      # итоговая цена
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # НОВОЕ ПОЛЕ: детали заказа в формате JSON
    details = db.Column(db.JSON, default=dict)  # хранит все специфические параметры
    # Отношения
    user = db.relationship('User', backref=db.backref('orders', lazy=True))
    service = db.relationship('Service', backref=db.backref('orders', lazy=True))
    
    def __repr__(self):
        return f'<Order {self.id} | Price {self.final_price}>'