from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import jwt
from config import secret_key, algorithm, access_token_expire_minutes

# Настройка хеширования
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# 2. Функции для паролей
def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(plain_password: str):
    return pwd_context.hash(plain_password)


# 3. Функция создания токена
def create_access_token(data: dict):
    # 1. Берем данные (например, {"sub": "student_vasya"})
    to_encode = data.copy()

    # 2. Вычисляем время смерти токена (сейчас + 30 минут)
    expire = datetime.now(timezone.utc) + timedelta(minutes=access_token_expire_minutes)

    # 3. Вписываем время смерти прямо в данные
    to_encode.update({"exp": expire})

    # 4. Самое главное: ЗАПЕЧАТЫВАЕМ
    # Мы берем данные и смешиваем их с СЕКРЕТНЫМ КЛЮЧОМ.
    # На выходе получается длинная строка "eyJhbGciOiJIUzI1Ni..."
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)

    return encoded_jwt  # Отдаем эту строку пользователю
