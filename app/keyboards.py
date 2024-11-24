from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton

reply = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Получить рекомендацию')],
    [KeyboardButton(text='Узнать цвет своего вкуса')],
], resize_keyboard=True, input_field_placeholder='Выберите пункт меню')

async def create_inline_keyboard(inline_buttons):
    keyboard = InlineKeyboardBuilder()
    for s in inline_buttons:
        keyboard.add(InlineKeyboardButton(text=s, callback_data=s))
    return keyboard.adjust(1).as_markup()
