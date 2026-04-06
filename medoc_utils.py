from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bot_notifacation import send_to_telegram
import os
import shutil
import time
import uuid
import random


# Функция для проверки обновлений M.E.Doc
def check_medoc_updates(THREAD_ID, MEDOC_URL, VERSION_FILE):
    
    CHROME_DRIVER_PATH = "/home/jz_52/drivers/chrome140/chromedriver-v140-bin/chromedriver-linux64/chromedriver"

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-features=NetworkService")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("--no-default-browser-check")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    
    # Используем случайный порт для отладки вместо фиксированного 9222
    debug_port = random.randint(9300, 9400)
    chrome_options.add_argument(f"--remote-debugging-port={debug_port}")
    
    # Создаем уникальную временную директорию
    unique_id = f"{int(time.time())}_{os.getpid()}_{uuid.uuid4().hex[:8]}"
    temp_data_dir = os.path.join("/tmp/", f"chrome_temp_dir_{unique_id}")
    
    chrome_options.add_argument(f"--user-data-dir={temp_data_dir}")
    chrome_options.binary_location = "/home/jz_52/drivers/chrome141/chrome-linux64/chrome"

    driver = None
    
    try:
        service = Service(executable_path=CHROME_DRIVER_PATH)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        driver.implicitly_wait(10)
        
        driver.get(MEDOC_URL)
        
        version_element = WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "js-update-num"))
        )
        version_new = version_element.text

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
        # Гарантированная очистка
        if driver:
            try:
                driver.quit()
                print("Chrome driver закрыт")
            except Exception as e:
                print(f"Ошибка при закрытии драйвера: {e}")
        
        # Подождем немного, чтобы Chrome освободил директорию
        time.sleep(2)
        
        if os.path.exists(temp_data_dir):
            try:
                shutil.rmtree(temp_data_dir)
                print(f"Временный каталог удален: {temp_data_dir}")
            except Exception as e:
                print(f"Ошибка при удалении временного каталога: {e}")