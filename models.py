import pandas as pd
import os
from openpyxl import load_workbook
from datetime import datetime, time, timedelta
import re

FILE_PATH = 'график дежурств 2025.xlsx'

MONTH = { "Январь": 1, "февраль": 2, "март": 3, "апрель": 4, 
        "май": 5, "июнь": 6, "июль": 7, "август": 8, 
        "сентябрь": 9, "октябрь": 10, "ноябрь": 11, "декабрь": 12
}

USER_DUTY = {
    "Гриченко": "Гриченко Павел",
    "Залецкий": "Залецкий Евгений",
    "Шутов": "Шутов Алексей",
}

CURRENT_MONTH = datetime.now().month
ACTUAL_MONTH = ""
DUTY = ""
LINE = ""
line_letter = ""
MESSAGE = "Сегодня"


def day_to_duty():
    for month in MONTH:
        if MONTH[month] == CURRENT_MONTH:
            ACTUAL_MONTH = month

    wb = load_workbook(FILE_PATH)
    sheet = wb[ACTUAL_MONTH]

    CURRENT_DATE = datetime.now().day
    TIME = datetime.now().time()

    if TIME >= time(21, 30) and TIME <= time(23, 59):
        CURRENT_DATE = datetime.now().date()
        MESSAGE = "Завтра"
        NEXT_CURRENT_DATE = CURRENT_DATE + timedelta(days=1)
        if NEXT_CURRENT_DATE.month != CURRENT_DATE.month:
            NEXT_CURRENT_DATE = datetime(NEXT_CURRENT_DATE.year, NEXT_CURRENT_DATE.month, 1).date()
            CURRENT_DATE = NEXT_CURRENT_DATE.day
        CURRENT_DATE = NEXT_CURRENT_DATE.day

    for row in sheet['A1:AF1']:
        for cell in row:
            if cell.value == CURRENT_DATE:
                DUTY = cell.coordinate
                column_letter = re.sub(r'\d', '', DUTY)

    for cell in sheet[column_letter]:
        if cell.value in ['x', 'Х', 'х', 'X']:
            LINE = cell.coordinate
            line_letter = re.sub(r'\D', '', LINE)

    for row in sheet.iter_rows(min_row=int(line_letter), max_row=int(line_letter), values_only=True):
        first_value = row[0]  # Первое значение в строке
        if first_value in USER_DUTY:
            surname = USER_DUTY[first_value]  # Извлекаем фамилию из кортежа
            full_message = f"{ MESSAGE } дежурит: <b> { surname }</b>"
    return full_message