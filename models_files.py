import os
from datetime import timedelta

def read_file():
    with open("user.txt", "r", encoding="utf-8") as file:
        user = file.read().splitlines()
        return user

def save_as_file(data, date_from, date_to):
    personal = data[0][0]
    file_name = f"{ personal }  { date_from } - { date_to - timedelta(days=1) }.txt"
    with open(file_name, "w", encoding="utf-8") as file:
        file.write(f'Дата - кол-во ответов\n')
        for _, date, answer in data:
            file.write(f'{ date.strftime("%d.%m.%Y")} - { answer }\n')

    return file_name


def deleta_files(file):
    os.remove(file)