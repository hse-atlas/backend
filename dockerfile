FROM python:3.9-slim

# Отключаем буферизацию вывода
ENV PYTHONUNBUFFERED=1

# Создаем файл /etc/apt/sources.list вручную
RUN echo "deb http://ftp.ru.debian.org/debian bookworm main" > /etc/apt/sources.list && \
    echo "deb http://ftp.ru.debian.org/debian bookworm-updates main" >> /etc/apt/sources.list && \
    echo "deb http://ftp.ru.debian.org/debian-security bookworm-security main" >> /etc/apt/sources.list

# Устанавливаем необходимые системные пакеты для сборки Python-зависимостей
RUN apt-get update -o Acquire::http::Timeout=60 && \
    apt-get install -y --no-install-recommends \
        gcc \
        libffi-dev \
        libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл зависимостей
COPY requirements.txt .

# Обновляем pip
RUN pip install --upgrade pip

# Устанавливаем базовые зависимости (FastAPI и Uvicorn)
RUN pip install --default-timeout=600 fastapi[all]
RUN pip install --default-timeout=600 uvicorn~=0.34.0

# Устанавливаем Pydantic с дополнительными зависимостями
RUN pip install --default-timeout=600 pydantic[email]~=2.9.2

# Устанавливаем SQLAlchemy с дополнительными зависимостями
RUN pip install --default-timeout=600 SQLAlchemy[all]~=2.0.37

# Устанавливаем requests (HTTP-библиотека)
RUN pip install --default-timeout=600 requests

# Устанавливаем asyncpg (асинхронный PostgreSQL драйвер)
RUN pip install --default-timeout=600 asyncpg

# Устанавливаем psycopg2-binary (синхронный PostgreSQL драйвер)
RUN pip install --default-timeout=600 psycopg2-binary

# Устанавливаем python-jose (JWT-библиотека)
RUN pip install --default-timeout=600 python-jose>=3.3.0

# Устанавливаем bcrypt (библиотека для хэширования паролей)
RUN pip install --default-timeout=600 bcrypt==4.0.1

# Устанавливаем passlib с поддержкой bcrypt
RUN pip install --default-timeout=600 passlib[bcrypt]~=1.7.4

# Устанавливаем pytest (для тестирования, если нужно)
RUN pip install --default-timeout=600 pytest

# Устанавливаем netcat
RUN apt-get install -y --no-install-recommends netcat && \
    rm -rf /var/lib/apt/lists/*

# Копируем весь проект
COPY . .

# Даем права на выполнение скрипта entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Открываем порт 8000
EXPOSE 8000

# Запускаем entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]