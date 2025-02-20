from fastapi import APIRouter, HTTPException, status, Response

from app.core import find_one_or_none_admin, GetPasswordHash, add_admin, auth_admin, create_access_token
from app.schemas import RegisterData, LoginData

router = APIRouter(prefix='/api/v1/AuthService', tags=['Auth API'])


@router.post("/register/")
async def adminRegistration(admin_data: RegisterData) -> dict:
    adminEmail = await find_one_or_none_admin(email=admin_data.email)
    if adminEmail:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='E-mail already registered'
        )

    adminLogin = await find_one_or_none_admin(login=admin_data.login)
    if adminLogin:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Login already exists'
        )

    admin_dict = admin_data.dict()
    admin_dict['password'] = GetPasswordHash(admin_data.password)
    await add_admin(**admin_dict)
    return {'message': 'Registration completed!'}


@router.post("/login/")
async def adminAuth(response: Response, admin_data: LoginData):
    admin = await auth_admin(email=admin_data.email, password=admin_data.password)
    if admin is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid email or password'
        )

    access_token = create_access_token({"sub": str(admin.id)})
    response.set_cookie(key="admins_access_token", value=access_token, httponly=True)
    return {'access_token': access_token, 'refresh_token': None}
