FROM python:3.12-slim

WORKDIR /app

# Устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini .

# Запускаем миграции и сервер
CMD alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000
