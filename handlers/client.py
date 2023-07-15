from aiogram import types, Dispatcher
from create_bot import dp, bot, channel_id, group_id
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ContentType
from data_base import sqlite_db
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext, filters
from handlers.admin import is_support

from typing import Union, List
import asyncio

from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware

# import telegram
# from telegram import InputMediaPhoto

message_user_id = {}

class FSMQuestion(StatesGroup):
    id = State()
    message = State()
    group_message_id = State()
    channel_message_id = State()

# class AlbumMiddleware(BaseMiddleware):
#     """This middleware is for capturing media groups."""

#     album_data: dict = {}

#     def __init__(self, latency: Union[int, float] = 0.01):
#         """
#         You can provide custom latency to make sure
#         albums are handled properly in highload.
#         """
#         self.latency = latency
#         super().__init__()

#     async def on_process_message(self, message: types.Message, data: dict):
#         if not message.media_group_id:
#             return

#         try:
#             self.album_data[message.media_group_id].append(message)
#             raise CancelHandler()  # Tell aiogram to cancel handler for this group element
#         except KeyError:
#             self.album_data[message.media_group_id] = [message]
#             await asyncio.sleep(self.latency)

#             message.conf["is_last"] = True
#             data["album"] = self.album_data[message.media_group_id]

#     async def on_post_process_message(self, message: types.Message, result: dict, data: dict):
#         """Clean up after handling our album."""
#         if message.media_group_id and message.conf.get("is_last"):
#             del self.album_data[message.media_group_id]


# async def handle_albums(message: types.Message, album: List[types.Message]):
#     media_group = []
#     photos_id = []
#     telegramMediaMethod = telegram.Bot(token = '5699040359:AAE3eJ9aqePRAZIN91KJZL1nlvREhsGLcQ4')
#     for obj in album:
#         if obj.photo:
#             photos_id.append(obj.photo[-1].file_id)
#             # file_id = obj.photo[-1].file_id
#         else:
#             pass
#             # file_id = obj[obj.content_type].file_id
#         try:
#             pass
#             # media_group.attach({"media": file_id, "type": obj.content_type})
#         except ValueError:
#             return await message.answer("Данный тип альбома не поддерживается")
    
#     for number, url in enumerate(photos_id):
#         media_group.append(InputMediaPhoto(media=url, caption = album[0].caption if number == 0 else ''))

#     telegramMediaMethod.send_media_group(chat_id=message.from_user.id, media=media_group)



@dp.message_handler(content_types=types.ContentType.PHOTO)
async def photo_check(message: types.Message):
    await bot.send_message(message.from_user.id, "Временно принимаем фото через сторонний сервис. Воспользуйтесь https://imgur.com/")
#     await sqlite_db.add_user(message.from_user.id, message.from_user.username)
#     if message.chat.type != 'supergroup':
#         # if not await sqlite_db.is_active_ticket(message.from_user.id):
#             # botSend = await bot.send_photo(channel_id, photo=message.photo[-1].file_id, caption=message.caption)
#         if not await sqlite_db.is_active_ticket(message.from_user.id):
#             botSend = await bot.send_photo(channel_id, photo=message.photo[-1].file_id, caption=message.caption)
#             # print(botSend)
#             # message_user_id[list(botSend)[5][1]] = message.from_user.id
#             message_user_id[message.caption] = message.from_user.id
#             print(message_user_id)
#             await sqlite_db.add_ticket(user_id=message.from_user.id, message=message.caption, channel_message_id=list(botSend)[0][1], request_id=message.message_id)
#         else:
#             await bot.send_photo(group_id, photo=message.photo[-1].file_id, caption=message.caption, reply_to_message_id=await sqlite_db.get_message_group_id(user_id=message.from_user.id))


async def load_question(message: types.Message, state: FSMContext):
    await sqlite_db.add_user(message.from_user.id, message.from_user.username)
    if await sqlite_db.check_banned(message.from_user.id) == False:
        if not await is_support(message.from_user.id) or await is_support(message.from_user.id) == 0:
            if message.chat.type != 'supergroup':
                if await sqlite_db.get_ticket_status_active(user_id=message.from_user.id) == "active" and await sqlite_db.get_count_message(user_id=message.from_user.id) <= 9:
                    msg = await sqlite_db.get_message_channel(message.from_user.id) + f'\n\n📌 {message.text}' # Сохранять в Базу данных
                    message_user_id[msg] = message.from_user.id
                    await sqlite_db.add_question_post(message.from_user.id, msg)
                    id_post = await sqlite_db.channel_message_id(user_id=message.from_user.id)
                    new_msg = await sqlite_db.get_message_channel(message.from_user.id)

                    await bot.edit_message_text(chat_id=channel_id, text=new_msg, message_id=id_post)

                if not await sqlite_db.is_active_ticket(message.from_user.id):
                    botSend = await bot.send_message(channel_id, 
                    f'🔴️️️️️️ #НЕ_ОТВЕЧЕНО #Telegram #ID{message.from_user.id}\n\nОбращение №{message.message_id} от пользователя {message.from_user.username} \n\n📌 {message.text}')
                    message_user_id[list(botSend)[5][1]] = message.from_user.id
                    # list(botSend)[5][1] - Достаём текст сообщения
                    # list(botSend)[0][1] - Достаём ID поста
                    await sqlite_db.add_ticket(user_id=message.from_user.id, message=list(botSend)[5][1], channel_message_id=list(botSend)[0][1], request_id=message.message_id)

                if await sqlite_db.get_ticket_status_active(message.from_user.id) == "active" and await sqlite_db.get_count_message(user_id=message.from_user.id) == 10:
                    await bot.send_message(message.from_user.id, "Ожидайте ответа от саппорта")

                if await sqlite_db.get_ticket_status_process(message.from_user.id) == "process":
                    testik = await bot.send_message(group_id, f"📍Вопрос от пользователя\n\n{message.text}", reply_to_message_id=await sqlite_db.get_message_group_id(user_id=message.from_user.id))
                    # print(testik)


@dp.message_handler(filters.ForwardedMessageFilter(True), filters.IDFilter(chat_id=group_id))
async def check_report(message: types.Message, state: FSMContext):
    await sqlite_db.upd_ticket(user_id=message_user_id.get(message.text),group_message_id=message.message_id)


async def command_start(message: types.Message):
    await sqlite_db.add_user(message.from_user.id, message.from_user.username)
    await bot.send_message(message.from_user.id, 'Привет! Это тех.поддержка Introsat™\nОзнакомьтесь с FAQ прежде чем задавать вопрос, возможно на него уже есть ответ.\nЧто бы мы могли быстрее Вам помочь, подробнее распишите вашу проблему', reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton(text="FAQ", url='https://docs.google.com/document/d/15KqFrMlc6Jzxut_zMf_pXNx5r5JTjqfKEvCHWx99rEc/edit#heading=h.demjj79bt080')))
    

def register_handlers_client(dp : Dispatcher):
    dp.register_message_handler(command_start, commands=['start', 'help'])
    # dp.register_message_handler(handle_albums,is_media_group=True, content_types=types.ContentType.ANY)
    dp.register_message_handler(load_question, state="*")
