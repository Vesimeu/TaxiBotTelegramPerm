# from aiogram import types
# from .admin import *
# from .driver import *
# from .passenger import *
# from .start import *
# from states.states import RegisterState
# from states.order import OrderState
#
# def register_handlers(dp):
#     # Регистрация всех хэндлеров
#     dp.register_message_handler(start, commands=["start"])
#     dp.register_message_handler(register_phone, content_types=types.ContentType.CONTACT, state=RegisterState.phone)
#     dp.register_message_handler(register_role, state=RegisterState.role)
#     dp.register_message_handler(list_users, commands=["users"])
#     dp.register_message_handler(ban_user_handler, commands=["ban"])
#     dp.register_message_handler(unban_user_handler, commands=["unban"])
#     dp.register_message_handler(list_banned_users, commands=["banned"])
#     dp.register_message_handler(order_stats, commands=["stats"])
#     dp.register_message_handler(list_orders, commands=["orders"])
#     dp.register_message_handler(accept_order_handler, commands=["accept"])
#     dp.register_message_handler(start_order, commands=["order"])
#     dp.register_message_handler(set_start_location, content_types=types.ContentType.LOCATION, state=OrderState.start_location)
#     dp.register_message_handler(set_end_location, state=OrderState.end_location)
#     dp.register_message_handler(set_price, state=OrderState.price)
#     dp.register_message_handler(confirm_order, state=OrderState.confirmation)
#     dp.register_message_handler(order_history, commands=["history"])