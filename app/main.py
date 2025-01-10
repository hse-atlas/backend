from http import HTTPStatus
from fastapi import FastAPI, Response
from app.auth import router as auth_router


app = FastAPI()

@app.get("/")
def home_page():
    return {"message": "Auth Service Server alive"}

app.include_router(auth_router)
