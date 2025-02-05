import pandas as pd
import os
from openpyxl import load_workbook
from datetime import datetime
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

def day_to_duty():
    for month in MONTH:
        if MONTH[month] == CURRENT_MONTH:
            ACTUAL_MONTH = month

    wb = load_workbook(FILE_PATH)
    sheet = wb[ACTUAL_MONTH]

    CURRENT_DATE = datetime.now().day

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
        message_to_telegram = f"Дежурный на сегодня: <b>{surname}<b>"
        return message_to_telegram