import subprocess


def backup_database():
    subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", "backup_database.ps1"])
    send_to_qnap()

def send_to_qnap():
    subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", "copy_to_qnap.ps1"])