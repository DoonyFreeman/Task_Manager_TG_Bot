from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime, timedelta
import database as db
from keyboards import (
    main_menu,
    cancel_kb,
    date_selection_kb,
    time_selection_kb,
    confirm_kb,
    tasks_list_kb,
    task_action_kb,
)
from scheduler import schedule_reminder

router = Router()


class TaskStates(StatesGroup):
    waiting_text = State()
    waiting_date = State()
    waiting_time = State()
    confirming = State()


@router.message(F.text == "📋 Мои задачи")
async def show_tasks(message: Message, state: FSMContext):
    tasks = db.get_tasks(message.from_user.id)
    if not tasks:
        await message.answer(
            "📭 У тебя пока нет задач. Нажми «➕ Добавить задачу»",
            reply_markup=main_menu(),
        )
    else:
        await message.answer(
            f"📋 <b>Твои задачи ({len(tasks)}):</b>",
            parse_mode="HTML",
            reply_markup=tasks_list_kb(tasks),
        )


@router.message(F.text == "✅ Выполненные")
async def show_done(message: Message):
    all_tasks = db.get_tasks(message.from_user.id, include_done=True)
    done_tasks = [t for t in all_tasks if t.is_done]
    if not done_tasks:
        await message.answer("✅ Нет выполненных задач", reply_markup=main_menu())
    else:
        text = "✅ <b>Выполненные:</b>\n\n"
        for t in done_tasks:
            text += f"• {t.text[:40]} — {t.remind_at.strftime('%d.%m')}\n"
        await message.answer(text, parse_mode="HTML", reply_markup=main_menu())


@router.message(F.text == "➕ Добавить задачу")
async def add_task_start(message: Message, state: FSMContext):
    await state.set_state(TaskStates.waiting_text)
    await message.answer("✏️ Напиши задачу:", reply_markup=cancel_kb())


@router.message(F.text == "❌ Отмена")
async def cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Отменено", reply_markup=main_menu())


@router.message(TaskStates.waiting_text)
async def task_text(message: Message, state: FSMContext):
    if len(message.text) < 2:
        await message.answer("⚠️ Задача слишком короткая")
        return
    await state.update_data(text=message.text, selected_date=None, selected_time=None)
    await state.set_state(TaskStates.waiting_date)
    await message.answer("📅 Выбери дату:", reply_markup=date_selection_kb())


@router.callback_query(F.data.startswith("date_"), TaskStates.waiting_date)
async def select_date(callback: CallbackQuery, state: FSMContext):
    date_str = callback.data.replace("date_", "")
    await state.update_data(selected_date=date_str)
    await state.set_state(TaskStates.waiting_time)
    await callback.message.edit_text(
        "🕐 Выбери время:", reply_markup=time_selection_kb()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("time_"), TaskStates.waiting_time)
async def select_time(callback: CallbackQuery, state: FSMContext, bot: Bot):
    time_str = callback.data.replace("time_", "")
    data = await state.get_data()

    date_obj = datetime.strptime(data["selected_date"], "%Y-%m-%d")
    time_obj = datetime.strptime(time_str, "%H:%M")
    remind_at = date_obj.replace(hour=time_obj.hour, minute=time_obj.minute)

    await state.update_data(selected_time=time_str, remind_at=remind_at.isoformat())
    await state.set_state(TaskStates.confirming)

    date_display = date_obj.strftime("%d.%m")
    await callback.message.edit_text(
        f"📝 <b>Проверь задачу:</b>\n\n"
        f"📌 {data['text']}\n"
        f"📅 {date_display}\n"
        f"🕐 {time_str}\n\n"
        f"<i>Всё верно?</i>",
        parse_mode="HTML",
        reply_markup=confirm_kb(),
    )
    await callback.answer()


@router.callback_query(F.data == "confirm_yes", TaskStates.confirming)
async def confirm_yes(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    remind_at = datetime.fromisoformat(data["remind_at"])

    task_id = db.add_task(
        user_id=callback.from_user.id, text=data["text"], remind_at=remind_at
    )

    schedule_reminder(
        bot=bot,
        task_id=task_id,
        user_id=callback.from_user.id,
        text=data["text"],
        remind_at=remind_at,
    )

    await state.clear()
    await callback.message.answer(
        f"✅ <b>Задача добавлена!</b>\n\n"
        f"📌 {data['text']}\n"
        f"🔔 Напомню: {remind_at.strftime('%d.%m в %H:%M')}",
        parse_mode="HTML",
        reply_markup=main_menu(),
    )
    await callback.answer("Добавлено!")


@router.callback_query(F.data == "confirm_no", TaskStates.confirming)
async def confirm_no(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("❌ Отменено", reply_markup=main_menu())
    await callback.answer()


@router.callback_query(F.data.startswith("task_"))
async def task_detail(callback: CallbackQuery):
    task_id = int(callback.data.replace("task_", ""))
    task = db.get_task_by_id(task_id)
    if not task:
        await callback.answer("❌ Задача не найдена")
        return
    await callback.message.edit_text(
        f"📝 <b>{task.text}</b>\n\n"
        f"📅 {task.remind_at.strftime('%d.%m.%Y')}\n"
        f"🕐 {task.remind_at.strftime('%H:%M')}",
        parse_mode="HTML",
        reply_markup=task_action_kb(task_id),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("done_"))
async def task_done(callback: CallbackQuery):
    task_id = int(callback.data.replace("done_", ""))
    if db.mark_done(task_id):
        await callback.message.answer("✅ Отмечено!", reply_markup=main_menu())
        await callback.answer("Выполнено!")
    else:
        await callback.answer("❌ Ошибка")


@router.callback_query(F.data.startswith("del_"))
async def task_delete(callback: CallbackQuery):
    task_id = int(callback.data.replace("del_", ""))
    if db.delete_task(task_id):
        await callback.message.answer("🗑️ Удалено!", reply_markup=main_menu())
        await callback.answer("Удалено!")
    else:
        await callback.answer("❌ Ошибка")


@router.callback_query(F.data == "back_to_tasks")
async def back_to_tasks(callback: CallbackQuery):
    tasks = db.get_tasks(callback.from_user.id)
    if not tasks:
        await callback.message.answer("📭 Нет задач", reply_markup=main_menu())
    else:
        await callback.message.edit_text(
            f"📋 <b>Твои задачи ({len(tasks)}):</b>",
            parse_mode="HTML",
            reply_markup=tasks_list_kb(tasks),
        )
    await callback.answer()


@router.message(F.text == "🗑️ Удалить задачу")
async def delete_task_menu(message: Message):
    tasks = db.get_tasks(message.from_user.id)
    if not tasks:
        await message.answer("📭 Нет задач для удаления", reply_markup=main_menu())
    else:
        await message.answer(
            "🗑️ Выбери задачу для удаления:", reply_markup=tasks_list_kb(tasks)
        )
