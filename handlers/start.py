import logging
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from database.db import add_user, get_user
from handlers.passenger import start_order, get_passenger_keyboard
from states.states import RegisterState
from bot import dp, bot  # Импортируем dp и bot из bot.py

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



def get_orders_keyboard(orders):
    """
    Создает клавиатуру с заказами и кнопками "Удалить".
    """
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for order in orders:
        markup.add(KeyboardButton(f"🚖 Заказ #{order[0]}"), KeyboardButton(f"❌ Удалить заказ #{order[0]}"))
    markup.add(KeyboardButton("Назад"))
    return markup

@dp.message_handler(Command("start"))
async def start(message: types.Message):
    """
    Обработчик команды /start.
    Проверяет, зарегистрирован ли пользователь, и предлагает отправить номер телефона.
    """
    try:
        user = get_user(message.from_user.id)

        if user:
            if user[3] == "passenger":
                # Показываем клавиатуру для пассажира
                await message.answer("Вы уже зарегистрированы! Выберите действие:", reply_markup=get_passenger_keyboard())
            else:
                # Логика для водителя (пока не трогаем)
                await message.answer("Вы водитель. Ваши функции пока не реализованы.")
            return

        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(KeyboardButton("📱 Отправить номер", request_contact=True))

        await message.answer("Привет! Отправьте свой номер телефона для регистрации.", reply_markup=markup)
        await RegisterState.phone.set()
    except Exception as e:
        logger.error(f"Ошибка в обработчике /start: {e}")
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте снова.")

@dp.message_handler(content_types=types.ContentType.CONTACT, state=RegisterState.phone)
async def register_phone(message: types.Message, state: FSMContext):
    """
    Обработчик для получения номера телефона пользователя.
    Переводит пользователя в состояние выбора роли.
    """
    try:
        phone = message.contact.phone_number
        user_id = message.from_user.id

        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("🚖 Я пассажир", "🚗 Я водитель")

        await state.update_data(phone=phone)
        await message.answer("Выберите свою роль:", reply_markup=markup)
        await RegisterState.role.set()
    except Exception as e:
        logger.error(f"Ошибка при регистрации номера телефона: {e}")
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте снова.")

@dp.message_handler(state=RegisterState.role)
async def register_role(message: types.Message, state: FSMContext):
    """
    Обработчик для выбора роли пользователя (пассажир или водитель).
    Завершает регистрацию и сохраняет данные в базу данных.
    """
    try:
        role = "passenger" if message.text == "🚖 Я пассажир" else "driver"

        data = await state.get_data()
        phone = data["phone"]
        add_user(message.from_user.id, phone, role)

        # Создаем клавиатуру с кнопками
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(KeyboardButton("Мой профиль"), KeyboardButton("Создать заказ"))

        await state.finish()
        await message.answer(f"Регистрация завершена!. Выберите действие:", reply_markup=markup)
    except Exception as e:
        logger.error(f"Ошибка при выборе роли: {e}")
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте снова.")

@dp.message_handler(lambda message: message.text == "Мой профиль")
async def show_profile(message: types.Message):
    """
    Обработчик для кнопки "Мой профиль".
    Показывает информацию о профиле пользователя.
    """
    try:
        user = get_user(message.from_user.id)

        if not user:
            await message.answer("Вы не зарегистрированы. Напишите /start, чтобы пройти регистрацию.")
            return

        profile_info = (
            f"📱 Ваш номер телефона: {user[2]}\n"
            f"🚶 Ваша роль: {user[3]}\n"
        )

        await message.answer(profile_info)
    except Exception as e:
        logger.error(f"Ошибка при показе профиля: {e}")
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте снова.")

@dp.message_handler(lambda message: message.text == "Создать заказ")
async def create_order_handler(message: types.Message):
    """
    Обработчик для кнопки "Создать заказ".
    Перенаправляет пользователя на процесс создания заказа.
    """
    try:
        user = get_user(message.from_user.id)

        if not user:
            await message.answer("Вы не зарегистрированы. Напишите /start, чтобы пройти регистрацию.")
            return

        if user[3] != "passenger":
            await message.answer("Этот раздел доступен только пассажирам.")
            return

        # Перенаправляем на команду /order
        await start_order(message)
    except Exception as e:
        logger.error(f"Ошибка при создании заказа: {e}")
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте снова.")