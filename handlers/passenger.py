import logging
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from database.db import get_user, create_order, get_orders_by_user, delete_order_from_db
from states.states import OrderState
from bot import dp, bot  # Импортируем dp и bot из bot.py
import utils.geo as geo

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_passenger_keyboard():
    """
    Создает клавиатуру для пассажира.
    """
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("Создать заказ"), KeyboardButton("Мой профиль"), KeyboardButton("Мои заказы"))
    return markup
@dp.message_handler(Command("order"))
async def start_order(message: types.Message):
    """
    Обработчик команды /order.
    Начинает процесс создания заказа для пассажира.
    """
    try:
        user = get_user(message.from_user.id)

        if not user:
            await message.answer("Вы не зарегистрированы. Напишите /start, чтобы пройти регистрацию.")
            return

        if user[3] != "passenger":
            await message.answer("Этот раздел доступен только пассажирам.")
            return

        # Проверяем количество активных заказов
        active_orders = get_orders_by_user(message.from_user.id)
        if len(active_orders) >= 2:
            await message.answer("❌ У вас уже есть 2 активных заказа. Дождитесь их завершения.",
                                reply_markup=get_passenger_keyboard())
            return

        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(KeyboardButton("📍 Отправить геолокацию", request_location=True))

        await message.answer("Отправьте свою текущую геопозицию.", reply_markup=markup)
        await OrderState.start_location.set()
    except Exception as e:
        logger.error(f"Ошибка при начале заказа: {e}")
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте снова.")

@dp.message_handler(content_types=types.ContentType.LOCATION, state=OrderState.start_location)
async def set_start_location(message: types.Message, state: FSMContext):
    """
    Обработчик для получения начальной геолокации пассажира.
    Переводит пользователя к следующему шагу.
    """
    try:
        latitude = message.location.latitude
        longitude = message.location.longitude

        await state.update_data(start_lat=latitude, start_lon=longitude)
        await message.answer("Куда поедем? Введите адрес или отправьте геолокацию.")
        await OrderState.end_location.set()
    except Exception as e:
        logger.error(f"Ошибка при получении начальной геолокации: {e}")
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте снова.")

@dp.message_handler(content_types=[types.ContentType.LOCATION, types.ContentType.TEXT], state=OrderState.end_location)
async def set_end_location(message: types.Message, state: FSMContext):
    """
    Обработчик для получения конечной точки маршрута.
    Переводит пользователя к следующему шагу.
    """
    try:
        if message.location:
            latitude = message.location.latitude
            longitude = message.location.longitude
        else:
            location = geo.address_to_coords(message.text)
            if not location:
                await message.answer("Не удалось найти адрес. Попробуйте снова.")
                return
            longitude, latitude = location

        await state.update_data(end_lat=latitude, end_lon=longitude)
        await message.answer("Введите стоимость поездки в рублях (минимум 100 руб.).")
        await OrderState.price.set()
    except Exception as e:
        logger.error(f"Ошибка при получении конечной точки маршрута: {e}")
        await message.answer("Такой адрес не найден. Пожалуйста, попробуйте снова.")

@dp.message_handler(state=OrderState.price)
async def set_price(message: types.Message, state: FSMContext):
    """
    Обработчик для ввода стоимости поездки.
    Переводит пользователя к следующему шагу.
    """
    try:
        if not message.text.isdigit() or int(message.text) < 100:
            await message.answer("Цена указана некорректно. Введите число больше 100.")
            return

        price = int(message.text)
        await state.update_data(price=price)

        await message.answer("Добавьте комментарий к заказу (например, 'Нас будет двое' или 'Жду у подъезда').")
        await OrderState.comment.set()  # Переходим к этапу комментария
    except Exception as e:
        logger.error(f"Ошибка при вводе стоимости поездки: {e}")
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте снова.")

@dp.message_handler(state=OrderState.comment)
async def set_comment(message: types.Message, state: FSMContext):
    """
    Обработчик для ввода комментария к заказу.
    Переводит пользователя к подтверждению заказа.
    """
    try:
        comment = message.text
        await state.update_data(comment=comment)

        data = await state.get_data()
        start_address = geo.coords_to_address(data["start_lon"], data["start_lat"])
        end_address = geo.coords_to_address(data["end_lon"], data["end_lat"])

        order_info = (
            f"Ваш заказ:\n"
            f"🚕 Откуда: {start_address}\n"
            f"📍 Куда: {end_address}\n"
            f"💰 Цена: {data['price']}₽\n"
            f"📝 Комментарий: {comment}\n\n"
            f"Подтвердить заказ?"
        )

        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("✅ Подтвердить", "❌ Отменить")

        await message.answer(order_info, reply_markup=markup)
        await OrderState.confirmation.set()
    except Exception as e:
        logger.error(f"Ошибка при вводе комментария: {e}")
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте снова.")

@dp.message_handler(state=OrderState.confirmation)
async def confirm_order(message: types.Message, state: FSMContext):
    """
    Обработчик для подтверждения заказа.
    Сохраняет заказ в базу данных и завершает процесс.
    """
    try:
        if message.text == "❌ Отменить":
            await message.answer("Заказ отменён.", reply_markup=get_passenger_keyboard())
            await state.finish()
            return

        data = await state.get_data()

        # Проверяем количество активных заказов
        active_orders = get_orders_by_user(message.from_user.id, active_only=True)
        if len(active_orders) >= 2:
            await message.answer("❌ У вас уже есть 2 активных заказа. Дождитесь их завершения.",
                                reply_markup=get_passenger_keyboard())
            await state.finish()
            return

        # Создаем заказ
        create_order(
            user_id=message.from_user.id,
            start_lat=data["start_lat"],
            start_lon=data["start_lon"],
            end_lat=data["end_lat"],
            end_lon=data["end_lon"],
            price=data["price"],
            comment=data["comment"]
        )

        await message.answer("✅ Заказ создан! Ожидайте, пока водитель примет заказ.",
                             reply_markup=get_passenger_keyboard())
        await state.finish()
    except Exception as e:
        logger.error(f"Ошибка при подтверждении заказа: {e}")
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте снова.")


@dp.message_handler(lambda message: message.text == "Мои заказы")
async def my_orders_button(message: types.Message):
    """
    Обработчик для кнопки "Мои заказы".
    Показывает историю заказов пассажира.
    """
    await show_order_history(message)
async def show_order_history(message: types.Message):
    """
    Общая функция для отображения истории заказов.
    """
    try:
        user = get_user(message.from_user.id)

        if not user:
            await message.answer("Вы не зарегистрированы. Напишите /start, чтобы пройти регистрацию.")
            return

        if user[3] != "passenger":
            await message.answer("Этот раздел доступен только пассажирам.")
            return

        orders = get_orders_by_user(message.from_user.id)

        if not orders:
            await message.answer("У вас пока нет завершённых поездок.", reply_markup=get_passenger_keyboard())
            return

        history_text = "📜 История заказов:\n\n"
        for order in orders:
            start_address = geo.coords_to_address(order[3], order[2])
            end_address = geo.coords_to_address(order[5], order[4])
            history_text += (
                f"🆔 ID заказа: {order[0]}\n"
                f"🚖 Откуда: {start_address}\n"
                f"📍 Куда: {end_address}\n"
                f"💰 Цена: {order[6]}₽\n\n"
            )

        # Добавляем инлайн-клавиатуру с кнопками удаления
        await message.answer(history_text, reply_markup=get_delete_orders_keyboard(orders))
    except Exception as e:
        logger.error(f"Ошибка при получении истории заказов: {e}")
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте снова.")

def get_delete_orders_keyboard(orders):
    """
    Создает инлайн-клавиатуру с кнопками удаления заказов.
    """
    markup = InlineKeyboardMarkup()
    for order in orders:
        markup.add(InlineKeyboardButton(f"❌ Удалить заказ #{order[0]}", callback_data=f"delete_order_{order[0]}"))
    return markup

@dp.callback_query_handler(lambda callback: callback.data.startswith("delete_order_"))
async def delete_order(callback: types.CallbackQuery):
    """
    Обработчик для удаления заказа.
    """
    try:
        order_id = int(callback.data.split("_")[2])  # Извлекаем ID заказа
        delete_order_from_db(order_id)  # Удаляем заказ из базы данных

        await callback.answer(f"Заказ #{order_id} удалён.")
        await callback.message.answer("Заказ удалён.", reply_markup=get_passenger_keyboard())
    except Exception as e:
        logger.error(f"Ошибка при удалении заказа: {e}")
        await callback.answer("Произошла ошибка. Пожалуйста, попробуйте снова.")
