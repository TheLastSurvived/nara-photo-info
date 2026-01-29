from app import app
from models import Service
from models import db

with app.app_context():
    # Очистка базы
    Service.query.delete()
    
    # Услуги печати
    printing_services = [
        Service(
            title="Печать фотографий",
            category="printing",
            price_from="от 2 BYN",
            price_period="за штуку",
            price_value=2.0,
            image_url="images/services/usluga1.jpg",
            features="Стандартные форматы 10×15, 15×20;Матовая и глянцевая бумага;Высокое разрешение 300 dpi;Цветокоррекция при необходимости;Пакет от 10 шт - скидка 10%",
            description="Печать ваших фотографий на профессиональном оборудовании. Идеальная цветопередача, качественная бумага, быстрая обработка.",
            is_popular=True
        ),
        Service(
            title="Увеличение и постеры",
            category="printing",
            price_from="от 15 BYN",
            price_period="за формат А4",
            price_value=15.0,
            image_url="images/services/usluga2.jpg",
            features="Постеры для интерьера;Холсты на подрамнике;Печать на пластике;Ламинирование +5 BYN;Обрамление в багет",
            description="Создание больших форматов для украшения интерьера. Печать на холсте, пластике, бумаге премиум-класса.",
            is_popular=True
        ),
        Service(
            title="Фотокниги и альбомы",
            category="printing",
            price_from="от 50 BYN",
            price_period="за 10 разворотов",
            price_value=50.0,
            image_url="images/services/usluga3.jpg",
            features="Твердый переплет;Мелованная бумага;Дизайн макета;Различные размеры;Срок изготовления 3-5 дней",
            description="Создание профессиональных фотокниг и альбомов. Сохраните ваши воспоминания в красивой форме.",
            is_popular=False
        ),
        Service(
            title="Обработка и ретушь",
            category="printing",
            price_from="от 10 BYN",
            price_period="за одно фото",
            price_value=10.0,
            image_url="images/services/usluga4.jpg",
            features="Цветокоррекция;Ретушь кожи;Удаление дефектов;Подготовка к печати;Пакет от 10 фото - скидка 15%",
            description="Профессиональная обработка фотографий. Улучшение цвета, ретушь портретов, подготовка к печати.",
            is_popular=False
        ),
        Service(
            title="Фотосувениры",
            category="printing",
            price_from="от 12 BYN",
            price_period="за единицу",
            price_value=12.0,
            image_url="images/services/usluga5.jpg",
            features="Кружки с вашим фото;Футболки с принтом;Пазлы 500-1000 элементов;Магниты на холодильник;Брелоки с фото",
            description="Создание персонализированных сувениров с вашими фотографиями. Отличный подарок для близких.",
            is_popular=True
        ),
        Service(
            title="Срочная печать",
            category="printing",
            price_from="от 5 BYN",
            price_period="за фото за 1 час",
            price_value=5.0,
            image_url="images/services/usluga6.jpg",
            features="Печать за 1 час;Восстановление старых фото;Сканирование + ретушь;Цифровизация архивов;Срочный заказ +50% к стоимости",
            description="Экспресс-печать фотографий. Восстановление и оцифровка старых снимков, срочное выполнение заказов.",
            is_popular=False
        )
    ]
    
    # Пакеты фотосессий
    photo_sessions = [
        Service(
            title="Базовый",
            category="photo_session",
            price_from="100 BYN",
            price_period="за 1 час съемки",
            price_value=100.0,
            image_url="images/services/1.jpg",
            features="1 час съемки в студии;10 обработанных фото;1 образ;Помощь в позировании;cross:Визажист не включен;cross:Срочная обработка не включена",
            description="Идеальный пакет для первой фотосессии или портретных снимков. Базовая обработка, помощь фотографа.",
            is_popular=True
        ),
        Service(
            title="Стандартный",
            category="photo_session",
            price_from="300 BYN",
            price_period="за 2 часа съемки",
            price_value=300.0,
            image_url="images/services/2.jpg",
            features="2 часа съемки в студии;25 обработанных фото;2-3 образа;Помощь в позировании;Консультация визажиста;cross:Срочная обработка не включена",
            description="Съемка с возможностью смены образов. Консультация стилиста, больше фотографий на выходе.",
            is_popular=True
        ),
        Service(
            title="Премиум",
            category="photo_session",
            price_from="500 BYN",
            price_period="за 4 часа съемки",
            price_value=500.0,
            image_url="images/services/3.jpg",
            features="4 часа съемки в студии;50 обработанных фото;Неограниченное количество образов;Профессиональный визажист;Стилист-консультант;Срочная обработка за 24 часа",
            description="Полный пакет для профессиональной съемки. Визажист, стилист, неограниченное время и образы.",
            is_popular=False
        )
    ]
    
    # Специальные предложения
    special_offers = [
        Service(
            title="Портретная съемка",
            category="special_offers",
            price_from="150 BYN",
            price_period="за 1 час",
            price_value=150.0,
            image_url="images/services/portret.jpg",
            features="Индивидуальные портреты;Семейные фотографии;Профессиональный свет;2 образа;15 обработанных фото",
            description="Профессиональная портретная съемка в студии. Создание имиджевых фото для соцсетей, резюме, личного архива.",
            order_button_text="Подробнее",
            is_popular=True
        ),
        Service(
            title="Свадебная фотосъемка",
            category="special_offers",
            price_from="500 BYN",
            price_period="за 6 часов",
            price_value=500.0,
            image_url="images/services/svadba.jpg",
            features="Съемка церемонии;Love-story;Фото гостей;Предсвадебная съемка;100+ обработанных фото",
            description="Полное сопровождение вашего особенного дня. От подготовки до первого танца - запечатлим каждый момент.",
            order_button_text="Подробнее",
            is_popular=True
        ),
        Service(
            title="Детская фотосъемка",
            category="special_offers",
            price_from="100 BYN",
            price_period="за 1 час",
            price_value=100.0,
            image_url="images/services/kids.jpg",
            features="Съемка в игровой форме;Безопасная обстановка;Яркие реквизиты;Родители в кадре;20 обработанных фото",
            description="Веселая и непринужденная съемка для детей. Естественные эмоции, комфортная атмосфера, красивые снимки.",
            order_button_text="Подробнее",
            is_popular=True
        ),
        Service(
            title="Предметная съемка",
            category="special_offers",
            price_from="75 BYN",
            price_period="за 5 предметов",
            price_value=75.0,
            image_url="images/services/predmet.jpg",
            features="Фото для каталогов;Съемка на белом фоне;Обработка фона;Коррекция цвета;Подготовка для сайта",
            description="Профессиональная съемка товаров для интернет-магазинов и каталогов. Качественные фото, которые продают.",
            order_button_text="Подробнее",
            is_popular=False
        ),
        Service(
            title="Корпоративная съемка",
            category="special_offers",
            price_from="250 BYN",
            price_period="за 3 часа",
            price_value=250.0,
            image_url="images/services/korparat.jpg",
            features="Портреты сотрудников;Репортаж с мероприятия;Фото офиса;Для сайта компании;Быстрая обработка",
            description="Фото для бизнеса: сотрудники, мероприятия, офис. Профессиональные снимки для корпоративного сайта и соцсетей.",
            order_button_text="Подробнее",
            is_popular=False
        ),
        Service(
            title="Ретушь и обработка",
            category="special_offers",
            price_from="125 BYN",
            price_period="за 10 фото",
            price_value=125.0,
            image_url="images/services/retush.jpg",
            features="Глубокая ретушь;Цветокоррекция;Замена фона;Коллажи;Подготовка к печати",
            description="Профессиональная обработка уже готовых фотографий. Улучшение качества, исправление дефектов, художественная ретушь.",
            order_button_text="Подробнее",
            is_popular=False
        )
    ]
    
    # Добавляем все услуги
    for service in printing_services + photo_sessions + special_offers:
        db.session.add(service)
    
    db.session.commit()
    print("✅ База данных успешно заполнена!")
    print(f"📸 Услуги печати: {len(printing_services)}")
    print(f"📷 Пакеты фотосессий: {len(photo_sessions)}")
    print(f"🎁 Специальные предложения: {len(special_offers)}")