# admin.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from functools import wraps
from models import db, User, Service, Order, Review, Messages
from datetime import datetime, timedelta
import os
from werkzeug.utils import secure_filename

# Создаем blueprint для админки
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Декоратор для проверки прав администратора
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Доступ запрещен. Требуются права администратора.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# Главная админ-панель
@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    # Статистика
    total_users = User.query.count()
    total_orders = Order.query.count()
    total_services = Service.query.count()
    total_reviews = Review.query.count()
    
    # Заказы по статусам
    pending_orders = Order.query.filter_by(status='pending').count()
    completed_orders = Order.query.filter_by(status='completed').count()
    cancelled_orders = Order.query.filter_by(status='cancelled').count()
    
    # Новые пользователи за последние 7 дней
    week_ago = datetime.now() - timedelta(days=7)
    new_users = User.query.filter(User.created_at >= week_ago).count()
    
    # Общая выручка
    total_revenue = db.session.query(db.func.sum(Order.final_price)).filter_by(status='completed').scalar() or 0
    
    # Последние заказы
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    
    # Последние пользователи
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         total_orders=total_orders,
                         total_services=total_services,
                         total_reviews=total_reviews,
                         pending_orders=pending_orders,
                         completed_orders=completed_orders,
                         cancelled_orders=cancelled_orders,
                         new_users=new_users,
                         total_revenue=total_revenue,
                         recent_orders=recent_orders,
                         recent_users=recent_users)

# Управление услугами
@admin_bp.route('/services')
@login_required
@admin_required
def services():
    services = Service.query.order_by(Service.category, Service.created_at.desc()).all()
    return render_template('admin/services.html', services=services)

@admin_bp.route('/services/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_service():
    if request.method == 'POST':
        try:
            # Обработка загрузки изображения
            image_url = None
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    # Добавляем уникальный суффикс
                    name, ext = os.path.splitext(filename)
                    filename = f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
                    file.save(os.path.join('static/img/upload', filename))
                    image_url = f'img/upload/{filename}'
            
            # Создание услуги
            service = Service(
                title=request.form['title'],
                category=request.form['category'],
                subcategory=request.form.get('subcategory', ''),
                price_from=request.form['price_from'],
                price_period=request.form.get('price_period', ''),
                image_url=image_url,
                features=request.form['features'],
                description=request.form['description'],
                order_button_text=request.form.get('order_button_text', 'Заказать'),
                is_popular='is_popular' in request.form,
                price_value=float(request.form['price_value']) if request.form['price_value'] else None
            )
            
            db.session.add(service)
            db.session.commit()
            flash('Услуга успешно добавлена!', 'success')
            return redirect(url_for('admin.services'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при добавлении услуги: {str(e)}', 'danger')
    
    return render_template('admin/add_service.html')

@admin_bp.route('/services/edit/<int:service_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_service(service_id):
    service = Service.query.get_or_404(service_id)
    
    if request.method == 'POST':
        try:
            service.title = request.form['title']
            service.category = request.form['category']
            service.subcategory = request.form.get('subcategory', '')
            service.price_from = request.form['price_from']
            service.price_period = request.form.get('price_period', '')
            service.features = request.form['features']
            service.description = request.form['description']
            service.order_button_text = request.form.get('order_button_text', 'Заказать')
            service.is_popular = 'is_popular' in request.form
            service.price_value = float(request.form['price_value']) if request.form['price_value'] else None
            
            # Обработка нового изображения
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    name, ext = os.path.splitext(filename)
                    filename = f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
                    file.save(os.path.join('static/img/upload', filename))
                    service.image_url = f'img/upload/{filename}'
            
            db.session.commit()
            flash('Услуга успешно обновлена!', 'success')
            return redirect(url_for('admin.services'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при обновлении услуги: {str(e)}', 'danger')
    
    return render_template('admin/edit_service.html', service=service)

@admin_bp.route('/services/delete/<int:service_id>', methods=['POST'])
@login_required
@admin_required
def delete_service(service_id):
    service = Service.query.get_or_404(service_id)
    
    try:
        # Проверяем, есть ли связанные заказы
        if service.orders:
            flash('Нельзя удалить услугу, так как есть связанные заказы', 'warning')
            return redirect(url_for('admin.services'))
        
        db.session.delete(service)
        db.session.commit()
        flash('Услуга успешно удалена!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка при удалении услуги: {str(e)}', 'danger')
    
    return redirect(url_for('admin.services'))

# Управление заказами
@admin_bp.route('/orders')
@login_required
@admin_required
def orders():
    status_filter = request.args.get('status', 'all')
    
    query = Order.query
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    orders = query.order_by(Order.created_at.desc()).all()
    return render_template('admin/orders.html', orders=orders, current_filter=status_filter)

@admin_bp.route('/orders/<int:order_id>')
@login_required
@admin_required
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('admin/order_detail.html', order=order)

@admin_bp.route('/orders/update/<int:order_id>', methods=['POST'])
@login_required
@admin_required
def update_order(order_id):
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get('status')
    
    if new_status in ['pending', 'completed', 'cancelled']:
        try:
            old_status = order.status
            order.status = new_status
            
            # Если заказ завершен, начисляем баллы
            if new_status == 'completed' and old_status != 'completed':
                user = order.user
                user.update_loyalty(order.final_price)
                
                # Бонус за первый заказ
                completed_orders = Order.query.filter_by(user_id=user.id, status='completed').count()
                if completed_orders == 1:
                    user.loyalty_points += 100
            
            db.session.commit()
            flash(f'Статус заказа №{order.id} изменен на "{new_status}"', 'success')
            
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при обновлении заказа: {str(e)}', 'danger')
    
    return redirect(url_for('admin.order_detail', order_id=order_id))

# Управление пользователями
@admin_bp.route('/users')
@login_required
@admin_required
def users():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/users/<int:user_id>')
@login_required
@admin_required
def user_detail(user_id):
    user = User.query.get_or_404(user_id)
    orders = Order.query.filter_by(user_id=user_id).order_by(Order.created_at.desc()).all()
    reviews = Review.query.filter_by(user_id=user_id).all()
    return render_template('admin/user_detail.html', user=user, orders=orders, reviews=reviews)

@admin_bp.route('/users/toggle_admin/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def toggle_admin(user_id):
    user = User.query.get_or_404(user_id)
    
    # Не даем снять права у самого себя
    if user.id == current_user.id:
        flash('Вы не можете изменить свои права администратора', 'warning')
        return redirect(url_for('admin.users'))
    
    try:
        user.is_admin = not user.is_admin
        db.session.commit()
        flash(f'Права администратора для {user.email} {"установлены" if user.is_admin else "сняты"}', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка: {str(e)}', 'danger')
    
    return redirect(url_for('admin.user_detail', user_id=user_id))

@admin_bp.route('/users/toggle_active/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def toggle_active(user_id):
    user = User.query.get_or_404(user_id)
    
    # Не даем заблокировать самого себя
    if user.id == current_user.id:
        flash('Вы не можете заблокировать свой аккаунт', 'warning')
        return redirect(url_for('admin.users'))
    
    try:
        user.is_active = not user.is_active
        db.session.commit()
        flash(f'Пользователь {user.email} {"активирован" if user.is_active else "заблокирован"}', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка: {str(e)}', 'danger')
    
    return redirect(url_for('admin.user_detail', user_id=user_id))

# Управление отзывами
@admin_bp.route('/reviews')
@login_required
@admin_required
def reviews():
    reviews = Review.query.order_by(Review.created_at.desc()).all()
    return render_template('admin/reviews.html', reviews=reviews)

@admin_bp.route('/reviews/delete/<int:review_id>', methods=['POST'])
@login_required
@admin_required
def delete_review(review_id):
    review = Review.query.get_or_404(review_id)
    
    try:
        db.session.delete(review)
        db.session.commit()
        flash('Отзыв успешно удален', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка при удалении отзыва: {str(e)}', 'danger')
    
    return redirect(url_for('admin.reviews'))

# Сообщения из контактной формы
@admin_bp.route('/messages')
@login_required
@admin_required
def messages():
    messages = Messages.query.order_by(Messages.created_at.desc()).all()
    return render_template('admin/messages.html', messages=messages)

@admin_bp.route('/messages/delete/<int:message_id>', methods=['POST'])
@login_required
@admin_required
def delete_message(message_id):
    message = Messages.query.get_or_404(message_id)
    
    try:
        db.session.delete(message)
        db.session.commit()
        flash('Сообщение удалено', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка: {str(e)}', 'danger')
    
    return redirect(url_for('admin.messages'))

# API для статистики (для графиков)
@admin_bp.route('/api/stats')
@login_required
@admin_required
def api_stats():
    # Заказы по дням за последние 30 дней
    thirty_days_ago = datetime.now() - timedelta(days=30)
    orders_by_day = db.session.query(
        db.func.date(Order.created_at).label('date'),
        db.func.count(Order.id).label('count'),
        db.func.sum(Order.final_price).label('revenue')
    ).filter(Order.created_at >= thirty_days_ago).group_by(
        db.func.date(Order.created_at)
    ).all()
    
    # Распределение пользователей по уровням
    users_by_level = db.session.query(
        User.loyalty_level,
        db.func.count(User.id)
    ).group_by(User.loyalty_level).all()
    
    return jsonify({
        'orders_by_day': [{'date': str(day.date), 'count': day.count, 'revenue': float(day.revenue or 0)} 
                         for day in orders_by_day],
        'users_by_level': [{'level': level, 'count': count} for level, count in users_by_level]
    })