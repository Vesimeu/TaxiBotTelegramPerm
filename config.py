import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")

DB_PATH = "database/base.db"
API_KEY = os.getenv("API_KEY")