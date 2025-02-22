#!/bin/sh
# Ожидание запуска базы данных (проверка, что база доступна)
echo "Ожидание запуска базы данных..."
while ! pg_isready -h "$PASS_DB_HOST" -p "$PASS_DB_PORT" -U "$PASS_DB_USER"; do
  sleep 0.5
done
echo "База данных запущена!"

# Запуск создания таблиц (инициализация БД)
echo "Инициализация базы данных..."
python init_db.py

# Запуск приложения (например, через Uvicorn)
echo "Запуск приложения..."
exec uvicorn app.main:application --host 0.0.0.0 --port 8000
