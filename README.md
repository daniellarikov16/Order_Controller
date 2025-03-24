# Order Management System

Система управления заказами с аутентификацией пользователей и обработкой заказов.

## 🚀 Основные функции

- ✅ Регистрация и авторизация пользователей
- ➕ Создание новых заказов
- 📋 Просмотр заказов (в обработке и завершенных)
- ✔️ Отметка заказов как выполненных
- 🗑️ Удаление выполненных заказов

## 🛠 Технологии

- **Backend**: FastAPI (Python 3.9+)
- **Frontend**: HTML5, CSS3, Jinja2
- **Database**: SQLite (SQLAlchemy ORM)
- **Authentication**: Bcrypt хеширование паролей

## 📦 Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/ваш-репозиторий.git
cd order-management-system
```
2. Установите зависимости:
```bash
pip install -r requirements.txt
```
3. Запустите приложение:
```bash
uvicorn main:app --reload
```

## 📂 Структура проекта

```
├── static/
│   └── styles.css          # Стили приложения
├── templates/
│   ├── create_order.html   # Форма создания заказа
│   ├── login.html          # Страница входа
│   ├── my_orders.html      # Список заказов
│   ├── personal_account.html # Личный кабинет
│   └── register.html       # Страница регистрации
├── services/
│   ├── order_service.py    # Логика работы с заказами
│   └── user_service.py     # Логика работы с пользователями
├── models.py              # Модели базы данных
├── database.py            # Настройки подключения к БД
├── auth.py                # Аутентификация
├── main.py                # Основное приложение
└── README.md              # Этот файл
```

## 🔐 Аутентификация

- Регистрация: /register
- Вход: /login
- Выход: /logout

## 📊 Работа с заказами
- create_order	        GET/POST	   Создание нового заказа
- pending_orders	      GET	         Заказыв обработке
- processed_orders	    GET	         Завершенные заказы
- perform	              GET	         Завершить заказ
- delete_processed	    GET	         Удалить выполненные заказы



