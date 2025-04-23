import os
import django
import asyncio
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FoodPlanBot.settings')
django.setup()

from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Router
from asgiref.sync import sync_to_async

from bot_admin.models import Recipe, DailyRecipeLimit

BOT_TOKEN = "7649928424:AAGNpZk9rzoeNgyxEyo71i5389w3ahY9y1U"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)


@router.message(Command("start"))
async def welcome_and_send_recipe(message: Message):
    # Приветственное сообщение
    try:
        await message.answer_photo(
            photo=types.FSInputFile("media/welcome_dish.jpg"),
            caption=(
                "Добро пожаловать в <b>FoodPlan</b>!\n\n"
                "Каждый день мы подбираем для вас вкусное, простое и бюджетное блюдо."
            ),
            parse_mode="HTML"
        )
    except Exception:
        await message.answer(
            "Добро пожаловать в FoodPlan!\n\n"
            "Каждый день мы подбираем для вас вкусное, простое и бюджетное блюдо."
        )

    # Получение рецепта
    recipe = await sync_to_async(Recipe.get_recipe_for_user)(message.from_user.id)

    if recipe:
        caption = (
            f"<b>{recipe.title}</b>\n\n"
            f"{recipe.description}\n\n"
            f"<i>Ингредиенты:</i>\n{recipe.ingredients}"
        )
        await message.answer_photo(
            photo=types.FSInputFile(recipe.image.path),
            caption=caption,
            parse_mode="HTML"
        )
    else:
        await message.answer("Вы уже получили 3 рецепта сегодня")

# Список покупок по последнему рецепту
@router.message(Command("buylist"))
async def show_ingredients(message: Message):
    record = await sync_to_async(
        lambda: DailyRecipeLimit.objects.filter(
            tg_user_id=message.from_user.id,
            date=date.today()
        ).first()
    )()

    if record and record.last_recipe:
        await message.answer(
            f"Список покупок для блюда «{record.last_recipe.title}»:\n\n{record.last_recipe.ingredients}"
        )
    else:
        await message.answer(
            "Сегодня ещё не было выбранного блюда. Напиши /start, чтобы получить рецепт."
        )


async def main():
    print("Бот запускается...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())