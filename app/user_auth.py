from fastapi import APIRouter, HTTPException, status, Response
from sqlalchemy.exc import SQLAlchemyError

# Импортируем необходимые функции и схемы из уже существующих модулей
from app.core import find_one_or_none_user, GetPasswordHash, add_user, auth_user, create_access_token
from app.schemas import RegisterData, LoginData

# Использование асинхронной сессии из database.py
# (в данном случае функции find_one_or_none и add уже работают через async_session_maker)

router = APIRouter(prefix="/api/v1/AuthService", tags=["Auth API"])


@router.post("/user_register/{project_id}")
async def user_register(project_id: int, user_data: RegisterData) -> dict:
    """
    Регистрация пользователя в рамках проекта с id=project_id.
    Проверяется уникальность email и login с учётом проекта.
    """
    # Проверяем, что нет пользователя с таким email в рамках указанного проекта
    existing_user_email = await find_one_or_none_user(email=user_data.email, project_id=project_id)
    if existing_user_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="E-mail already registered"
        )

    # Проверяем, что нет пользователя с таким login в рамках указанного проекта
    existing_user_login = await find_one_or_none_user(login=user_data.login, project_id=project_id)
    if existing_user_login:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Login already exists"
        )

    # Хэшируем пароль и готовим данные для создания пользователя
    user_dict = user_data.dict()
    user_dict["password"] = GetPasswordHash(user_data.password)
    user_dict["project_id"] = project_id  # Добавляем привязку к проекту

    try:
        await add_user(**user_dict)
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User registration failed"
        )

    return {"message": "User registration completed!"}


@router.post("/user_login/{project_id}")
async def user_login(project_id: int, user_data: LoginData, response: Response) -> dict:
    """
    Авторизация пользователя в рамках проекта с id=project_id.
    Если пользователь найден, пароль верный и он привязан к данному проекту,
    возвращается JWT-токен.
    """
    user = await auth_user(email=user_data.email, password=user_data.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if getattr(user, "project_id", None) != project_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not associated with the specified project"
        )

    access_token = create_access_token({"sub": str(user.id)})
    response.set_cookie(key="users_access_token", value=access_token, httponly=True)

    return {"access_token": access_token, "refresh_token": None}
