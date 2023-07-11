# import sqlite3 as sq
import psycopg2
from create_bot import bot
import os

def sql_start():
    global base, cursor
    # base = psycopg2.connect("postgresql://postgres:t0cSgT93h03PZVLljos0@containers-us-west-62.railway.app:7458/railway", sslmode="require")
    # base = sq.connect('prod1.db')
    base = psycopg2.connect(dbname="railway", host="containers-us-west-62.railway.app", user="postgres", password="t0cSgT93h03PZVLljos0", port="7458")
    cursor = base.cursor()
    if base:
        print("DB connect!")
    cursor.execute('CREATE TABLE IF NOT EXISTS users(user_id INT PRIMARY KEY, username TEXT, is_support BOOLEAN, is_work, is_banned BOOLEAN)')
    cursor.execute("CREATE TABLE IF NOT EXISTS tickets(id INTEGER PRIMARY KEY, user_id INTEGER, message TEXT, message_count INTEGER, channel_message_id INTEGER, group_message_id INTEGER, request_id INTEGER, status TEXT)")
    base.commit()

async def add_user(user_id, username):
    cursor.execute("SELECT user_id, username FROM users WHERE user_id=?", (user_id,))
    user = cursor.fetchone()
    try:
        if user[1] is None:
            cursor.execute("UPDATE users set username =? WHERE user_id =?", (username, user_id,))
            base.commit()
    except:
        if not user:
            cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?)", (user_id, username, False, False, False))
            base.commit()

async def is_active_ticket(user_id): # Функция проверки пользователя на активный тикет
    cursor.execute("SELECT * FROM tickets WHERE user_id=? AND status =? OR status =?", (user_id, "active", "process",))
    user = cursor.fetchall()
    return user

async def get_count_message(user_id):
    cursor.execute("SELECT message_count FROM tickets WHERE user_id=? ", (user_id,))
    count = cursor.fetchone()[0]
    return count

async def channel_message_id(user_id):
    cursor.execute("SELECT channel_message_id FROM tickets WHERE user_id=? AND status=?", (user_id, "active",))
    channel = cursor.fetchone()[0]
    return channel

async def add_question_post(user_id, message):
    cursor.execute("UPDATE tickets set message =?, message_count = message_count + 1 WHERE user_id =?", (message, user_id,))
    base.commit()

async def get_message_channel(user_id):
    message = cursor.execute("SELECT message FROM tickets WHERE user_id =? AND status=?", (user_id,"active",)).fetchone()[0]
    return message

async def add_ticket(user_id, message, channel_message_id, request_id):
    cursor.execute("INSERT INTO tickets (user_id, message, channel_message_id, message_count, group_message_id, request_id, status) VALUES (?, ?, ?, ?, ?, ?, ?)", (user_id, message, channel_message_id, 1, None, request_id, "active"))
    base.commit()

async def upd_ticket(user_id, group_message_id):
    cursor.execute("UPDATE tickets SET group_message_id =? WHERE user_id =? AND status =?", (group_message_id, user_id, "active"))
    base.commit()

async def get_message_group_id(user_id):
    cursor.execute("SELECT group_message_id FROM tickets WHERE user_id=?", (user_id,))
    message_group_id = cursor.fetchone()[0]
    return message_group_id

async def get_tickets():
    cursor.execute("SELECT user_id, request_id, message, channel_message_id, group_message_id FROM tickets WHERE status=?", ("active",))
    tickets = cursor.fetchall()
    return tickets

async def get_ticket_status_admin(argument_id):
    try:
        status = cursor.execute("SELECT status FROM tickets WHERE request_id=?", (argument_id,)).fetchone()[0] # Исправить, так как в случае пустого значения будет ошибка
    except:
        status = 0
    return status

async def get_ticket_status(user_id):
    status = cursor.execute("SELECT status FROM tickets WHERE user_id=?", (user_id,)).fetchone()[0] # Исправить, так как в случае пустого значения будет ошибка
    return status

async def get_ticket_status_active(user_id):
    try:
        status = cursor.execute("SELECT status FROM tickets WHERE user_id=? AND status=?", (user_id,"active",)).fetchone()[0] # Исправить, так как в случае пустого значения будет ошибка
    except:
        status = cursor.execute("SELECT status FROM tickets WHERE user_id=? AND status=?", (user_id,"active",)).fetchone() # Исправить, так как в случае пустого значения будет ошибка
    return status

async def get_ticket_status_process(user_id):
    try:
        status = cursor.execute("SELECT status FROM tickets WHERE user_id=? AND status=?", (user_id,"process",)).fetchone()[0] # Исправить, так как в случае пустого значения будет ошибка
    except:
        status = cursor.execute("SELECT status FROM tickets WHERE user_id=? AND status=?", (user_id,"process",)).fetchone() # Исправить, так как в случае пустого значения будет ошибка
    return status

async def take_ticket(argument_id):
    cursor.execute("UPDATE tickets set status =? WHERE request_id =?", ("process", argument_id)) # Обновление статуса на Process
    ticket = cursor.execute("SELECT group_message_id, channel_message_id FROM tickets WHERE request_id =?", (argument_id,)).fetchone() # Достаём тикет по ID и получает ID сообщения для ответа
    message = cursor.execute("SELECT message FROM tickets WHERE request_id =?", (argument_id,)).fetchone()[0].replace("🔴️️️️️️", "🟡").replace("#НЕ_ОТВЕЧЕНО", "#В_РАБОТЕ")
    cursor.execute("UPDATE tickets set message =? WHERE request_id =?", (message, argument_id))
    base.commit()
    params = [ticket[0], ticket[1], message]
    return params

async def get_user(argument_id): # Достаём пользователя по переданному аргументу
    user = cursor.execute("SELECT user_id from tickets WHERE request_id =?", (argument_id,)).fetchone()[0]
    base.commit
    return user
    
async def close_ticket(argument_id):
    cursor.execute("UPDATE tickets set status =? WHERE request_id =?", ("close", argument_id)) # Обновление статуса на Close
    ticket = cursor.execute("SELECT group_message_id, channel_message_id FROM tickets WHERE request_id =?", (argument_id,)).fetchone() # Достаём тикет по ID и получает ID сообщения для ответа
    message = cursor.execute("SELECT message FROM tickets WHERE request_id =?", (argument_id,)).fetchone()[0].replace("🟡", "🟢").replace("#В_РАБОТЕ", "#ЗАКРЫТО")
    cursor.execute("UPDATE tickets set message =? WHERE request_id =?", (message, argument_id))
    base.commit()
    params = [ticket[0], ticket[1], message]
    return params
    
async def is_support(user_id):
    try:
        support = cursor.execute("SELECT is_support FROM users WHERE user_id =?", (user_id,)).fetchone()[0] # Без ошибки, т.к. пользователь уже есть в системе
    except:
        support = 0
    return support

async def set_support(user_id):
    check_support = cursor.execute("SELECT is_support FROM users WHERE user_id=?", (user_id,)).fetchone()
    if check_support is None:
        cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?)", (user_id, None, True, False, False))
        base.commit()
    else:
        try:
            if check_support[0] == 1:
                # Уже саппорт
                return "Пользователь уже действующий саппорт"
            elif check_support[0] == 0:
                username = cursor.execute("SELECT username FROM users WHERE user_id=?", (user_id,)).fetchone()
                cursor.execute("UPDATE users set is_support =? WHERE user_id=?", (1, user_id,))
                base.commit()
                return f"{username[0]} был назначен саппортом"
        except:
            return "ID передан неверно"
    
async def un_support(user_id):
    check_support = cursor.execute("SELECT is_support FROM users WHERE user_id=?", (user_id,)).fetchone()
    try:
        if check_support[0] == 0:
            # Уже саппорт
            return "Пользователь не имел прав саппорта"
        elif check_support[0] == 1:
            username = cursor.execute("SELECT username FROM users WHERE user_id=?", (user_id,)).fetchone()
            cursor.execute("UPDATE users set is_support =? WHERE user_id=?", (0, user_id,))
            base.commit()
            return f"{username[0]} лишён прав саппорта"
    except:
        return "ID передан неверно"
    
async def supports():
    support_list = cursor.execute("SELECT username, user_id FROM users WHERE is_support=?", (True,)).fetchall()
    if not support_list:
        return "Список саппортов пуст"
    else:
        list = []
        for i in support_list:
            list.append('Саппорт: ' + str(i[0]) + ' id: ' + str(i[1]))
        result = '\n'.join(list)
        return result
    
async def check_thread_id(thread_id):
    thread = cursor.execute("SELECT user_id FROM tickets WHERE group_message_id=?", (thread_id,)).fetchone()[0]
    return thread

async def ban(user_id):
    try:
        username = cursor.execute("SELECT username, is_banned FROM users WHERE user_id=?", (user_id,)).fetchone()
        if username[1] == 1:
            return "Пользователь уже заблокирован"
        else:
            cursor.execute("UPDATE users set is_banned =? WHERE user_id=?", (1, user_id,))
            base.commit()
            return f"Пользователь {username[0]} заблокирован"
    except:
        return "Неверный ID"

async def unban(user_id):
    try:
        username = cursor.execute("SELECT username, is_banned FROM users WHERE user_id=?", (user_id,)).fetchone()
        if username[1] == 0:
            return "Пользователь не заблокирован"
        else:
            cursor.execute("UPDATE users set is_banned =? WHERE user_id=?", (0, user_id,))
            base.commit()
            return f"Пользователь {username[0]} разблокирован"
    except:
        return "Неверный ID"


async def check_banned(user_id):
    user = cursor.execute("SELECT is_banned FROM users WHERE user_id=?", (user_id,)).fetchone()
    return user[0]

async def all():
    users = cursor.execute("SELECT user_id FROM users").fetchall()
    return users