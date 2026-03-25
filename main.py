import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from config import BOT_TOKEN
from handlers import (
    router,
    add_task_start,
    show_tasks,
    show_done,
    delete_task_menu,
    cancel,
)
from keyboards import main_menu
from scheduler import start_scheduler, stop_scheduler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

dp.include_router(router)


@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "👋 <b>Привет! Я бот-планировщик задач.</b>\n\n"
        "Просто добавь задачу, и я напомню тебе в нужное время!\n\n"
        "📋 Используй меню ниже для управления задачами.",
        parse_mode="HTML",
        reply_markup=main_menu(),
    )


@dp.message(Command("menu"))
async def cmd_menu(message: Message):
    await message.answer("📋 Главное меню:", reply_markup=main_menu())


async def main():
    logger.info("Бот запускается...")
    start_scheduler(bot)
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        stop_scheduler()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
