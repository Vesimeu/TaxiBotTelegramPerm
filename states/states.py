from aiogram.dispatcher.filters.state import State, StatesGroup

class RegisterState(StatesGroup):
    """
    Состояния для регистрации пользователя.
    """
    phone = State()  # Шаг 1: Ввод номера телефона
    role = State()   # Шаг 2: Выбор роли (пассажир или водитель)
    driver_code = State()  # Шаг 3: Ввод кода для водителя
    car_model = State()    # Шаг 4: Ввод марки и модели машины
    car_number = State()   # Шаг 5: Ввод номера машины
    car_photo = State()    # Шаг 6: Отправка фото машины
    location = State()     # Шаг 7: Отправка геолокации

from aiogram.dispatcher.filters.state import State, StatesGroup

class OrderState(StatesGroup):
    start_location = State()  # Начальная точка
    end_location = State()    # Конечная точка
    price = State()           # Цена
    comment = State()         # Комментарий
    confirmation = State()    # Подтверждение

class DriverState(StatesGroup):
    """
    Состояния для работы водителя.
    """
    accept_order = State()  # Шаг 1: Принятие заказа
    complete_order = State()  # Шаг 2: Завершение заказа