from fastapi import FastAPI, Depends, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from starlette.middleware.sessions import SessionMiddleware
import logging

from app.admin_auth import router as admin_auth_router
from app.database import test_db_connection
from app.project_CRUD import router as project_crud_router
from app.user_CRUD import router as user_crud_router
from app.user_auth import router as user_auth_router
from app.user_roles import router as user_roles_router #роли
from app.oauth import router as oauth_router
from app.security import security_config
from app.jwt_auth import auth_middleware, get_async_session

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("app.log")
    ]
)
logger = logging.getLogger(__name__)

# Создаем лимитер для защиты от DDoS атак
limiter = Limiter(key_func=get_remote_address)

# Создаем приложение FastAPI
application = FastAPI(
    title="Atlas Auth Service",
    description="Микросервис для управления аутентификацией пользователей",
    version="1.0.0",
    debug=False  # В продакшене лучше выключить режим отладки
)

# Middleware для обработки сессий (для OAuth)
application.add_middleware(
    SessionMiddleware,
    secret_key=security_config.SESSION_SECRET_KEY,
    max_age=1800  # 30 минут
)

# Middleware для CORS
application.add_middleware(
    CORSMiddleware,
    allow_origins=security_config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware для ограничения запросов
application.add_middleware(SlowAPIMiddleware)

# Применение rate limiter к приложению
application.state.limiter = limiter


# Обработчик ошибок для превышения лимита запросов
@application.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request, exc):
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests. Please try again later."}
    )


# Middleware для установки токенов в ответы
@application.middleware("http")
async def token_middleware(request: Request, call_next):
    # Запуск эндпоинта
    response = await call_next(request)

    # Если в request.state есть новые токены, добавляем их в ответ
    if hasattr(request.state, "new_access_token"):
        response.set_cookie(
            key=(
                "admins_access_token"
                if request.state.user_type == "admin"
                else "users_access_token"
            ),
            value=request.state.new_access_token,
            httponly=True,
            secure=True,
            samesite="strict"
        )

    if hasattr(request.state, "new_refresh_token"):
        response.set_cookie(
            key=(
                "admins_refresh_token"
                if request.state.user_type == "admin"
                else "users_refresh_token"
            ),
            value=request.state.new_refresh_token,
            httponly=True,
            secure=True,
            samesite="strict"
        )

    return response


# Middleware для аутентификации по токенам
@application.middleware("http")
async def auth_middleware_wrapper(request: Request, call_next):
    db = get_async_session()
    async for session in db:
        try:
            await auth_middleware(request, session)
        except Exception as e:
            # Логируем ошибку, но не прерываем запрос для публичных маршрутов
            logger.error(f"Auth middleware error: {str(e)}")

    return await call_next(request)


# Подключаем роутеры
application.include_router(admin_auth_router, prefix="/api/v1/AuthService")
application.include_router(user_auth_router, prefix="/api/v1/AuthService")
application.include_router(project_crud_router, prefix="/projects")
application.include_router(user_crud_router, prefix="/users")
application.include_router(oauth_router, prefix="/api/v1/AuthService")
application.include_router(user_roles_router) #роли


# Корневой эндпоинт
@application.get("/")
@limiter.limit("10/minute")
async def root(request: Request):
    return {"message": "Atlas Auth Service is working"}


# Информация о здоровье сервиса
@application.get("/health")
async def health():
    return {"status": "healthy"}


# События при запуске и остановке приложения
@application.on_event("startup")
async def startup_event():
    # Тестируем подключение к базе данных
    await test_db_connection()

    # Добавляем информацию о запуске в логи
    logger.info("Atlas Auth Service started successfully")


@application.on_event("shutdown")
async def shutdown_event():
    # Логируем остановку сервиса
    logger.info("Atlas Auth Service shutdown")