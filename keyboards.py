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
    builder.add(
        InlineKeyboardButton(
            text="📅 Другой день (календарь)",
            callback_data="show_calendar",
        )
    )
    builder.adjust(2)
    return builder.as_markup()


def calendar_kb(year: int, month: int) -> InlineKeyboardMarkup:
    """Генерирует inline-календарь на месяц"""
    builder = InlineKeyboardBuilder()

    month_names = [
        "",
        "Январь",
        "Февраль",
        "Март",
        "Апрель",
        "Май",
        "Июнь",
        "Июль",
        "Август",
        "Сентябрь",
        "Октябрь",
        "Ноябрь",
        "Декабрь",
    ]

    prev_month = (month - 1) if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = (month + 1) if month < 12 else 1
    next_year = year if month < 12 else year + 1

    builder.row(
        InlineKeyboardButton(
            text="◀️", callback_data=f"cal_nav_{prev_year}_{prev_month}"
        ),
        InlineKeyboardButton(
            text=f"{month_names[month]} {year}", callback_data="cal_nop"
        ),
        InlineKeyboardButton(
            text="▶️", callback_data=f"cal_nav_{next_year}_{next_month}"
        ),
    )

    days_of_week = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    for day in days_of_week:
        builder.add(InlineKeyboardButton(text=day, callback_data="cal_nop"))

    first_day = datetime(year, month, 1)
    last_day = datetime(year, month, 1).replace(
        month=month + 1 if month < 12 else 1, year=year if month < 12 else year + 1
    ) - timedelta(days=1)

    start_weekday = first_day.weekday()
    if start_weekday == 6:
        start_weekday = 0
    else:
        start_weekday += 1

    empty_cells = start_weekday
    total_cells = empty_cells + last_day.day

    row = []
    for i in range(empty_cells):
        builder.add(InlineKeyboardButton(text=" ", callback_data="cal_nop"))

    today = datetime.now()
    for day in range(1, last_day.day + 1):
        day_date = datetime(year, month, day)
        if day_date.date() < today.date():
            builder.add(InlineKeyboardButton(text=str(day), callback_data="cal_nop"))
        else:
            builder.add(
                InlineKeyboardButton(
                    text=str(day), callback_data=f"cal_day_{year}_{month:02d}_{day:02d}"
                )
            )

    remaining = 7 - (total_cells % 7)
    if remaining < 7:
        for _ in range(remaining):
            builder.add(InlineKeyboardButton(text=" ", callback_data="cal_nop"))

    builder.add(
        InlineKeyboardButton(text="🔙 Быстрый выбор даты", callback_data="cal_back")
    )

    builder.adjust(7)
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
