from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove


inline_btn_1 = InlineKeyboardButton('Отменить рассылку', callback_data='button1')
inline_kb1 = InlineKeyboardMarkup(row_width=2).add(inline_btn_1)