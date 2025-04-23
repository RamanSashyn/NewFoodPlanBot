from aiogram.types import BotCommand
from aiogram import types


def create_inline_keyboard():
    kb = [
        [
            types.KeyboardButton(text="Следующий рецепт"),
            types.KeyboardButton(text="Посмотреть ингредиенты"),
        ],
        [
            types.KeyboardButton(text="Поставить лайк"),
            types.KeyboardButton(text="Мои лайки"),
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