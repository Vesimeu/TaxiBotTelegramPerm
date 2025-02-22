import logging
from aiogram import types
from aiogram.dispatcher.filters import Command
from database.db import get_user, get_available_orders, accept_order, get_order_by_id
from bot import dp, bot  # Импортируем dp и bot из bot.py
import utils.geo as geo
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dp.message_handler(Command("orders"))
async def list_orders(message: types.Message):
    """
    Обработчик команды /orders.
    Показывает список доступных заказов для водителя.
    """
    try:
        user = get_user(message.from_user.id)

        if not user:
            await message.answer("Вы не зарегистрированы. Напишите /start, чтобы пройти регистрацию.")
            return

        if user[3] != "driver":
            await message.answer("Этот раздел доступен только водителям.")
            return

        orders = get_available_orders()

        if not orders:
            await message.answer("🚖 Сейчас нет доступных заказов. Попробуйте позже.")
            return

        for order in orders:
            start_address = geo.coords_to_address(order[2], order[3])
            end_address = geo.coords_to_address(order[4], order[5])
            text = (
                f"🚕 Заказ #{order[0]}\n"
                f"📍 Откуда: {start_address}\n"
                f"🏁 Куда: {end_address}\n"
                f"💰 Цена: {order[6]}₽\n"
                "Чтобы принять заказ, отправьте /accept <номер заказа>"
            )
            await message.answer(text)
    except Exception as e:
        logger.error(f"Ошибка при получении списка заказов: {e}")
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте снова.")

@dp.message_handler(Command("accept"))
async def accept_order_handler(message: types.Message):
    """
    Обработчик команды /accept.
    Принимает заказ водителем.
    """
    try:
        user = get_user(message.from_user.id)

        if not user:
            await message.answer("Вы не зарегистрированы. Напишите /start, чтобы пройти регистрацию.")
            return

        if user[3] != "driver":
            await message.answer("Этот раздел доступен только водителям.")
            return

        try:
            order_id = int(message.text.split()[1])
        except (IndexError, ValueError):
            await message.answer("❌ Укажите номер заказа после команды, например: /accept 5")
            return

        order = get_order_by_id(order_id)

        if not order:
            await message.answer("❌ Заказ не найден.")
            return

        accept_order(order_id, message.from_user.id)

        passenger_id = order[1]
        passenger_message = (
            f"✅ Ваш заказ #{order_id} принят!\n"
            f"🚗 Водитель скоро прибудет."
        )
        await bot.send_message(passenger_id, passenger_message)

        await message.answer(f"Вы приняли заказ #{order_id}. Свяжитесь с пассажиром и начните поездку.")
    except Exception as e:
        logger.error(f"Ошибка при принятии заказа: {e}")
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте снова.")