import os
import socket
from collections import defaultdict

IP_FILE_PATH = 'ip_dvr.txt'

def check_service(dic, port, body):
    down_dvr = set()
    for key, value in dic.items():
        for ip_check_dvr in value:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                result = sock.connect_ex((ip_check_dvr, port))
                status = "в сети" if result == 0 else "не в сети"
                print(f"Видеорегистратор {ip_check_dvr}:{port} {status}")
                if result != 0:
                    body.add(f"{key} - {ip_check_dvr}")
                    down_dvr.add(ip_check_dvr)

    if body:
        return "Видеорегистраторы не в сети:\n" + "\n".join(body)


def message_to_telegram(body):
    string_ip = []
    for item in body:
        item = item.replace('_', ' ')
        parts = item.split(' - ')
        if len(parts) == 2:
            name, ip = parts
            link = f'<a href = "http://{ ip }:85"> { ip } </a>'
            string_ip.append(f'🛒 <b>{ name }</b> - { link }')
        else:
            string_ip.append(item)
    result= '\n'.join(string_ip)
    return result

def read_ip_file(IP_FILE_PATH):
    dic = defaultdict(list)
    with open(IP_FILE_PATH, 'r', encoding="utf-8") as file:
        for ip_check in file:
            key, *value = ip_check.split()
            dic[key].extend(value)
    return dic

def check_dvr():
    body = set()
    dic = read_ip_file(IP_FILE_PATH)
    check_service(dic, 85, body)
    if body:
        result = message_to_telegram(body)
        head = f'Видеорегистраторы не в сети: \n\n'
        all_message = head + result
        return all_message
    else:
        return None