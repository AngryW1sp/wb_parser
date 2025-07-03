# WB Parser

## Описание

WB Parser — это Django REST API для парсинга и анализа товаров с Wildberries с поддержкой асинхронного запуска задач (Celery), фильтрации, автодокументации и построения графиков.

---

## Возможности

- Асинхронный парсинг товаров по поисковому запросу или категории (через Celery)
- Просмотр и фильтрация товаров по цене, рейтингу, количеству отзывов, запросу
- Кэширование списка товаров
- Автоматическая документация API (Swagger)
- Генерация графиков (гистограмма цен) на сервере
- Простая интеграция с фронтендом (HTML + Chart.js)

---

## Быстрый старт

### 1. Клонируйте репозиторий и установите зависимости

```sh
git clone <your_repo_url>
cd wb_parser
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2. Настройте базу данных и переменные окружения

- В файле `wb_parser/settings.py` укажите параметры вашей БД.
- Для Celery рекомендуется использовать Redis:
  ```
  CELERY_BROKER_URL = 'redis://localhost:6379/0'
  CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
  ```

### 3. Примените миграции и создайте суперпользователя

```sh
python manage.py migrate
python manage.py createsuperuser
```

### 4. Запустите Django сервер

```sh
python manage.py runserver
```

### 5. Запустите Celery воркер

```sh
celery -A wb_parser worker --loglevel=info --pool=solo
```

### 6. (Опционально) Запустите фронтенд

```sh
cd wb_parser
python -m http.server 8080
```
Откройте [http://localhost:8080/index.html](http://localhost:8080/index.html)

---

## Основные эндпоинты API

- `GET /api/products/` — список товаров с фильтрацией
- `POST /api/products/parse/` — запуск парсинга (body: `{"query": "...", "category_url": "...", "pages": 10}`)
- `GET /swagger/` — Swagger UI (автодокументация)

---

## Пример запроса на парсинг

```http
POST /api/products/parse/
Content-Type: application/json

{
  "query": "iphone 15",
  "pages": 5
}
```

---

## Пример фильтрации

```
GET /api/products/?min_price=10000&max_price=50000&min_rating=4&request_query=iphone
```

---

## Требования

- Python 3.9+
- Redis (для Celery)
- Django 4.x
- Celery 5.x

---


