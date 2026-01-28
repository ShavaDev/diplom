from datetime import datetime

from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io


def generate_certificate(fullname: str, test_name: str,
                         score: int):
    # 1. Создаем буфер в памяти (виртуальный файл)
    buffer = io.BytesIO()

    # 2. Создаем объект PDF
    # pagesize='A4' задаст стандартный лист.
    p = canvas.Canvas(buffer)
    try:
        # Указываем имя, которое мы хотим использовать ('MyFont'), и имя файла ('Roboto-Regular.ttf')
        pdfmetrics.registerFont(TTFont("MyFont", "fonts/Roboto-Regular.ttf"))
        font_name = 'MyFont'
    except Exception as e:
        # Если путь неверный, выведем ошибку в консоль и возьмем стандартный шрифт
        print(f"Ошибка: {e}")
        font_name = 'Helvetica'

    # рисуем сертификат

    # заголовок (крупный)
    p.setFont(font_name, 30)
    p.drawString(180, 750, "СЕРТИФИКАТ")

    # текст (награждается) (поменьше)
    p.setFont(font_name, 16)
    p.drawString(150, 680, "Награждается студент:")

    # Имя студента, (крупно и по центру)
    p.setFont(font_name, 24)
    p.drawString(150, 650, fullname)

    # Линия разделитель (Рисуем линию от x1,y1 до x2,y2)
    p.line(100, 630, 500, 630)

    # Название теста
    p.setFont(font_name, 16)
    p.drawString(150, 580, f"За успешное прохождение теста:")
    p.setFont(font_name, 20)
    p.drawString(150, 550, f"«{test_name}»")

    # Результат
    p.setFont(font_name, 18)
    p.drawString(150, 500, f"Итоговый балл: {score}")

    # сохраняем
    p.showPage()
    p.save()

    buffer.seek(0)
    return buffer
