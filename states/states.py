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

class OrderState(StatesGroup):
    """
    Состояния для создания заказа.
    """
    start_location = State()  # Шаг 1: Начальная точка маршрута
    end_location = State()    # Шаг 2: Конечная точка маршрута
    price = State()           # Шаг 3: Ввод стоимости поездки
    confirmation = State()    # Шаг 4: Подтверждение заказа

class DriverState(StatesGroup):
    """
    Состояния для работы водителя.
    """
    accept_order = State()  # Шаг 1: Принятие заказа
    complete_order = State()  # Шаг 2: Завершение заказа