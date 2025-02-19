import pandas as pd
import os
from openpyxl import load_workbook
from datetime import datetime, time, timedelta
import re

FILE_PATH = 'график дежурств 2025.xlsx'

MONTH = {
    "Январь": 1, "Февраль": 2, "Март": 3, "Апрель": 4,
    "Май": 5, "Июнь": 6, "Июль": 7, "Август": 8,
    "Сентябрь": 9, "Октябрь": 10, "Ноябрь": 11, "Декабрь": 12
}

USER_DUTY = {
    "Гриченко": "Гриченко Павел",
    "Залецкий": "Залецкий Евгений",
    "Шутов": "Шутов Алексей",
}

def day_to_duty():
    now = datetime.now()
    current_date = now.day
    current_month = now.month
    message = "Сегодня"

    # Если время больше 21:30, переключаемся на "завтра"
    if time(21, 30) <= now.time() <= time(23, 59):
        next_day = now + timedelta(days=1)
        message = "Завтра"
        current_date = next_day.day
        current_month = next_day.month

    # Получаем название месяца
    actual_month = next((month for month, num in MONTH.items() if num == current_month), None)
    if actual_month is None:
        return "Ошибка: месяц не найден."

    # Открываем книгу и выбираем лист
    try:
        wb = load_workbook(FILE_PATH)
        sheet = wb[actual_month]
    except Exception as e:
        return f"Ошибка при загрузке файла: {e}"

    # Поиск даты в первой строке
    column_letter = None
    for row in sheet['A1:AF1']:
        for cell in row:
            if cell.value == current_date:
                column_letter = re.sub(r'\d', '', cell.coordinate)
                break
        if column_letter:
            break

    if not column_letter:
        return f"Ошибка: дата {current_date} не найдена в файле."

    # Поиск дежурного
    duty_row = None
    for cell in sheet[column_letter]:
        if str(cell.value).strip().lower() in ['x', 'х']:
            duty_row = re.sub(r'\D', '', cell.coordinate)
            break

    if not duty_row:
        return f"Ошибка: не найден дежурный на {message.lower()}."

    # Получение фамилии дежурного
    duty_person = None
    for row in sheet.iter_rows(min_row=int(duty_row), max_row=int(duty_row), values_only=True):
        surname = row[0]  # Первая колонка содержит фамилию
        if surname in USER_DUTY:
            duty_person = USER_DUTY[surname]
            break

    if not duty_person:
        return f"Ошибка: дежурный не найден в списке сотрудников."

    return f"{message} дежурит: <b>{duty_person}</b>"
