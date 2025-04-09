from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bot_notifacation import send_to_telegram
import os

# Функция для проверки обновлений M.E.Doc
def check_medoc_updates(THREAD_ID, MEDOC_URL, VERSION_FILE):
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
                f"\U0001F195 Вышла новая версия M.E.Doс: <b>{version_new}</b>\n"
                f"Обновите, пожалуйста!"
            )
            send_to_telegram(message, thread_id=THREAD_ID)
            print(f"Новая версия: {version_new}")
        else:
            print(f"Версия актуальна: {version_actual}")
    except Exception as e:
            print(f"Ошибка при проверке обновлений M.E.Doc: {e}")
    finally:
        driver.quit()
