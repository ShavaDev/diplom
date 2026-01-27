from datetime import datetime

from pydantic import BaseModel
from typing import List, Optional


class UserCreateSchema(BaseModel):
    fullname: str
    password: str
    username: str


class UserReadSchema(BaseModel):
    id: int
    fullname: str
    role: str
    username: str

    class Config:
        from_attributes = True  # Без этого FastAPI выдаст ошибку при возврате данных из БД


class OptionCreateSchema(BaseModel):
    option_text: str
    is_correct: bool


class QuestionCreateSchema(BaseModel):
    question_text: str
    options: List[OptionCreateSchema]  # Прямо тут создаем список вариантов


class TestCreateSchema(BaseModel):
    title: str
    timer: int  # в секундах
    questions: List[QuestionCreateSchema]  # А тут список вопросов


class OptionReadSchema(BaseModel):
    id: int
    option_text: str

    class Config:
        from_attributes = True  # Без этого FastAPI выдаст ошибку при возврате данных из БД


class QuestionReadSchema(BaseModel):
    id: int
    question_text: str
    options: List[OptionReadSchema]

    class Config:
        from_attributes = True  # Без этого FastAPI выдаст ошибку при возврате данных из БД


class TestReadSchema(BaseModel):
    id: int
    title: str
    timer: int  # в секундах
    questions: List[QuestionReadSchema]

    class Config:
        from_attributes = True  # Без этого FastAPI выдаст ошибку при возврате данных из БД


class AnswerSubmitSchema(BaseModel):
    question_id: int
    option_id: int


class TestSubmitSchema(BaseModel):
    test_id: int
    answers: List[AnswerSubmitSchema]


class AttemptReadSchema(BaseModel):
    id: int
    score: int
    completed: bool
    start_time: datetime
    end_time: Optional[datetime] # Позволяет полю быть пустым (None)
    author: UserReadSchema

    class Config:
        from_attributes = True  # Без этого FastAPI выдаст ошибку при возврате данных из БД
