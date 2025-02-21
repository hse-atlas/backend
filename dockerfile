FROM python:3.9-alpine

# Отключаем буферизацию вывода
ENV PYTHONUNBUFFERED=1

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем необходимые системные пакеты для сборки Python-зависимостей
RUN apk update && apk add --no-cache gcc musl-dev python3-dev libffi-dev openssl-dev cargo

# Обновляем pip и устанавливаем зависимости (увеличенный таймаут)
RUN pip install --upgrade pip && \
    pip install --default-timeout=300 -r requirements.txt

# Устанавливаем netcat (в Alpine: netcat-openbsd)
RUN apk add --no-cache netcat-openbsd

# Копируем весь проект
COPY . .

# Даем права на выполнение скрипта entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Открываем порт 8000
EXPOSE 8000

# Запускаем entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]
