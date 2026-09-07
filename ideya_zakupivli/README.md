# ІдеЯ у закупівлях — сайт на Django

Багатосторінковий сайт для юридичного консультування з питань публічних закупівель.
Реалізовано за узгодженою картою сайту: Головна, Замовникам (7 послуг), Учасникам (6 послуг),
Роз'яснення, Новини, Питання та відповіді (FAQ), Послуги та консультації, Про мене, Контакти.

Кольорова гамма: білий + відтінки синього (--blue-900…--blue-50) + відтінки жовтого
(--yellow-700…--yellow-100). Змінні визначені на самому початку `static/css/style.css` —
щоб змінити відтінки, достатньо відредагувати їх там.

## Структура проєкту

```
ideya_zakupivli/
├── manage.py
├── requirements.txt
├── config/            # settings, urls, wsgi/asgi
├── core/               # Головна, Про мене, Контакти-налаштування, підписка, seed-команда
├── content/             # Роз'яснення, Новини, FAQ, теги (Tag) — усе на одній моделі Article
├── services/            # Замовникам / Учасникам (Service) + Послуги та консультації (ConsultationService)
├── consultations/        # Форма звернення (ConsultationRequest) + сторінка "Дякуємо"
├── templates/            # HTML-шаблони
└── static/css/style.css   # уся кольорова гамма й верстка
```

## Як запустити локально

Знадобиться Python 3.10+ і встановлений Django (у цій пісочниці не було доступу в
інтернет, тож команди нижче потрібно виконати на вашій машині — сам код синтаксично
перевірено, але наживо на Django-сервері я його тут не запускав).

```bash
# 1. Створити та активувати віртуальне середовище
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Встановити залежності
pip install -r requirements.txt

# 3. Застосувати міграції
python manage.py makemigrations
python manage.py migrate

# 4. Створити адміністратора (для входу в /admin/)
python manage.py createsuperuser

# 5. Наповнити сайт демо-контентом (9 тем, 13 послуг, статті, FAQ, кейси)
python manage.py seed_content

# 6. Запустити сервер розробки
python manage.py runserver
```

Сайт відкриється на http://127.0.0.1:8000/, адмін-панель — на http://127.0.0.1:8000/admin/.

## Де і що редагувати контент

Весь текстовий контент керується через `/admin/` — окремо кодити нічого не треба:

- **Роз'яснення / Новини** — модель `Article` (поле `article_type` перемикає тип).
  Для роз'яснень заповнюйте 4 поля («Коротка відповідь», «Нормативна опора»,
  «Алгоритм дій», «Робоче формулювання») — вони автоматично зберуться в структуровану
  сторінку. Для новин достатньо поля «Текст новини».
- **Теми (теги)** — модель `Tag`, єдина для Роз'яснень, Новин і FAQ — саме вона керує
  фільтрами на цих трьох сторінках.
- **Послуги Замовникам / Учасникам** — модель `Service` (поле `audience`), кожен пункт —
  окрема сторінка з блоками «Що входить» / «Ризики» (кожен рядок тексту = один пункт списку).
- **Послуги та консультації (ціни)** — модель `ConsultationService`. Ціни навмисно не
  виводяться на сайт (рішення клієнта) — замість них показується `format_note`
  («Відповідь письмово, вартість — за запитом»).
- **FAQ** — модель `FAQItem`, з можливістю прив'язати до конкретного роз'яснення
  (`related_article`) і позначити як популярне (виводиться на Головній).
- **Про мене** — кейси в моделі `CaseStudy`, загальні тексти й досвід — у `SiteSettings`.
- **Контакти сайту** (телефон, email, Telegram, Viber, текст про формат консультацій,
  орієнтовний термін відповіді) — теж у `SiteSettings` (єдиний запис в адмінці).
- **Звернення з форми Контактів** потрапляють у модель `ConsultationRequest` — видно в
  адмінці, можна позначати опрацьованими.
- **Підписники на розсилку** (форма у футері) — модель `NewsletterSubscriber`.

## Публікація на PythonAnywhere

Нижче наведено готовий варіант для безкоштовного або платного Django Web app.
SQLite підходить для старту: файл бази залишайте в каталозі проєкту та регулярно
робіть його резервну копію.

### 1. Завантаження та virtualenv

У Bash-консолі PythonAnywhere:

```bash
cd ~
git clone YOUR_REPOSITORY_URL ideya_zakupivli
cd ~/ideya_zakupivli
python3.11 -m venv ~/.virtualenvs/ideya-zakupivli
source ~/.virtualenvs/ideya-zakupivli/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
python manage.py seed_content
```

Якщо проєкт завантажується через вкладку **Files**, його каталог має бути
`/home/ВАШ_USERNAME/ideya_zakupivli`, а `manage.py` має лежати безпосередньо
в ньому.

### 2. Web app та WSGI

Створіть **Web app** з ручною конфігурацією для Python 3.11. У полі **Virtualenv**
вкажіть `/home/ВАШ_USERNAME/.virtualenvs/ideya-zakupivli`.

Відкрийте WSGI-файл, який покаже PythonAnywhere, і замініть його вміст на цей код,
замінивши `ВАШ_USERNAME` та домен:

```python
import os
import sys

project_dir = '/home/ВАШ_USERNAME/ideya_zakupivli'
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
os.environ['DJANGO_SECRET_KEY'] = 'вставте-довгий-випадковий-секрет'
os.environ['DJANGO_DEBUG'] = 'False'
os.environ['DJANGO_ALLOWED_HOSTS'] = 'ВАШ_USERNAME.pythonanywhere.com'
os.environ['DJANGO_CSRF_TRUSTED_ORIGINS'] = 'https://ВАШ_USERNAME.pythonanywhere.com'

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
```

### 3. Static files

У вкладці **Web** додайте mappings:

| URL | Directory |
|---|---|
| `/static/` | `/home/ВАШ_USERNAME/ideya_zakupivli/staticfiles` |
| `/media/` | `/home/ВАШ_USERNAME/ideya_zakupivli/media` |

Після змін натисніть **Reload**. Сайт буде доступний за адресою
`https://ВАШ_USERNAME.pythonanywhere.com/`, адмінка — `/admin/`.

Після кожного оновлення коду виконуйте:

```bash
cd ~/ideya_zakupivli
source ~/.virtualenvs/ideya-zakupivli/bin/activate
git pull
python manage.py migrate
python manage.py collectstatic --noinput
```

Секретний ключ не додавайте в git. Перед публікацією також заповніть контакти
через `/admin/`; заявки з форми та підписники зберігатимуться у SQLite.
