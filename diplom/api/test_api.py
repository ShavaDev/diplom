from fastapi import APIRouter, Depends, HTTPException, status, Request
from starlette.responses import StreamingResponse
from database.models import User
from database.schemas import TestCreateSchema, TestSubmitSchema
from deps import get_current_user
from service.test_service import *
from service.report_pdf import generate_certificate
from limiter_config import limiter

test_router = APIRouter(prefix="/test", tags=["Test API"])


@test_router.post("/create_test")
async def create_test_api(test_data: TestCreateSchema,
                          current_user: User = Depends(get_current_user)):
    if current_user.role not in ["teacher", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to perform this action"
        )
    test = create_test_db(test_data=test_data, author_id=current_user.id)
    return test


@test_router.get("/all_tests")
async def get_all_tests_api(current_user: User = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to perform this action"
        )
    return get_all_tests_db()


@test_router.get("/{test_id}/questions")
async def get_exact_test_api(test_id: int, current_user: User = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to perform this action"
        )
    exact_test = get_exact_test_db(test_id=test_id)
    questions = []
    if not exact_test:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Test does not exist"
        )

    for question in exact_test.questions:
        questions.append(
            {
                "id": question.id,
                "text": question.question_text,
                "options": question.options,  # Студент видит варианты, но не знает какой верный
            }
        )

    return questions


@test_router.post("/{test_id}/questions/submit")
@limiter.limit("5/minute")
async def submit_test_api(request: Request,
                          test_id: int, user_test: TestSubmitSchema,
                          current_user: User = Depends(get_current_user)):
    # 1. Проверка на дурака: совпадают ли ID в URL и в теле?
    if test_id != user_test.test_id:
        raise HTTPException(status_code=400, detail="ID теста не совпадает")

    attempt = test_submit_db(author_id=current_user.id, test_data=user_test)

    if not attempt:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ошибка прохождения теста (тест не найден или ошибка сохранения)"
        )

    total = len(attempt.test.questions)

    # Защита от деления на ноль (если в тесте 0 вопросов)
    if total == 0:
        return {"message": "В тесте нет вопросов", "user_score": 0}

    percentage = round((attempt.score / total) * 100, 2)
    is_passed = percentage >= 70

    context = {
        "attempt_id": attempt.id,
        "total_questions": total,
        "user_score": attempt.score,
        "user_score_percentage": percentage,
        "is_passed": is_passed
    }
    return context


@test_router.get("/result/{attempt_id}/certificate")
@limiter.limit("10/minute")
async def get_certificate_api(request: Request,
                              attempt_id: int, current_user: User = Depends(get_current_user)):
    user_attempt = get_exact_attempt_db(attempt_id=attempt_id)
    if not user_attempt:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    if user_attempt.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещен"
        )

    total_questions = len(user_attempt.test.questions)

    if total_questions == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="В тесте нет вопросов"
        )

    percentage = round((user_attempt.score / total_questions) * 100, 2)

    if percentage < 70:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Тест не сдан, сертификат недоступен"
        )

    pdf_buffer = generate_certificate(
        fullname=current_user.fullname,
        test_name=user_attempt.test.title,
        score=user_attempt.score
    )

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=certificate_{attempt_id}.pdf"
        }
    )


@test_router.delete("/{test_id}/delete_test")
async def delete_test_api(test_id: int, current_user: User = Depends(get_current_user)):
    if current_user.role not in ["teacher", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to perform this action"
        )
    result = delete_test_db(test_id=test_id)
    if result:
        return {"message": f"Тест {test_id} успешно удален"}

    # Если сервис вернул False или None (на всякий случай)
    raise HTTPException(status_code=404, detail="Тест не найден")


@test_router.get("/user_attempts")
async def get_user_attempts_api(current_user: User = Depends(get_current_user)):
    result = get_user_attempts_db(author_id=current_user.id)
    if result is None:
        return []
    return result


@test_router.get("/{test_id}/results")
async def get_test_results_api(test_id: int, current_user: User = Depends(get_current_user)):
    if current_user.role not in ["teacher", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to perform this action"
        )
    result = get_test_results_db(test_id=test_id)
    if result is None:
        return []
    return result
