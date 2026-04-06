import os
from dotenv import load_dotenv
import psycopg2
import requests
from datetime import date, timedelta
from datetime import datetime
from psycopg2 import OperationalError
from models import day_to_duty
from dvr import check_dvr
from apscheduler.schedulers.blocking import BlockingScheduler
import time
from telegram_exporter import  export_start
from db_connection import create_connection
import medoc_utils
from pathlib import Path

# Загрузка переменных окружения
load_dotenv('key.env')

SQL_ADRES = os.getenv("SQL_ADRES")
SQL_USER = os.getenv("SQL_USER")
SQL_PASSWORD = os.getenv("SQL_PASSWORD")
SQL_DATABASE = os.getenv("SQL_DATABASE")
SQL_PORT = os.getenv("SQL_PORT")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_KEY = os.getenv("API_KEY")
API_URL = os.getenv("API_URL")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
THREAD_ID = os.getenv("THREAD_ID")
MEDOC_URL = os.getenv("MEDOC_URL")



BASE_DIR = Path(__file__).resolve().parent
VERSION_FILE = BASE_DIR / "version.txt"


def get_message_ending(count):
    if 11 <= count % 100 <= 19:
        return "сообщений"
    elif count % 10 == 1:
        return "сообщение"
    elif 2 <= count % 10 <= 4:
        return "сообщения"
    else:
        return "сообщений"

def duty_day():
    message = day_to_duty()
    send_to_telegram(message, thread_id=THREAD_ID)

def get_montly_summary():
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
    start_date = date(prev_year, prev_month, 1)
    end_date = date(year, month, 1) - timedelta(days=1)
    query = """
    SELECT user_name, COUNT(slack_messages) AS message_count
    FROM slack_messages
    WHERE date::date >= %s AND date::date <= %s
    GROUP BY user_name
    """
    try:
        connection = create_connection()
        with connection.cursor() as cursor:
            cursor.execute(query, (start_date, end_date))
            result = cursor.fetchall()
            return result
    except Exception as e:
        log_error(f"Ошибка при выполнении запроса: {e}")
        return []
    finally:
        if 'connection' in locals() and connection is not None:
            connection.close()

def get_daily_summary():
    query = """
            SELECT user_name, COUNT(*) as message_count
            FROM slack_messages
            WHERE date::date = %s
            GROUP BY user_name
            ORDER BY message_count DESC
    """
    today = datetime.now().date()
    try:
        connection = create_connection()
        with connection.cursor() as cursor:
            cursor.execute(query, (today,))
            result = cursor.fetchall()
            return result
    except Exception as e:
        log_error(f"Ошибка при выполнении запроса: {e}")
        return []
    finally:
        if 'connection' in locals() and connection is not None:
            connection.close()


# Функция для отправки сообщений в Telegram
def send_to_telegram(message, thread_id=None, retries=3):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
    if thread_id:
        payload["message_thread_id"] = thread_id

    for attempt in range(retries):
        try:
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                return
        except Exception as e:
            print(f"Исключение при отправке сообщения: {e}")
        time.sleep(5)  # Пауза перед повторной попыткой


def send_summary_monthly():
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
    start_date = date(prev_year, prev_month, 1)
    end_date = date(year, month, 1) - timedelta(days=1)
    summary = get_montly_summary()
    if not summary:
        log_error("Нет данных для отправки сводки.")
        return

    message = f"Количество ответов по Slack за <b>{start_date} - { end_date}</b>: \n"
    for user_name, count in summary:
        ending = get_message_ending(count)
        message += f"👤<b>{user_name}</b>: {count} {ending}\n"
    print(f"{message}\n")
    send_to_telegram(message, thread_id=THREAD_ID)
    

# Функция для отправки сводки за день
def send_summary():
    summary = get_daily_summary()
    today = datetime.now().date()
    if not summary:
        log_error("Нет данных для отправки сводки.")
        return

    message = f"Количество ответов по Slack за <b>{today}</b>: \n"
    for user_name, count in summary:
        ending = get_message_ending(count)
        message += f"👤<b>{user_name}</b>: {count} {ending}\n"
    print(f"{message}\n")
    send_to_telegram(message, thread_id=THREAD_ID)

def check_next_month():
    today = datetime.now().date()
    if today.day == 1:
        result = send_summary_monthly()

def check_dvr_work():
    all_message = check_dvr()
    if all_message:
        send_to_telegram(all_message, thread_id=THREAD_ID)

# Основная функция с расписанием задач
def main():
    scheduler = BlockingScheduler()

    scheduler.add_job(duty_day, 'cron', hour=8)
    scheduler.add_job(duty_day, 'cron', hour=22)
    scheduler.add_job(check_next_month, 'cron', hour=0, minute=0)
    #scheduler.add_job(send_summary, 'cron', hour=23)
    scheduler.add_job(medoc_utils.check_medoc_updates, 'cron', hour=9, args=[THREAD_ID, MEDOC_URL, VERSION_FILE])
    scheduler.add_job(check_dvr_work, 'cron', hour='9-21/3')  # 9, 12, 15, 18, 21
    #scheduler.add_job(export_start, 'cron', day = 1, hour = 9, minute = 15)

    print("🟢 Планировщик запущен. Нажмите Ctrl+C для выхода.")

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("\n🛑 Получен сигнал остановки. Завершение...")
        scheduler.shutdown()


if __name__ == "__main__":
    main()
