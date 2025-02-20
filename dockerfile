FROM python:3.9-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Копирование файла зависимостей и установка зависимостей
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Установка netcat для проверки доступности базы данных
RUN apt-get update && apt-get install -y netcat && rm -rf /var/lib/apt/lists/*

# Копирование всего исходного кода
COPY . .

# Копирование скрипта entrypoint и выдача прав на выполнение
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

# Указываем entrypoint для контейнера
ENTRYPOINT ["/app/entrypoint.sh"]
