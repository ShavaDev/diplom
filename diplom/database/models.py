from database.basa import Base
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import String, ForeignKey
from typing import List
from datetime import datetime
from sqlalchemy.sql import func


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    fullname: Mapped[str] = mapped_column(String(length=64), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(length=16), nullable=False, default="student")
    password: Mapped[str] = mapped_column(String(length=256), nullable=False)
    username: Mapped[str] = mapped_column(String(length=16), nullable=False, index=True, unique=True)

    # обратная связь с Test
    tests: Mapped[List['Test']] = relationship("Test", back_populates="author",
                                               passive_deletes=True)

    # обратная связь с Attempt
    attempts: Mapped[List['Attempt']] = relationship("Attempt", back_populates="author", passive_deletes=True)


class Test(Base):
    __tablename__ = "tests"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    title: Mapped[str] = mapped_column(String(length=64), nullable=False)
    timer: Mapped[int] = mapped_column(nullable=False, default=3600)  # в секундах

    # связь с колонкой айди в таблице User
    author_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete="CASCADE"))

    # устанавливаем связь с User
    author: Mapped['User'] = relationship("User", back_populates="tests", lazy="selectin")

    # связываем с Question
    questions: Mapped[List['Question']] = relationship("Question", back_populates="test",
                                                       passive_deletes=True)

    # обратная связь с Attempt
    attempts: Mapped['Attempt'] = relationship("Attempt", back_populates="test", passive_deletes=True)


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    question_text: Mapped[str] = mapped_column(String(length=128), nullable=False)

    # к какому тесту принадлежит (к какому предмету)
    test_id: Mapped[int] = mapped_column(ForeignKey('tests.id', ondelete="CASCADE", onupdate="CASCADE"))

    # устанавливаем связь с Test
    test: Mapped['Test'] = relationship("Test", back_populates="questions", lazy="selectin")

    # устанавливаем связь с Option
    options: Mapped[List['Option']] = relationship("Option", back_populates="question", passive_deletes=True)


class Option(Base):
    __tablename__ = "options"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    option_text: Mapped[str] = mapped_column(String(length=128), nullable=False)

    is_correct: Mapped[bool] = mapped_column(default=False, nullable=False)

    # к какому вопросу принадлежит
    question_id: Mapped[int] = mapped_column(ForeignKey('questions.id', ondelete="CASCADE", onupdate="CASCADE"))

    # устанавливаем связь с Question
    question: Mapped['Question'] = relationship("Question", back_populates="options", lazy="selectin")


class Attempt(Base):
    __tablename__ = "attempts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # итоговый балл
    score: Mapped[int] = mapped_column(default=0, nullable=False)

    start_time: Mapped[datetime] = mapped_column(server_default=func.now())
    end_time: Mapped[datetime] = mapped_column(nullable=True)

    # Завершил ли студент тестирование
    completed: Mapped[bool] = mapped_column(default=False, nullable=False)

    # какой пользователь
    author_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete="CASCADE"))

    # какой тест прошел пользователь
    test_id: Mapped[int] = mapped_column(ForeignKey('tests.id', ondelete="CASCADE"))

    # связываем пользователя с User
    author: Mapped['User'] = relationship("User", back_populates="attempts", lazy="selectin")

    # связываем тест с Test
    test: Mapped['Test'] = relationship("Test", back_populates="attempts", lazy="selectin")
