# wb_parser
# WB Parser Project

## Описание

Этот проект — парсер товаров с Wildberries, реализованный на Django + DRF.  
Позволяет парсить товары по поисковому запросу или категории, сохранять их в базу данных, фильтровать и сортировать через API, а также строить графики по данным.

---

## Backend

- **Django 4.2+**
- **Django REST Framework**
- **django-filter** — фильтрация по цене, рейтингу, отзывам и запросу
- **django-cors-headers** — для работы с фронтендом
- **pandas, matplotlib** — для построения графиков (по желанию)

### Установка

1. Клонируй репозиторий:
    ```sh
    git clone <repo_url>
    cd wb_parser
    ```

2. Установи зависимости:
    ```sh
    pip install -r requirements.txt
    ```

3. Применить миграции:
    ```sh
    python manage.py migrate
    ```

4. Запусти сервер:
    ```sh
    python manage.py runserver
    ```

---

## API

- `POST /api/products/parse/` — парсинг товаров (передай `query` или `category_url` в JSON)
- `GET /api/products/` — список товаров с фильтрацией:
    - `min_price`, `max_price`
    - `min_rating`, `max_rating`
    - `min_reviews`, `max_reviews`
    - `request_query` — фильтр по названию запроса
- `GET /api/products/queries/` — список всех уникальных запросов

**Пример фильтрации:**
```
GET /api/products/?min_price=5000&min_rating=4&request_query=iphone
```

---





