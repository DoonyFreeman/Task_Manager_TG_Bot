from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from datetime import datetime, timedelta


def main_menu() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="📋 Мои задачи"), KeyboardButton(text="➕ Добавить задачу")
    )
    builder.row(
        KeyboardButton(text="✅ Выполненные"), KeyboardButton(text="🗑️ Удалить задачу")
    )
    return builder.as_markup(resize_keyboard=True)


def cancel_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="❌ Отмена"))
    return builder.as_markup(resize_keyboard=True)


def date_selection_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    today = datetime.now()
    dates = [
        (today, "Сегодня"),
        (today + timedelta(days=1), "Завтра"),
        (today + timedelta(days=2), "Послезавтра"),
    ]
    for date, label in dates:
        builder.add(
            InlineKeyboardButton(
                text=f"📅 {label} ({date.strftime('%d.%m')})",
                callback_data=f"date_{date.strftime('%Y-%m-%d')}",
            )
        )
    builder.adjust(2)
    return builder.as_markup()


def time_selection_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    times = [
        ("09:00", "🌅 Утро 09:00"),
        ("10:00", "☀️ 10:00"),
        ("11:00", "📌 11:00"),
        ("12:00", "🏃 12:00"),
        ("14:00", "☀️ 14:00"),
        ("16:00", "📌 16:00"),
        ("18:00", "🌆 18:00"),
        ("20:00", "🌙 20:00"),
        ("21:00", "😴 21:00"),
    ]
    for time, label in times:
        builder.add(InlineKeyboardButton(text=label, callback_data=f"time_{time}"))
    builder.adjust(3)
    return builder.as_markup()


def confirm_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_yes")
    )
    builder.add(InlineKeyboardButton(text="❌ Отмена", callback_data="confirm_no"))
    return builder.as_markup()


def tasks_list_kb(tasks: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for task in tasks:
        time_str = task.remind_at.strftime("%d.%m %H:%M")
        builder.add(
            InlineKeyboardButton(
                text=f"⏰ {time_str} — {task.text[:30]}...",
                callback_data=f"task_{task.id}",
            )
        )
    builder.adjust(1)
    return builder.as_markup()


def task_action_kb(task_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="✅ Выполнено", callback_data=f"done_{task_id}")
    )
    builder.add(InlineKeyboardButton(text="🗑️ Удалить", callback_data=f"del_{task_id}"))
    builder.add(InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_tasks"))
    return builder.as_markup()
