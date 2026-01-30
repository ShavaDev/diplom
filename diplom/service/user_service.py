from security import hash_password
from database.models import User
from database.schemas import UserCreateSchema
from database.basa import session_db


# Регистрация пользователя
def create_user_db(user_data: UserCreateSchema):
    with session_db() as db:
        existing_user = db.query(User).filter(User.username == user_data.username).first()
        if not existing_user:
            password = hash_password(user_data.password)
            new_user = User(fullname=user_data.fullname,
                            password=password,
                            username=user_data.username)
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            return new_user
        return None


# Получение пользователя по логину (нужно для входа)
def get_user_by_username_db(username: str):
    with session_db() as db:
        user = db.query(User).filter(User.username == username).first()
        return user


# удаление пользователя (к примеру его давно не было)
def delete_user_db(user_id: int):
    with session_db() as db:
        user = db.query(User).filter(User.id == user_id).first()
        db.delete(user)
        db.commit()
        return True


def change_role_to_teacher_db(user_id: int):
    with session_db() as db:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        new_role = "teacher"
        user.role = new_role
        db.commit()
        db.refresh(user)
        return user
