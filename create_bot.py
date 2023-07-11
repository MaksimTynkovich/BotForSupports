# from aiogram import Bot
# from aiogram.dispatcher import Dispatcher # Диспетчер для отлавливания событий в чате
# from aiogram.contrib.fsm_storage.memory import MemoryStorage

# storage=MemoryStorage() # Сохранение состояния в ОЗУ

# group_id = -1001961836070
# channel_id = -1001793402278

# bot = Bot(token="5699040359:AAE3eJ9aqePRAZIN91KJZL1nlvREhsGLcQ4")
# dp = Dispatcher(bot, storage=storage)

from aiogram import Bot
from aiogram.dispatcher import Dispatcher # Диспетчер для отлавливания событий в чате
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import os
from dotenv import load_dotenv, find_dotenv

storage=MemoryStorage() # Сохранение состояния в ОЗУ
load_dotenv(find_dotenv())

admin = int(os.getenv("ADMIN"))
group_id = int(os.getenv("GROUP_ID"))
channel_id = int(os.getenv("CHANNEL_ID"))

bot = Bot(token=os.getenv("TOKEN"))
dp = Dispatcher(bot, storage=storage)