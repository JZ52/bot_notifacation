import requests
from dotenv import load_dotenv
import os
from models_files import deleta_files
import time

load_dotenv('key.env')

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
THREAD_ID = os.getenv("THREAD_ID")

def send_telegram_files(file_path, thread_id=None, retries=3):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
    }

    if thread_id:
        data["message_thread_id"] = thread_id

    for attempt in range(retries):
        try:
            with open(file_path, "rb") as doc:
                files = {"document": doc}
                response = requests.post(url, files=files, data=data, timeout=10)

            if response.status_code == 200:
                print("Файл успешно отправлен")
                deleta_files(file_path)
                return
            else:
                print(f"Ошибка при отправке файла: {response.status_code}, {response.text}")
        except Exception as e:
            print(f"Исключение при отправке файла: {e}")
        time.sleep(5)
