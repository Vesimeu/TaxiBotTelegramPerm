import logging
from aiogram import Bot, Dispatcher, executor
from aiogram.types import BotCommand
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import config
from database.db import init_db

# Инициализация бота и диспетчера
logging.basicConfig(level=logging.INFO)
bot = Bot(token=config.TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Инициализация базы данных
init_db()

# Импорт хэндлеров
from handlers.admin import *
from handlers.driver import *
from handlers.passenger import *
from handlers.start import *

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)