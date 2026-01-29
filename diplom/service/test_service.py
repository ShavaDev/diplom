from http.client import HTTPException

from database.models import Test, Question, Option, Attempt
from database.basa import session_db
from database.schemas import *
from sqlalchemy.orm import joinedload


# создание теста (для учителя)
def create_test_db(author_id: int, test_data: TestCreateSchema):
    with session_db() as db:
        # 1. Создаем тест
        test = Test(title=test_data.title, timer=test_data.timer, author_id=author_id)
        db.add(test)
        for question in test_data.questions:
            # 2. Создаем вопрос. Вместо test_id=test.id,
            # мы можем просто привязать объект вопроса к тесту
            new_question = Question(question_text=question.question_text, test=test)
            db.add(new_question)
            for option in question.options:
                # 3. Создаем вариант. Привязываем его к объекту new_question
                new_option = Option(option_text=option.option_text, is_correct=option.is_correct,
                                    question=new_question)  # SQLAlchemy сама вытащит ID вопроса
                db.add(new_option)
        db.commit()
        db.refresh(test)
        return test


# удаление теста (для учителя)
def delete_test_db(test_id: int):
    with session_db() as db:
        test = db.get(Test, id=test_id)
        if not test:
            raise HTTPException()
        db.delete(test)
        db.commit()
        return True


# отправка пройденного теста студентом
def test_submit_db(author_id: int, test_data: TestSubmitSchema):
    with session_db() as db:
        score = 0
        test = db.get(Test, id=test_data.test_id)
        if not test:
            return None

        # Логика проверки на дубликаты вопросов
        answered_questions = [a.question_id for a in test_data.answers]
        if len(answered_questions) != len(set(answered_questions)):
            return None

        # Перебираем ответы, которые прислал студент в схеме
        for student_answer in test_data.answers:
            # Достаем этот вариант из базы
            option = db.get(Option, id=student_answer.option_id)
            # Проверяем: существует ли такой вариант И правильный ли он
            if option and option.is_correct:
                # ВАЖНО: Тут еще стоит проверить, что этот вариант
                # принадлежит вопросу, который принадлежит нашему тесту!
                # порталы relationship
                if option.question.test_id == test.id:
                    score += 1
        end_time = datetime.now()
        attempt = Attempt(
            test=test, score=score,
            author_id=author_id,
            test_id=test.id, completed=True,
            end_time=end_time)
        db.add(attempt)
        db.commit()
        db.refresh(attempt)
        return attempt


# получение всех тестов
def get_all_tests_db():
    with session_db() as db:
        tests = db.query(Test).all()
        if tests:
            return tests
        return None


# получение одного теста для студента
def get_exact_test_db(test_id: int):
    with session_db() as db:
        # Используем joinedload, чтобы сразу подтянуть вопросы и ответы для студента
        test = db.query(Test) \
            .options(joinedload(Test.questions). \
                     joinedload(Question.options)). \
            filter(Test.id == test_id).first()
        if test:
            return test
        return None


# получение попыток пользователя
def get_user_attempts_db(author_id: int):
    with session_db() as db:
        attempts = db.query(Attempt).filter(Attempt.author_id == author_id).all()
        if attempts:
            return attempts
        return None


# результаты теста для учителя
def get_test_results_db(test_id: int):
    with session_db() as db:
        results = db.query(Attempt) \
            .options(joinedload(Attempt.author)) \
            .filter(Attempt.test_id == test_id) \
            .all()
        return results


# для скачивания сертификата
def get_exact_attempt_db(attempt_id: int):
    with session_db() as db:
        # Подгружаем попытку сразу вместе с Тестом (чтобы взять название)
        attempt = db.query(Attempt). \
            options(joinedload(Attempt.test)). \
            filter(Attempt.id == attempt_id).first()
        return attempt
