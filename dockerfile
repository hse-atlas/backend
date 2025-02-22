FROM python:3.9-alpine

# Отключаем буферизацию вывода
ENV PYTHONUNBUFFERED=1

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл зависимостей и устанавливаем их
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Обновляем apk и устанавливаем netcat (в Alpine он называется netcat-openbsd)
RUN apk update && apk add --no-cache netcat-openbsd

RUN apk update && apk add --no-cache postgresql-client

# Копируем весь проект в рабочую директорию
COPY . .

# Даем права на выполнение entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Открываем порт 8000
EXPOSE 8000

# Задаем скрипт запуска
ENTRYPOINT ["/app/entrypoint.sh"]
