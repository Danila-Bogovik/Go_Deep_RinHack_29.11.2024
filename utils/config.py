import os

# Настройки пути базы данных
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = f"sqlite:///{os.path.join(BASE_DIR, '../bank_data.db')}"
