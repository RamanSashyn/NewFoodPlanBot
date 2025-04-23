from aiogram.types import BotCommand
from aiogram import types


def create_inline_keyboard():
    kb = [
        [
            types.KeyboardButton(text="Следующий"),
        ],
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
    )
    return keyboard


private = [
    BotCommand(command='start', description='Запустить бота'),
]