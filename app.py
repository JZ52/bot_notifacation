import os
from dotenv import load_dotenv
import psycopg2
import schedule
import time
import requests
from datetime import datetime
from psycopg2 import OperationalError
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import traceback
import sys
from models import day_to_duty


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
VERSION_FILE = "version.txt"




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
    user = day_to_duty()
    message = (f"Сегодня дежурит: <b>{ user }</b>")
    send_to_telegram(message, thread_id=THREAD_ID)

# Функция для создания подключения к базе данных
def create_connection():
    try:
        connection = psycopg2.connect(
            host=SQL_ADRES,
            user=SQL_USER,
            password=SQL_PASSWORD,
            database=SQL_DATABASE,
            port=SQL_PORT,
            client_encoding='UTF8'
        )
        print("Успешное подключение к базе данных")
        return connection
    except OperationalError as e:
        raise Exception(f"Ошибка подключения к базе данных: {e}")

def get_montly_summary():
    # Определяем текущий месяц и год
    today = datetime.date.today()
    year = today.year
    month = today.month
    # Определяем первый и последний день текущего месяца
    start_date = datetime.date(year, month, 1)
    next_month = month % 12 + 1
    next_year = year if month < 12 else year + 1
    end_date = datetime.date(next_year, next_month, 1) - datetime.timedelta(days=1)
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
    today = datetime.date.today()
    year = today.year
    month = today.month
    summary = get_montly_summary()
    start_date = datetime.date(year, month, 1)
    next_month = month % 12 + 1
    next_year = year if month < 12 else year + 1
    end_date = datetime.date(next_year, next_month, 1) - datetime.timedelta(days=1)
    if not summary:
        log_error("Нет данных для отправки сводки.")
        return

    message = f"Количество ответов по Slack за <b>{start_date} - { end_date}</b>: \n"
    for user_name, count in summary:
        ending = get_message_ending(count)
        message += f"👤<b>{user_name}</b>: {count} {ending}\n"
    print(f"{message}\n")
    send_to_telegram(message, hread_id=THREAD_ID)
    

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


# Функция для проверки обновлений M.E.Doc
def check_medoc_updates():
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    try:
        driver.get(MEDOC_URL)
        version_new = driver.find_element(By.CLASS_NAME, "js-update-num").text
        if os.path.exists(VERSION_FILE):
            with open(VERSION_FILE, "r", encoding='utf-8') as file:
                version_actual = file.read().strip()
        else:
            version_actual = ""

        if version_new != version_actual:
            with open(VERSION_FILE, "w", encoding='utf-8') as file:
                file.write(version_new)
            message = (
                f"\U0001F195 Вышла новая версия M.E.Doс: <b>{version_new}</b>.\n"
                f"Обновите, пожалуйста!"
            )
            send_to_telegram(message, thread_id=THREAD_ID)
            print(f"Новая версия: {version_new}")
        else:
            log_error(f"Версия актуальна: {version_actual}")
    except Exception as e:
        log_error(f"Ошибка при проверке обновлений M.E.Doc: {e}")
    finally:
        driver.quit()


def check_next_month():
    today = datetime.now().date()
    if today.day == 1:
        result = send_summary_monthly()

# Основная функция с расписанием задач
def main():
    schedule.every().day.at("08:00").do(duty_day())
    schedule.every().day.at("00:00").do(check_next_month)
    schedule.every().day.at("23:00").do(send_summary)
    schedule.every().saturday.at("09:00").do(check_medoc_updates)
    

    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    main()