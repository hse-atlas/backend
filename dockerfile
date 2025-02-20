FROM python:3.9-alpine

# Отключаем буферизацию вывода
ENV PYTHONUNBUFFERED=1

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл зависимостей и устанавливаем их
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Обновляем apk и устанавливаем netcat для проверки доступности базы данных
RUN apk update && apk add --no-cache netcat-openbsd

# Копируем все файлы проекта в контейнер
COPY . .

# Копируем и даем права на выполнение entrypoint.sh
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Открываем порт 8000
EXPOSE 8000

# Запускаем скрипт entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]
