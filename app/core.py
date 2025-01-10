from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta, timezone
from app.config import get_auth_data
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from app.database import async_session_maker
from app.schemas import UsersBase

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

async def find_one_or_none(**filter_by):
    async with async_session_maker() as session:
        query = select(UsersBase).filter_by(**filter_by)
        result = await session.execute(query)
        return result.scalar_one_or_none()

async def add(**values):
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
    user = find_one_or_none(email=email)
    if not user or not VerifyPassword(password, user.password):
        return None
    return user