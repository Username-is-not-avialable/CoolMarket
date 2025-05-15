## 🚀 Запуск проекта

### Предварительные требования
- Python 3.10+
- PostgreSQL 13+
- Установленный `pip` и `virtualenv`

### 1. Установка зависимостей
```bash
git clone https://github.com/Username-is-not-avialable/CoolMarket.git
cd market

# Создание виртуального окружения (Linux/macOS)
python -m venv venv
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt
```
### 2. Настройка окружения

#### 1. Создайте файл .env в корне проекта со следующим содержимым:

```ini
DB_USER=market_user
DB_PASSWORD=your_password
```

#### 2. Настройте подключение к БД в PostgreSQL:
```bash
sudo -u postgres psql -c "CREATE DATABASE market;"
sudo -u postgres psql -c "CREATE USER market_user WITH PASSWORD 'your_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE market TO market_user;"
```

### 3. Запуск сервера:
```bash
uvicorn main:app --reload
```

### После запуска будут доступны:

- Интерактивная документация: http://localhost:8000/docs

- Альтернативная документация: http://localhost:8000/redoc
