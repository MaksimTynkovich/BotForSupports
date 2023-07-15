from aiogram import types, Dispatcher, filters
from create_bot import dp, bot, group_id, admin
from data_base import sqlite_db
from handlers import client
from aiogram.dispatcher import FSMContext, filters

async def is_support(user_id):
    return await sqlite_db.is_support(user_id)

async def help(message: types.Message):
    if await sqlite_db.is_support(user_id=message.from_user.id):
        await bot.send_message(message.from_user.id, "/take id - взять тикет\n\n/close id - закрыть тикет \n\n/tickets - активные тикеты\n\n/ban id - заблокировать пользователя\n\n/unban id - разблокировать пользователя\n\n/all *текст* - сделать рассылку пользователям")

# Получить список вопросов
async def get_tickets(message: types.Message):
    if await sqlite_db.is_support(user_id=message.from_user.id):
        get_list = await sqlite_db.get_tickets()
        if not get_list:
            await bot.send_message(message.from_user.id, 'Нет активных тикетов')
        else:
            arr_list = []
            for i in get_list:
                arr_list.append("🔴️️️️️️ ID пользователя: " + str(i[0]) + "\n\n💬️️️️️️ ID обращения: " + str(i[1]) + "\n\n" + str(i[2]) + '\n_____________________________')
            result = '\n\n'.join(arr_list)
            await bot.send_message(message.from_user.id, result)

async def set_support(message: types.Message):
    if message.from_user.id == admin:
        if not message.get_args():
            await bot.send_message(message.from_user.id, "Укажите ID пользователя")
        else:
            await bot.send_message(message.from_user.id, await sqlite_db.set_support(user_id=int(message.get_args())))

async def un_support(message: types.Message):
    if message.from_user.id == admin:
        if not message.get_args():
            await bot.send_message(message.from_user.id, "Укажите ID пользователя")
        else:
            await bot.send_message(message.from_user.id, await sqlite_db.un_support(user_id=message.get_args()))

async def supports(message: types.Message):
    if message.from_user.id == admin:
        await bot.send_message(message.from_user.id, await sqlite_db.supports())            

# Взять тикет в работу
async def take_ticket(message: types.Message):
    if await sqlite_db.is_support(user_id=message.from_user.id):
        if not message.get_args():
            await bot.send_message(message.from_user.id, "Укажите ID обращения")
        else:
            try:
                argument_id = int(message.get_args())
                get_status = await sqlite_db.get_ticket_status_admin(argument_id)
                if get_status == "process":
                    await bot.send_message(message.from_user.id, "Уже в работе")
                elif get_status == "close":
                    await bot.send_message(message.from_user.id, "Тикет недоступен")
                elif get_status == False:
                    await bot.send_message(message.from_user.id, "Неверный ID")
                else:
                    ticket_data = await sqlite_db.take_ticket(argument_id=argument_id)
                    await bot.send_message(await sqlite_db.get_user(argument_id=argument_id), "Саппорт начал работу по вашему обращению")
                    await bot.send_message(message.from_user.id, "Взят в работу")
                    await bot.send_message(group_id, f"🟡 В работе, {message.from_user.username}", reply_to_message_id=ticket_data[0])
                    await bot.edit_message_text(chat_id=channel_id, text=ticket_data[2], message_id=ticket_data[1])
            except:
                await bot.send_message(message.from_user.id, "Ошибка!\nВ ID должны присутствовать только цифры")
            
# Закрыть тикет
async def close_ticket(message: types.Message):
    if await sqlite_db.is_support(user_id=message.from_user.id):
        if not message.get_args():
            await bot.send_message(message.from_user.id, "Укажите ID обращения")
        else:
            argument_id = int(message.get_args())
            get_status = await sqlite_db.get_ticket_status_admin(argument_id)
            if get_status == "close" or get_status == "active":
                await bot.send_message(message.from_user.id, "Тикет не активен")
            else:
                ticket_data = await sqlite_db.close_ticket(argument_id)
                await bot.send_message(message.from_user.id, f"🟢 Обращение №{argument_id} закрыто!")
                await bot.send_message(group_id, f"🟢 Закрыто, {message.from_user.username}", reply_to_message_id=ticket_data[0])
                await bot.edit_message_text(chat_id=channel_id, text=ticket_data[2], message_id=ticket_data[1])

@dp.message_handler(filters.IDFilter(chat_id=group_id))
async def admin_answer(message: types.Message, state: FSMContext):
    if await is_support(message.from_user.id) == 1 and message.chat.id == group_id:
        thread_id = list(message)[4][1]
        value = await sqlite_db.check_thread_id(thread_id)
        await bot.send_message(value, message.text)
    else:
        data = await state.get_data()
        await client.check_report(message=message, state=data)

# Заблокировать
async def ban(message: types.Message):
    if await sqlite_db.is_support(user_id=message.from_user.id):
        await bot.send_message(message.from_user.id, await sqlite_db.ban(int(message.get_args())))

# Разблокировать
async def unban(message: types.Message):
    if await sqlite_db.is_support(user_id=message.from_user.id):
        await bot.send_message(message.from_user.id, await sqlite_db.unban(int(message.get_args())))

async def all(message: types.Message):
    if await sqlite_db.is_support(user_id=message.from_user.id):
        if message.get_args() == '':
            await bot.send_message(message.from_user.id, "Текст рассылки не задан")
        else:
            for i in await sqlite_db.all():
                try:
                    await bot.send_message(i[0], message.get_args())
                except:
                    pass
            await bot.send_message(message.from_user.id, "Рассылка завершена")

# Регистрация хэндлеров
def register_handlers_admin(dp : Dispatcher):
    dp.register_message_handler(take_ticket, commands=['take'])
    dp.register_message_handler(close_ticket, commands=['close'])
    dp.register_message_handler(get_tickets, commands=['tickets'])
    dp.register_message_handler(ban, commands=['ban'])
    dp.register_message_handler(unban, commands=['unban'])
    dp.register_message_handler(set_support, commands=['support'])
    dp.register_message_handler(un_support, commands=['unsupport'])
    dp.register_message_handler(supports, commands=['supports'])
    dp.register_message_handler(all, commands=['all'])
    dp.register_message_handler(help, commands=['help'])
    # dp.register_message_handler(cancel_handler, Text(equals="отмена", ignore_case=True), state="*")

    # dp.register_message_handler(admin_answer, state="*")
    # dp.register_message_handler(all_message, commands=['all'])
