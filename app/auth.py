from fastapi import APIRouter, HTTPException, status, Response
from sqlalchemy import select 
from app.database import async_session_maker
from app.core import find_one_or_none, GetPasswordHash, add, auth_user, create_access_token
from app.schemas import UserRegisterData, UserLoginData

router = APIRouter(prefix='/api/v1/AuthService', tags=['Auth API'])


@router.post("/register/")
async def userRegistration(user_data: UserRegisterData) -> dict:
    userEmail = await find_one_or_none(email=user_data.email)
    if userEmail:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='E-mail already registered'
        )

    userLogin = await find_one_or_none(login=user_data.login)
    if userLogin:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Login already exists'
        )

    user_dict = user_data.dict()
    user_dict['password'] = GetPasswordHash(user_data.password)
    await add(**user_dict)
    return {'message': 'Registration completed!'}

@router.post("/login/")
async def userAuth(response: Response, user_data: UserLoginData):
    user = await auth_user(email=user_data.email, password=user_data.password)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Invalid email or password')

    access_token = create_access_token({"sub": str(user.id)})
    response.set_cookie(key="users_access_token", value=access_token, httponly=True)
    return {'access_token': access_token, 'refresh_token': None}