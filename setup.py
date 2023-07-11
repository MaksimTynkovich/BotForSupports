from aiogram.utils import executor # Для запуска бота в online
from create_bot import dp, bot
from handlers import client
from handlers import admin
from data_base import sqlite_db
import os

async def on_startup(dp):
    print("Бот вышел в онлайн")
    sqlite_db.sql_start()
    await bot.set_webhook(os.getenv("URL_APP"))

async def on_shutdown(dp):
    await bot.delete_webhook()

# async def on_startup(_):
#     print("Бот вышел в онлайн")
#     sqlite_db.sql_start()

admin.register_handlers_admin(dp)
client.register_handlers_client(dp)

if __name__ == "__main__":
    # dp.middleware.setup(client.AlbumMiddleware())
    # executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
    executor.start_webhook(dp,
                           webhook_path="",
                           on_startup=on_startup,
                           on_shutdown=on_shutdown,
                           skip_updates=True,
                           host="0.0.0.0",
                           port=int(os.environ.get("PORT", 5000)))

