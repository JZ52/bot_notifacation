from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bot_notifacation import send_to_telegram
import os

# Функция для проверки обновлений M.E.Doc
def check_medoc_updates(THREAD_ID, MEDOC_URL, VERSION_FILE):
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    
    driver = None 
    
    try:
        service = Service(ChromeDriverManager().install())
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
            
    except Exception as e:п
        print(f"Ошибка при проверке обновлений M.E.Doc: {e}")
        
    finally:
        # Гарантированное закрытие драйвера, если он был инициализирован
        if driver:
            driver.quit()