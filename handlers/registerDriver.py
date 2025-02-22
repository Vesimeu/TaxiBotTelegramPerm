import logging
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from database.db import add_user, get_user
from states.states import RegisterState
from bot import dp, bot  # Импортируем dp и bot из bot.py
from utils.geo import coords_to_address

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dp.message_handler(state=RegisterState.role)
async def register_driver(message: types.Message, state: FSMContext):
    """
    Обработчик для регистрации водителя.
    Запрашивает код для подтверждения роли водителя.
    """
    try:
        if message.text == "🚗 Я водитель":
            await message.answer("Напишите код. Если у вас его нет, и вы хотите стать таксистом, то напишите сюда: @vesimeu",
                                reply_markup=types.ReplyKeyboardRemove())
            await RegisterState.driver_code.set()
        else:
            await message.answer("Вы выбрали роль пассажира.")
    except Exception as e:
        logger.error(f"Ошибка при регистрации водителя: {e}")
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте снова.")

@dp.message_handler(state=RegisterState.driver_code)
async def taxi_password(message: types.Message, state: FSMContext):
    """
    Обработчик для проверки кода водителя.
    Если код верный, переводит пользователя к следующему шагу.
    """
    try:
        if message.text == '2907':
            await message.answer("Успешно! Введите марку и модель машины.")
            await RegisterState.car_model.set()
        else:
            await message.answer("Неверный код. Попробуйте снова.")
    except Exception as e:
        logger.error(f"Ошибка при проверке кода водителя: {e}")
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте снова.")

@dp.message_handler(state=RegisterState.car_model)
async def machine_firm(message: types.Message, state: FSMContext):
    """
    Обработчик для ввода марки и модели машины.
    Переводит пользователя к следующему шагу.
    """
    try:
        firm = message.text
        await state.update_data(car_model=firm)
        await message.answer("Введите номер машины.")
        await RegisterState.car_number.set()
    except Exception as e:
        logger.error(f"Ошибка при вводе марки машины: {e}")
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте снова.")

@dp.message_handler(state=RegisterState.car_number)
async def car_numbers_def(message: types.Message, state: FSMContext):
    """
    Обработчик для ввода номера машины.
    Переводит пользователя к следующему шагу.
    """
    try:
        car_numbers = message.text
        if 6 <= len(car_numbers) <= 9:
            await state.update_data(car_number=car_numbers)
            await message.answer("Отправьте фото машины.")
            await RegisterState.car_photo.set()
        else:
            await message.answer("Некорректный номер машины! Напишите корректный номер.")
    except Exception as e:
        logger.error(f"Ошибка при вводе номера машины: {e}")
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте снова.")

@dp.message_handler(content_types=types.ContentType.PHOTO, state=RegisterState.car_photo)
async def handle_docs_photo(message: types.Message, state: FSMContext):
    """
    Обработчик для получения фото машины.
    Сохраняет фото и переводит пользователя к следующему шагу.
    """
    try:
        file_info = await bot.get_file(message.photo[-1].file_id)
        downloaded_file = await bot.download_file(file_info.file_path)

        data = await state.get_data()
        car_numbers = data["car_number"]
        src = f'photo_cars/{car_numbers}.jpg'

        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file.read())

        await state.update_data(car_photo=src)
        await message.answer("Включите GPS и отправьте вашу геолокацию.🌐")
        await RegisterState.location.set()
    except Exception as e:
        logger.error(f"Ошибка при обработке фото машины: {e}")
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте снова.")

@dp.message_handler(content_types=types.ContentType.LOCATION, state=RegisterState.location)
async def geo_location_driver(message: types.Message, state: FSMContext):
    """
    Обработчик для получения геолокации водителя.
    Завершает регистрацию водителя.
    """
    try:
        latitude = message.location.latitude
        longitude = message.location.longitude

        data = await state.get_data()
        phone = data["phone"]
        car_model = data["car_model"]
        car_number = data["car_number"]
        car_photo = data["car_photo"]

        # Сохраняем данные водителя в базу данных
        add_user(message.from_user.id, phone, "driver")
        # Здесь можно добавить сохранение данных о машине и геолокации в базу данных

        await state.finish()
        await message.answer("Регистрация завершена! Теперь вы можете принимать заказы.")
    except Exception as e:
        logger.error(f"Ошибка при регистрации водителя: {e}")
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте снова.")