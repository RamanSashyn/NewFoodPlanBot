import os
import django
import asyncio

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FoodPlanBot.settings')
django.setup()

from aiogram import Bot, Dispatcher, Router, F, types
from aiogram.types import Message
from aiogram.fsm.storage.memory import MemoryStorage
from bot_admin.models import Recipe
from asgiref.sync import sync_to_async
from aiogram.filters import Command
from bot_data.keyboards import create_inline_keyboard, private


BOT_TOKEN = "8147998562:AAFeqmcUZIuEqSFxi0VM2OlpT8GHW9-7p3M"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

router = Router()
dp.include_router(router)


@router.message(Command("start"))
async def send_recipe(message: Message):
    recipe = await sync_to_async(Recipe.get_recipe_for_user)(message.from_user.id)

    if recipe:
        await message.answer_photo(
             photo=types.FSInputFile(recipe.image.path),
             caption=f"🍽 {recipe.title}\n\n{recipe.description}",
             reply_markup=create_inline_keyboard()
        )
    else:
        await message.answer("Вы уже получили 3 рецепта сегодня 🙃")


@router.message(F.text.lower() == 'следующий')
async def with_puree(message: types.Message):
    await send_recipe(message)


async def main():
    print("✅ Бот запускается...")
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands(commands=private, scope=types.BotCommandScopeAllPrivateChats())
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())