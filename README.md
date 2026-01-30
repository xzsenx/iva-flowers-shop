# Ива - Цветочная студия

Полнофункциональный интернет-магазин цветов с админ-панелью.

## Возможности

### Для клиентов:
- Просмотр каталога цветов
- Фильтрация по категориям, цветам, характеристикам
- Добавление товаров в корзину
- Оформление заказов

### Для администратора:
- Добавление/удаление товаров
- Просмотр заказов
- Управление ассортиментом

## Установка локально

```bash
# Установить зависимости
pip install -r requirements.txt

# Запустить приложение
python app.py
```

Приложение будет доступно по адресу: `http://localhost:5000`
Админ-панель: `http://localhost:5000/admin`

## Деплой на Render

1. Загрузите все файлы в GitHub репозиторий
2. Создайте новый Web Service на Render
3. Подключите GitHub репозиторий
4. Настройки:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python app.py`

## Структура файлов

- `app.py` - Flask backend с API
- `index.html` - Frontend интерфейс магазина
- `logo.png` - Логотип
- `requirements.txt` - Python зависимости
- `flowers.db` - SQLite база данных (создаётся автоматически)

## API Endpoints

- `GET /api/products` - Получить список товаров
- `POST /api/products` - Добавить товар
- `PUT /api/products/<id>` - Обновить товар
- `DELETE /api/products/<id>` - Удалить товар
- `GET /api/orders` - Получить список заказов
- `POST /api/orders` - Создать заказ
