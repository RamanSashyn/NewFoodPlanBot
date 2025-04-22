import os
import django
import asyncio

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FoodPlanBot.settings')
django.setup()

from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command
from bot_admin.models import Recipe
from asgiref.sync import sync_to_async

BOT_TOKEN = "7649928424:AAGNpZk9rzoeNgyxEyo71i5389w3ahY9y1U"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

from aiogram import Router
router = Router()
dp.include_router(router)

@router.message(Command("start"))
async def send_recipe(message: Message):
    recipe = await sync_to_async(Recipe.get_recipe_for_user)(message.from_user.id)

    if recipe:
        await message.answer_photo(
             photo=types.FSInputFile(recipe.image.path),
             caption=f"🍽 {recipe.title}\n\n{recipe.description}"
        )
    else:
        await message.answer("Вы уже получили 3 рецепта сегодня 🙃")

async def main():
    print("✅ Бот запускается...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
