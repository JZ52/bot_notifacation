# db_connection.py
import os
from dotenv import load_dotenv
import psycopg2
from psycopg2 import OperationalError

load_dotenv('key.env')

SQL_ADRES = os.getenv("SQL_ADRES")
SQL_USER = os.getenv("SQL_USER")
SQL_PASSWORD = os.getenv("SQL_PASSWORD")
SQL_DATABASE = os.getenv("SQL_DATABASE")
SQL_PORT = os.getenv("SQL_PORT")


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
        return connection
    except OperationalError as e:
        raise Exception(f"Ошибка подключения к базе данных: {e}")
