from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from sqlalchemy import or_
from config import Config
from models import db, User, Service
import os
from datetime import datetime, date
import uuid 

app = Flask(__name__)
app.config.from_object(Config)

# Инициализация расширений
db.init_app(app)

# Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Пожалуйста, войдите в систему для доступа к этой странице.'
login_manager.login_message_category = 'warning'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/price')
def price():
    # Получаем параметры фильтрации из URL
    category_filter = request.args.get('category', 'all')
    sort_by = request.args.get('sort', 'default')
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')
    
    # Базовый запрос
    query = Service.query
    
    # Фильтрация по категории
    if category_filter != 'all':
        query = query.filter_by(category=category_filter)
    
    # Фильтрация по цене (если есть price_value)
    if min_price:
        try:
            query = query.filter(Service.price_value >= float(min_price))
        except:
            pass
    if max_price:
        try:
            query = query.filter(Service.price_value <= float(max_price))
        except:
            pass
    
    # Сортировка
    if sort_by == 'price_asc':
        query = query.order_by(Service.price_value.asc())
    elif sort_by == 'price_desc':
        query = query.order_by(Service.price_value.desc())
    elif sort_by == 'title':
        query = query.order_by(Service.title.asc())
    elif sort_by == 'popular':
        query = query.filter_by(is_popular=True).order_by(Service.created_at.desc())
    else:
        query = query.order_by(Service.category, Service.created_at.desc())
    
    services = query.all()
    
    # Группируем услуги по категориям для якорей
    printing_services = [s for s in services if s.category == 'printing']
    photo_session_packages = [s for s in services if s.category == 'photo_session']
    special_offers = [s for s in services if s.category == 'special_offers']
    
    # Получаем уникальные категории для фильтра
    categories = db.session.query(Service.category).distinct().all()
    categories = [c[0] for c in categories]
    
    return render_template('price.html',
                         services=services,
                         printing_services=printing_services,
                         photo_session_packages=photo_session_packages,
                         special_offers=special_offers,
                         categories=categories,
                         current_category=category_filter,
                         current_sort=sort_by)

@app.route('/portfolio')
def portfolio():
    return render_template('portfolio.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password')
        remember = request.form.get('remember') == 'on'
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            if user.is_active:
                login_user(user, remember=remember)
                flash('Вы успешно вошли в систему!', 'success')
                
                # Перенаправление на страницу, с которой пришли
                next_page = request.args.get('next')
                return redirect(next_page or url_for('index'))
            else:
                flash('Ваш аккаунт заблокирован', 'error')
        else:
            flash('Неверный email или пароль', 'error')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        # Получаем данные из формы
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Валидация
        errors = []
        
        if not email:
            errors.append('Email обязателен')
        if not password:
            errors.append('Пароль обязателен')
        

        if len(password) < 6:
            errors.append('Пароль должен быть не менее 6 символов')
        
        # Проверка совпадения паролей
        if password != confirm_password:
            errors.append('Пароли не совпадают')
        
        if User.query.filter_by(email=email).first():
            errors.append('Email уже используется')
        
        # Если есть ошибки, показываем их
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('register.html', 
                                 username=username,
                                 email=email,
                                 first_name=first_name,
                                 last_name=last_name,
                                 phone=phone)
        
        # Создание пользователя
        try:
            user = User(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                phone=phone
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            flash('Регистрация успешна! Теперь вы можете войти в систему.', 'success')
            return redirect(url_for('login'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Произошла ошибка при регистрации: {str(e)}', 'error')
    
    # GET запрос - просто показываем форму
    return render_template('register.html')


@app.route('/profile')
def profile():
    return render_template('profile.html')


@app.route('/service/<int:service_id>')
def service_detail(service_id):
    service = Service.query.get_or_404(service_id)
    return render_template('service_detail.html', service=service)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('index'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    app.run(debug=True)