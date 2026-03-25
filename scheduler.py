import asyncio
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from database import get_task_by_id, mark_done
from aiogram import Bot

scheduler = AsyncIOScheduler()


async def send_reminder(bot: Bot, task_id: int, user_id: int, text: str):
    await bot.send_message(
        chat_id=user_id,
        text=f"🔔 <b>Напоминание!</b>\n\n📝 {text}\n\nЧтобы отметить выполненной — /done",
        parse_mode="HTML",
    )
    mark_done(task_id)


def schedule_reminder(
    bot: Bot, task_id: int, user_id: int, text: str, remind_at: datetime
):
    if remind_at > datetime.now():
        scheduler.add_job(
            send_reminder,
            trigger=DateTrigger(run_date=remind_at),
            args=[bot, task_id, user_id, text],
            id=str(task_id),
            replace_existing=True,
        )


def start_scheduler(bot: Bot):
    scheduler.start()


def stop_scheduler():
    scheduler.shutdown()
