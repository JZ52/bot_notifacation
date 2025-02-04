import pandas as pd
import os
from openpyxl import load_workbook
from app import get_daily_summary
from datetime import datetime

# data = get_daily_summary()
FILE_PATH = 'график дежурств 2025.xlsx'


wb = load_workbook(FILE_PATH)

info = wb.get_sheet_names()


print(f"{ info }")