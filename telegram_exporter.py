from db_connection import create_connection
from datetime import date
import models_files
from telegram_send_messages import send_telegram_files
from dotenv import load_dotenv
import os


load_dotenv('key.env')

THREAD_ID = os.getenv("THREAD_ID")

def data_to_telegram(user_name, date_from, date_to):

    query = """
            SELECT user_name, date::date AS response_date, COUNT(*) AS total_responses
            FROM slack_messages
            WHERE user_name = %s
            AND date >= %s
            AND date <= %s
            GROUP BY user_name, date::DATE
            ORDER BY response_date
    """

    try:
        connect_bd = create_connection()
        with connect_bd.cursor() as cursor:
            cursor.execute(query, (user_name, date_from, date_to))
            result = cursor.fetchall()
            return result
    except Exception as e:
        print(f"Ошибка при выполнении запроса: { e }")
        return []
    finally:
        if connect_bd:
            connect_bd.close()


def get_date_range():
    today = date.today()
    year = today.year
    month = today.month

    # Определяем предыдущий месяц
    if month == 1:  # Если сейчас январь, то предыдущий месяц — декабрь прошлого года
        prev_month = 12
        prev_year = year - 1
    else:
        prev_month = month - 1
        prev_year = year

    # Начало и конец предыдущего месяца
    date_from = date(prev_year, prev_month, 1)
    date_to = date(year, month, 1)
    print(date_from, date_to)
    return date_from, date_to


def export_start():
    users = models_files.read_file()
    date_from, date_to = get_date_range()
    for user in users:
        data = data_to_telegram(user, date_from, date_to)
        file = models_files.save_as_file(data, date_from, date_to)
        send_telegram_files(file, thread_id=THREAD_ID)

