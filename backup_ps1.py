import subprocess
import os
import shutil
import subprocess
from datetime import datetime
from dotenv import load_dotenv



load_dotenv('key.env')


backup_folder = os.getenv("BACKUP_FOLDER")
destination_path = os.getenv("DESTINATION_PATH")
username = os.getenv("NET_USERNAME")
password = os.getenv("PASSWORD")


def backup_database():
    subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", "backup_database.ps1"])
    backup_to_qnap()


def get_latest_sql_file(folder):
    sql_files = [
        os.path.join(folder, f)
        for f in os.listdir(folder)
        if f.endswith(".sql") and os.path.isfile(os.path.join(folder, f))
    ]
    if not sql_files:
        return None
    return max(sql_files, key=os.path.getmtime)

def map_network_drive(drive_letter, path, username, password):
    cmd = [
        "net", "use", f"{drive_letter}:", path,
        f"/user:{username}", password, "/persistent:no"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0, result.stderr.strip()

def unmap_network_drive(drive_letter):
    subprocess.run(["net", "use", f"{drive_letter}:", "/delete", "/y"],
                   capture_output=True)

def backup_to_qnap():
    latest_file = get_latest_sql_file(backup_folder)

    if not latest_file:
        print("❌ Нет .sql файлов для копирования.")
        return

    print(f"✅ Найден файл: {latest_file}")

    success, error = map_network_drive("Z", destination_path, username, password)
    if not success:
        print(f"❌ Ошибка при подключении сетевого диска: {error}")
        return
    print("🔗 Сетевой диск Z: смонтирован.")

    try:
        destination_file = os.path.join("Z:\\", os.path.basename(latest_file))
        shutil.copy2(latest_file, destination_file)
        print(f"✅ Файл успешно скопирован: {destination_file}")
    except Exception as e:
        print(f"❌ Ошибка при копировании: {e}")
    finally:
        unmap_network_drive("Z")
        print("🔌 Сетевой диск Z: отключён.")