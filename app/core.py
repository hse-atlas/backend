from datetime import datetime, timedelta, timezone

from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select

from app.config import get_auth_data
from app.database import async_session_maker
from app.schemas import AdminsBase, UsersBase

context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def GetPasswordHash(password: str) -> str:
    return context.hash(password)


def VerifyPassword(input_data: str, hashed_data: str) -> bool:
    return context.verify(input_data, hashed_data)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=30)
    to_encode.update({"exp": expire})
    auth_data = get_auth_data()
    encode_jwt = jwt.encode(to_encode, auth_data['secret_key'], algorithm=auth_data['algorithm'])
    return encode_jwt


# ----------------------- Функции для администраторов -----------------------

async def find_one_or_none_admin(**filter_by):
    async with async_session_maker() as session:
        query = select(AdminsBase).filter_by(**filter_by)
        result = await session.execute(query)
        return result.scalar_one_or_none()


async def add_admin(**values):
    async with async_session_maker() as session:
        async with session.begin():
            new_instance = AdminsBase(**values)
            session.add(new_instance)
            try:
                await session.commit()
            except SQLAlchemyError as e:
                await session.rollback()
                raise e
            return new_instance


async def auth_admin(email: str, password: str):
    admin = await find_one_or_none_admin(email=email)
    if not admin or not VerifyPassword(password, admin.password):
        return None
    return admin


# ----------------------- Функции для пользователей -----------------------

async def find_one_or_none_user(**filter_by):
    async with async_session_maker() as session:
        query = select(UsersBase).filter_by(**filter_by)
        result = await session.execute(query)
        return result.scalar_one_or_none()


async def add_user(**values):
    async with async_session_maker() as session:
        async with session.begin():
            new_instance = UsersBase(**values)
            session.add(new_instance)
            try:
                await session.commit()
            except SQLAlchemyError as e:
                await session.rollback()
                raise e
            return new_instance


async def auth_user(email: str, password: str):
    user = await find_one_or_none_user(email=email)
    if not user or not VerifyPassword(password, user.password):
        return None
    return user
