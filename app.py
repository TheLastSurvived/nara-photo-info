from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import (
    LoginManager,
    login_user,
    login_required,
    logout_user,
    current_user,
)
from sqlalchemy import or_, desc
from config import Config
from models import db, User, Service, Messages, Review, Order
import os
from datetime import datetime, date
import uuid
from werkzeug.exceptions import HTTPException
from admin import admin_bp

app = Flask(__name__)
app.config.from_object(Config)
app.register_blueprint(admin_bp)

# Инициализация расширений
db.init_app(app)

# Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = (
    "Пожалуйста, войдите в систему для доступа к этой странице."
)
login_manager.login_message_category = "warning"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)


@app.context_processor
def utility_processor():
    return {'datetime': datetime}

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form.get("name")
        surname = request.form.get("surname")
        message = request.form.get("message")
        message = Messages(
            name=name,
            surname=surname,
            message=message,
        )

        db.session.add(message)
        db.session.commit()
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/price")
def price():
    # Получаем параметры фильтрации из URL
    category_filter = request.args.get("category", "all")
    sort_by = request.args.get("sort", "default")
    min_price = request.args.get("min_price")
    max_price = request.args.get("max_price")
    search_query = request.args.get("search", "").strip()

    # Базовый запрос
    query = Service.query

    # Поиск по названию и описанию
    if search_query:
        search = f"%{search_query}%"
        query = query.filter(
            or_(
                Service.title.ilike(search),
                Service.description.ilike(search),
                Service.features.ilike(search),
            )
        )

    # Фильтрация по категории
    if category_filter != "all":
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
    if sort_by == "price_asc":
        query = query.order_by(Service.price_value.asc())
    elif sort_by == "price_desc":
        query = query.order_by(Service.price_value.desc())
    elif sort_by == "title":
        query = query.order_by(Service.title.asc())
    elif sort_by == "popular":
        query = query.filter_by(is_popular=True).order_by(Service.created_at.desc())
    else:
        query = query.order_by(Service.category, Service.created_at.desc())

    services = query.all()

    # Группируем услуги по категориям для якорей
    printing_services = [s for s in services if s.category == "printing"]
    photo_session_packages = [s for s in services if s.category == "photo_session"]
    special_offers = [s for s in services if s.category == "special_offers"]

    # Получаем уникальные категории для фильтра
    categories = db.session.query(Service.category).distinct().all()
    categories = [c[0] for c in categories]

    return render_template(
        "price.html",
        services=services,
        printing_services=printing_services,
        photo_session_packages=photo_session_packages,
        special_offers=special_offers,
        categories=categories,
        current_category=category_filter,
        current_sort=sort_by,
        search_query=search_query,
    )


@app.route("/portfolio")
def portfolio():
    return render_template("portfolio.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password")
        remember = request.form.get("remember") == "on"

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            if user.is_active:
                login_user(user, remember=remember)
                flash("Вы успешно вошли в систему!", "success")

                # Перенаправление на страницу, с которой пришли
                next_page = request.args.get("next")
                return redirect(next_page or url_for("index"))
            else:
                flash("Ваш аккаунт заблокирован", "error")
        else:
            flash("Неверный email или пароль", "error")
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    if request.method == "POST":
        # Получаем данные из формы
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        # Валидация
        errors = []

        if not email:
            errors.append("Email обязателен")
        if not password:
            errors.append("Пароль обязателен")

        if len(password) < 6:
            errors.append("Пароль должен быть не менее 6 символов")

        # Проверка совпадения паролей
        if password != confirm_password:
            errors.append("Пароли не совпадают")

        if User.query.filter_by(email=email).first():
            errors.append("Email уже используется")

        # Если есть ошибки, показываем их
        if errors:
            for error in errors:
                flash(error, "error")
            return render_template(
                "register.html",
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
            )

        # Создание пользователя
        try:
            user = User(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
            )
            user.set_password(password)

            db.session.add(user)
            db.session.commit()

            flash("Регистрация успешна! Теперь вы можете войти в систему.", "success")
            return redirect(url_for("login"))

        except Exception as e:
            db.session.rollback()
            flash(f"Произошла ошибка при регистрации: {str(e)}", "error")

    # GET запрос - просто показываем форму
    return render_template("register.html")


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        # Обновление профиля
        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        phone = request.form.get("phone", "").strip()

        try:
            current_user.first_name = first_name
            current_user.last_name = last_name
            current_user.phone = phone

            db.session.commit()
            flash("Профиль успешно обновлен!", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Ошибка при обновлении профиля: {str(e)}", "error")

        return redirect(url_for("profile"))

    # GET запрос - показываем профиль с заказами
    orders = (
        Order.query.filter_by(user_id=current_user.id)
        .order_by(Order.created_at.desc())
        .all()
    )

    return render_template("profile.html", orders=orders)


@app.route("/order/create/<int:service_id>", methods=["GET", "POST"])
@login_required
def create_order(service_id):
    service = Service.query.get_or_404(service_id)

    # Проверяем, не заказывал ли уже пользователь эту услугу
    existing_order = Order.query.filter_by(
        user_id=current_user.id, service_id=service_id, status="pending"
    ).first()

    if existing_order:
        flash("Вы уже заказали эту услугу!", "info")
        return redirect(url_for("profile"))

    if request.method == "POST":
        use_points = request.form.get("use_points") == "on"
        points_to_use = 0

        # Рассчитываем скидку
        original_price = service.price_value if service.price_value else 0
        discount_percent = current_user.get_discount_percent()

        # Проверяем использование баллов
        if use_points and current_user.can_use_points():
            # Максимум 50% стоимости можно оплатить баллами
            max_points_value = original_price * 0.5
            points_to_use = min(current_user.loyalty_points, int(max_points_value))

        # Рассчитываем итоговую цену
        discount_amount = original_price * (discount_percent / 100)
        points_discount = points_to_use  # 1 балл = 1 единица валюты
        final_price = max(0, original_price - discount_amount - points_discount)

        try:
            # Создаем заказ
            order = Order(
                service_id=service_id,
                user_id=current_user.id,
                original_price=original_price,
                discount_percent=discount_percent,
                points_used=points_to_use,
                final_price=final_price,
                status="pending",
            )

            db.session.add(order)

            # Обновляем баллы пользователя
            if points_to_use > 0:
                current_user.loyalty_points -= points_to_use

            db.session.commit()

            flash(
                f'Услуга "{service.title}" успешно заказана за {final_price:.2f} BYN! (скидка {discount_percent}% + использовано {points_to_use} баллов)',
                "success",
            )

        except Exception as e:
            db.session.rollback()
            flash(f"Ошибка при создании заказа: {str(e)}", "error")

        return redirect(url_for("profile"))

    # GET запрос - показываем форму с расчетом
    original_price = service.price_value if service.price_value else 0
    discount_percent = current_user.get_discount_percent()
    discount_amount = original_price * (discount_percent / 100)
    price_with_discount = original_price - discount_amount

    return render_template(
        "create_order.html",
        service=service,
        original_price=original_price,
        discount_percent=discount_percent,
        discount_amount=discount_amount,
        price_with_discount=price_with_discount,
    )


@app.route("/order/cancel/<int:order_id>")
@login_required
def cancel_order(order_id):
    order = Order.query.get_or_404(order_id)

    # Проверяем, что пользователь отменяет свой заказ
    if order.user_id != current_user.id:
        flash("Вы не можете отменить этот заказ", "error")
        return redirect(url_for("profile"))

    if order.status != "pending":
        flash("Нельзя отменить этот заказ", "info")
        return redirect(url_for("profile"))

    try:
        order.status = "cancelled"
        db.session.commit()
        flash("Заказ успешно отменен", "info")

    except Exception as e:
        db.session.rollback()
        flash(f"Ошибка при отмене заказа: {str(e)}", "error")

    return redirect(url_for("profile"))


@app.route("/service/<int:service_id>")
def service_detail(service_id):
    service = Service.query.get_or_404(service_id)

    # Получаем отзывы для этой услуги
    reviews = (
        Review.query.filter_by(service_id=service_id)
        .order_by(desc(Review.created_at))
        .all()
    )

    return render_template("service_detail.html", service=service, reviews=reviews)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Вы вышли из системы", "info")
    return redirect(url_for("index"))


@app.route('/service/<int:service_id>/add_review', methods=['POST'])
@login_required
def add_review(service_id):
    service = Service.query.get_or_404(service_id)
    
    content = request.form.get('content', '').strip()
    rating = request.form.get('rating', type=int)
    
    # Валидация
    if not content or len(content) < 10:
        flash('Отзыв должен содержать минимум 10 символов', 'error')
        return redirect(url_for('service_detail', service_id=service_id))
    
    if not rating or rating < 1 or rating > 5:
        flash('Пожалуйста, поставьте оценку от 1 до 5 звёзд', 'error')
        return redirect(url_for('service_detail', service_id=service_id))
    
    try:
        # Проверяем, оставлял ли пользователь уже отзыв
        existing_review = Review.query.filter_by(
            user_id=current_user.id,
            service_id=service_id
        ).first()
        
        if existing_review:
            flash('Вы уже оставляли отзыв на эту услугу', 'info')
            return redirect(url_for('service_detail', service_id=service_id))
        
        # Создаем новый отзыв с рейтингом
        review = Review(
            content=content,
            rating=rating,
            user_id=current_user.id,
            service_id=service_id
        )
        
        db.session.add(review)
        
        # Начисляем 50 баллов за отзыв
        current_user.loyalty_points += 50
        db.session.commit()
        
        # Определяем текстовое описание оценки
        rating_text = {5: 'отлично', 4: 'хорошо', 3: 'удовлетворительно', 2: 'плохо', 1: 'ужасно'}
        flash(f'Спасибо за ваш отзыв! Вы оценили услугу на {rating}★ ({rating_text.get(rating, "")}) и получили +50 баллов!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Произошла ошибка при сохранении отзыва: {str(e)}', 'error')
    
    return redirect(url_for('service_detail', service_id=service_id))


@app.route("/review/<int:review_id>/delete", methods=["POST"])
@login_required
def delete_review(review_id):
    review = Review.query.get_or_404(review_id)

    # Проверяем, что пользователь удаляет свой отзыв
    if review.user_id != current_user.id and not current_user.is_admin:
        flash("Вы не можете удалить этот отзыв", "error")
        return redirect(url_for("service_detail", service_id=review.service_id))

    service_id = review.service_id
    db.session.delete(review)
    db.session.commit()

    flash("Отзыв успешно удален", "success")
    return redirect(request.referrer or url_for('index'))


@app.route('/order/complete/<int:order_id>')
@login_required
def complete_order(order_id):
    # Только администратор может завершать заказы
    if not current_user.is_admin:
        flash('У вас нет прав для этого действия', 'error')
        return redirect(url_for('profile'))
    
    order = Order.query.get_or_404(order_id)
    
    if order.status == 'pending':
        try:
            order.status = 'completed'
            
            # Начисляем баллы пользователю
            user = order.user
            user.update_loyalty(order.final_price)  # используем final_price для начисления
            
            # Бонус за первый заказ
            if len(user.orders.filter_by(status='completed').all()) == 1:
                user.loyalty_points += 100
                flash('+100 баллов за первый заказ!', 'success')
            
            db.session.commit()
            flash(f'Заказ №{order.id} завершен. Пользователю начислено {int(order.final_price)} баллов.', 'success')
            
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка: {str(e)}', 'error')
    
    return redirect(url_for('admin_panel'))  # нужна админская панель


@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500

@app.errorhandler(403)
def forbidden(e):
    return render_template('errors/403.html'), 403

@app.errorhandler(400)
def bad_request(e):
    return render_template('errors/400.html'), 400

@app.errorhandler(401)
def unauthorized(e):
    return redirect(url_for('login'))  # Перенаправляем на страницу входа


# Обработчик для всех остальных ошибок
@app.errorhandler(Exception)
def handle_exception(e):
    # Если это HTTP ошибка, используем её код
    if isinstance(e, HTTPException):
        return e
    
    # Для всех остальных ошибок возвращаем 500
    return render_template('errors/500.html'), 500


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)
