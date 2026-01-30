from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from config import secret_key, algorithm
from service.user_service import get_user_by_username_db

# ВАЖНО: Эта настройка говорит Swagger UI, куда отправлять логин/пароль, чтобы получить токен.
# Мы скоро создадим этот адрес: /user/login
# tokenUrl="/user/login" значит, что Swagger будет стучаться по этому адресу, чтобы получить токен.
# Делаем auto_error=False, чтобы зависимость не выкидывала 401 раньше времени,
# если заголовок Authorization отсутствует.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login", auto_error=False)


def _credentials_exception():
    """Если токен невалидный или просрочен - выкидываем ошибку 401"""
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(request: Request, token: str = Depends(oauth2_scheme)):
    # 1. Сначала пробуем взять токен, который нашел Depends (в заголовке)
    # Если его нет - ищем в куках
    if not token:
        token = request.cookies.get("access_token")

    # Если и в куках нет - всё, ошибка, выгоняем
    if not token:
        raise _credentials_exception()

    # 2. Если токен начинается с "Bearer " (стандарт), отрезаем это слово
    if token.startswith("Bearer "):
        token = token.split(" ", 1)[1]

    try:
        # 3. Расшифровываем
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        # Достаем имя пользователя (в токене оно обычно под ключом "sub")
        username: str = payload.get("sub")

        if username is None:
            raise _credentials_exception()

        # Дополнительная проверка: не истек ли срок действия (поле 'exp')
        # jose.jwt обычно проверяет это сам, но можно и явно

    except JWTError:
        raise _credentials_exception()

    # 4. Ищем владельца токена в базе
    user = get_user_by_username_db(username)

    if user is None:
        raise _credentials_exception()

    return user
