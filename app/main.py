from fastapi import FastAPI

from app.admin_auth import router as admin_auth_router
from app.database import test_db_connection
from app.project_CRUD import router as project_crud_router
from app.user_CRUD import router as user_crud_router
from app.user_auth import router as user_auth_router

app = FastAPI(title="API Gateway", debug=True)

app.include_router(admin_auth_router, prefix="/api/v1/AuthService")
app.include_router(user_auth_router, prefix="/api/v1/AuthService")
app.include_router(project_crud_router, prefix="/projects")
app.include_router(user_crud_router, prefix="/users")


@app.get("/")
async def root():
    return {"message": "API Gateway is working"}


@app.on_event("startup")
async def startup_event():
    await test_db_connection()
