from fastapi import APIRouter, Request
from service.user_service import *
from database.schemas import UserCreateSchema
from database.models import User
from fastapi.security import OAuth2PasswordRequestForm
from security import create_access_token, verify_password
from fastapi import Depends, HTTPException, status, Response
from deps import get_current_user
from limiter_config import limiter

user_router = APIRouter(prefix="/user", tags=["User API"])


@user_router.post("/register")
@limiter.limit("3/minute")
async def create_user_api(request: Request,
                          user_data: UserCreateSchema):
    result = create_user_db(user_data=user_data)
    if result:
        return "User created successfully"
    raise HTTPException(status_code=400, detail="User already exists")


@user_router.post("/login")
@limiter.limit("5/minute")
async def login_user_api(request: Request,
                         response: Response, form_data: OAuth2PasswordRequestForm = Depends()):
    # 1. Ищем пользователя
    current_user = get_user_by_username_db(username=form_data.username)
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    # 2. Проверяем пароль
    if verify_password(form_data.password, current_user.password) == False:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    # 3. Генерируем токен
    access_token = create_access_token(data={"sub": current_user.username})
    # 4. Устанавливаем куки (просто вызываем метод)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}",
                        httponly=True,
                        samesite="lax", # Помогает с передачей кук на localhost
                        secure=False, # Для локальной разработки без HTTPS ставим False
                        path="/") # Чтобы кука была видна во всем приложении

    # 5. Возвращаем JSON для Swagger и фронтенда
    return {"access_token": access_token, "token_type": "bearer"}


@user_router.delete("/delete_user")
async def delete_user_api(user_id: int,
                          current_user: User = Depends(get_current_user)):
    # Теперь current_user — это реально объект User, если токен прошел проверку
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action"
        )
    result = delete_user_db(user_id=user_id)
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted"}


@user_router.post("/change_role")
async def change_user_api(user_id: int,
                          current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action"
        )
    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="Вы не можете менять роль самому себе")

    result = change_role_to_teacher_db(user_id=user_id)
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User changed"}


@user_router.post("/logout")
async def logout_user_api(response: Response):
    response.delete_cookie("access_token", httponly=True)
    return {"message": "User logged out"}


@user_router.get("/me")
async def get_user_me(current_user: User = Depends(get_current_user)):
    return current_user
