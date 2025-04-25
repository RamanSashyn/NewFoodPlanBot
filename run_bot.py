import os
import django
import asyncio
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FoodPlanBot.settings')
django.setup()

from aiogram import Bot, Dispatcher, Router, F, types
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from asgiref.sync import sync_to_async

from bot_admin.models import Recipe, DailyRecipeLimit, UserRecipeInteraction
from bot_data.keyboards import create_inline_keyboard, private


BOT_TOKEN = "8017797463:AAHs0PihkrEE8ceBQUt_pa5IVblCXumKsy4"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

router = Router()
dp.include_router(router)


async def send_recipe(message: Message):
    global recipe
    recipe, reason = await sync_to_async(Recipe.get_recipe_for_user)(message.from_user.id)
    if recipe:
        await message.answer_photo(
             photo=types.FSInputFile(recipe.image.path),
             caption=f"🍽 {recipe.title}\n\n{recipe.description}",
             reply_markup=create_inline_keyboard()
        )
    elif reason == "empty":
        await message.answer("Рецепты пока что в доработке 👨‍🍳")
    elif reason == "limit":
        await message.answer("Вы уже получили 3 рецепта сегодня 🙃")


@router.message(F.text.lower() == 'следующий рецепт')
async def get_recipe(message: types.Message):
    await send_recipe(message)


@router.message(F.text.lower() == 'посмотреть ингредиенты')
async def get_ingredients(message: types.Message):
    def get_last_recipe():
        record = DailyRecipeLimit.objects.filter(
            tg_user_id=message.from_user.id,
            date=date.today()
        ).first()
        return record.last_recipe if record and record.last_recipe else None

    last_recipe = await sync_to_async(get_last_recipe)()

    if last_recipe:
        await message.answer(
            f"Ингредиенты для блюда «{last_recipe.title}»:\n\n{last_recipe.ingredients}"
        )
    else:
        await message.answer("Сначала получи рецепт, чтобы посмотреть ингредиенты.")


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

    await get_recipe(message)


@router.message(F.text.lower() == 'поставить лайк')
async def like_recipe(message: Message):
    def get_last_recipe():
        record = DailyRecipeLimit.objects.filter(
            tg_user_id=message.from_user.id,
            date=date.today()
        ).first()
        return record.last_recipe if record and record.last_recipe else None

    last_recipe = await sync_to_async(get_last_recipe)()

    if last_recipe:
        await sync_to_async(UserRecipeInteraction.objects.update_or_create)(
            tg_user_id=message.from_user.id,
            recipe=last_recipe,
            defaults={"liked": True}
        )
        await message.answer("❤️ Рецепт добавлен в избранное!")
    else:
        await message.answer("Сначала получи рецепт, чтобы его лайкнуть.")


@router.message(F.text.lower() == 'мои лайки')
async def show_liked_recipes(message: Message):
    def get_liked_recipes():
        return list(UserRecipeInteraction.objects.filter(
            tg_user_id=message.from_user.id,
            liked=True
        ).select_related('recipe'))

    interactions = await sync_to_async(get_liked_recipes)()

    if interactions:
        for interaction in interactions:
            recipe = interaction.recipe
            caption = (
                f"<b>{recipe.title}</b>\n\n"
                f"{recipe.description}\n\n"
                f"<i>Ингредиенты:</i>\n{recipe.ingredients}"
            )
            try:
                await message.answer_photo(
                    photo=types.FSInputFile(recipe.image.path),
                    caption=caption,
                    parse_mode="HTML"
                )
            except Exception:
                await message.answer(caption, parse_mode="HTML")
    else:
        await message.answer("Ты пока не отметил ни одного любимого рецепта.")


async def main():
    print("Бот запускается...")
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands(commands=private, scope=types.BotCommandScopeAllPrivateChats())
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
