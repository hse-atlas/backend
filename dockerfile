FROM python:3.13.1-alpine3.21

WORKDIR /authservice
COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app"]