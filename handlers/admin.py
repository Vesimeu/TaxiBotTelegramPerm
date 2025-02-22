from aiogram import types
from aiogram.dispatcher.filters import Command
from bot import dp, bot  # Импортируем dp и bot из bot.py
from database.db import get_all_users, ban_user, unban_user, get_banned_users, get_order_stats

ADMIN_ID = 123456789  # Замени на свой Telegram ID

def is_admin(user_id):
    return user_id == ADMIN_ID

@dp.message_handler(Command("users"))
async def list_users(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав администратора.")
        return

    users = get_all_users()

    if not users:
        await message.answer("📋 В системе пока нет пользователей.")
        return

    text = "📋 Список пользователей:\n"
    for user in users:
        text += f"👤 {user[1]} | {user[3]} | {'🚫 Забанен' if user[4] else '✅ Активен'}\n"

    await message.answer(text)

@dp.message_handler(Command("ban"))
async def ban_user_handler(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав администратора.")
        return

    try:
        user_id = int(message.text.split()[1])
    except (IndexError, ValueError):
        await message.answer("❌ Укажите ID пользователя после команды, например: /ban 123456789")
        return

    ban_user(user_id)
    await message.answer(f"🚫 Пользователь {user_id} заблокирован.")

@dp.message_handler(Command("unban"))
async def unban_user_handler(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав администратора.")
        return

    try:
        user_id = int(message.text.split()[1])
    except (IndexError, ValueError):
        await message.answer("❌ Укажите ID пользователя после команды, например: /unban 123456789")
        return

    unban_user(user_id)
    await message.answer(f"✅ Пользователь {user_id} разблокирован.")

@dp.message_handler(Command("banned"))
async def list_banned_users(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав администратора.")
        return

    users = get_banned_users()

    if not users:
        await message.answer("🚫 Нет забаненных пользователей.")
        return

    text = "🚫 Забаненные пользователи:\n"
    for user in users:
        text += f"👤 {user[1]} | {user[3]}\n"

    await message.answer(text)

@dp.message_handler(Command("stats"))
async def order_stats(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав администратора.")
        return

    total_orders, completed_orders = get_order_stats()

    await message.answer(
        f"📊 Статистика заказов:\n"
        f"Всего заказов: {total_orders}\n"
        f"Завершённых заказов: {completed_orders}"
    )
