#!/bin/sh
# Ожидание запуска базы данных (проверка, что база доступна)
echo "Ожидание запуска базы данных..."
while ! nc -z "$PASS_DB_HOST" "$PASS_DB_PORT"; do
  sleep 0.5
done
echo "База данных запущена!"

# Запуск создания таблиц (инициализация БД)
echo "Инициализация базы данных..."
python init_db.py

# Запуск приложения (например, через Uvicorn)
echo "Запуск приложения..."
exec uvicorn app.main:application --host 0.0.0.0 --port 8000
