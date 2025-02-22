from telebot import types
import telebot
import sqlite3
import math
import time
import os
from dotenv import load_dotenv

from telebot import apihelper

apihelper.SESSION_TIME_TO_LIVE = 5*60

# apihelper.proxy = {'https': 'socks5://telegram.vpn99.net:55655'}

# python files functions

from geocoder_coords import coords_to_address, addess_to_coords
from static_map_passengers import create_static_map_order  # get static map geopos for choose order

# TOKEN for bot
load_dotenv()
token = os.environ.get("token")
bot = telebot.TeleBot(token)
bot.remove_webhook()
@bot.message_handler(commands=["start"])
def start(message):
    try:
        f=open('black list')
        s=f.readlines()
        black_list= []
        for i in range(len(s)):black_list.append(int(s[i]))
        print(message.chat.id in black_list)
        print(message.chat.id , black_list)
        if not(message.chat.id in black_list):
            name = message.text
            bot.send_message(message.chat.id,
                             "Привет <b>{first_name}</b>, рад тебя видеть. Пожалуйста, отправьте мне свой номер телефона,для этого есть команда /phone".format(
                                 first_name=message.from_user.first_name), parse_mode='HTML',
                             reply_markup=types.ReplyKeyboardRemove())
            markup = types.InlineKeyboardMarkup()
            switch_button = types.InlineKeyboardButton(text='@TaxiBotPerm',
                                                       switch_inline_query="Закажи такси, и укажи стоимость поездки сам!")
            markup.add(switch_button)
            bot.send_message(message.chat.id, "Поделиться ботом:", reply_markup=markup)
            bot.send_message(message.chat.id, 'По любым вопросам можете обратиться: @vesimeu .')
            return ''
        else:
            bot.send_message(message.chat.id,'Вы в чёрном списке.')
    except:
        bot.send_message(message.chat.id,'Ошибка')
        return ''

@bot.message_handler(commands=["adminmenu"])
def adminmenu(message):
    mybd = sqlite3.connect('base.db')
    mycurs_admin = mybd.cursor()
    mycurs_admin.execute('SELECT * FROM passengers')
    pass_all = mycurs_admin.fetchall()
    c=0
    for pas in pass_all:
        c=c+1
    bot.send_message(message.chat.id,'Количество пользователей в базее данных:')
    bot.send_message(message.chat.id,c)
@bot.message_handler(commands=["phone"])
def phone(message):
    try:
        f = open('black list')
        s = f.readlines()
        black_list = []
        for i in range(len(s)): black_list.append(int(s[i]))
        print(message.chat.id in black_list)
        print(message.chat.id, black_list)
        if not (message.chat.id in black_list):
            user_markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
            button_phone = types.KeyboardButton(text="Отправить номер телефона", request_contact=True)
            user_markup.add(button_phone)
            msg = bot.send_message(message.chat.id, "Согласны ли вы предоставить ваш номер телефона для регистрации в системе?",
                                   reply_markup=user_markup)
            bot.register_next_step_handler(msg, reg_or_auth)
        else:
            bot.send_message(message.chat.id, 'Вы в чёрном списке.')
    except:
        bot.send_message(message.chat.id,'Ошибка,попробуйте написать /start')
        return ''


def reg_or_auth(message):
    try:
        input_phone = message.contact.phone_number

        # connect to base
        mydb = sqlite3.connect('base.db')
        mycursor = mydb.cursor()

        # find phone in passengers table
        mycursor.execute('SELECT * FROM taxi_drivers')
        drivers = mycursor.fetchall()
        print(drivers)
        for user in drivers:
            table_phone = user[1]
            if table_phone == input_phone:  # if user_phone find in taxi_drivers table
                # keyboard for auth taxi driver
                buttons_actions = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
                button_settings = types.KeyboardButton(text="Настройки")
                button_choose_order = types.KeyboardButton(text="Выбрать поездку")
                buttons_actions.add(button_settings)
                buttons_actions.add(button_choose_order)
                mess = bot.send_message(message.chat.id, "Выберите действие.", reply_markup=buttons_actions)
                bot.register_next_step_handler(mess, choose_action_taxi_driver, input_phone, message.chat.id)

                return ''  # stop function
        mycursor.execute('SELECT * FROM passengers')
        passengers = mycursor.fetchall()

        for user in passengers:
            table_phone = user[1]
            if table_phone == input_phone:  # if user_phone find in passengers table

                # keyboard for auth passenger
                buttons_actions = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
                button_history_ways = types.KeyboardButton(text="Мои заказы")
                button_add_order = types.KeyboardButton(text="Новая поездка")
                buttons_actions.add(button_add_order)
                buttons_actions.add(button_history_ways)
                mess = bot.send_message(message.chat.id, "Выберите действие.", reply_markup=buttons_actions)
                bot.register_next_step_handler(mess, choose_action_passenger, input_phone, message.chat.id)

                return ''  # stop function

        # if table is empty
        buttons_characters = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        button_taxi_driver = types.KeyboardButton(text="Таксист")
        button_passenger = types.KeyboardButton(text="Пассажир")
        buttons_characters.add(button_taxi_driver)
        buttons_characters.add(button_passenger)
        mess = bot.send_message(message.chat.id, "Выберите кем вы являетесь?", reply_markup=buttons_characters)
        bot.register_next_step_handler(mess, choose_character, input_phone)

    except:
        if message.text == '/start':
            mess_2 = bot.send_message(message.chat.id, "Отправляю назад,чтобы продолжить, напишите что-то",
                                      reply_markup=types.ReplyKeyboardRemove())
            bot.register_next_step_handler(mess_2, start)  # изменить на phone
        elif message.text == 'Нет':
            mess_2 = bot.send_message(message.chat.id, "Отправляю назад,чтобы продолжить, напишите что-то", reply_markup=types.ReplyKeyboardRemove())
            bot.register_next_step_handler(mess_2, start)  # изменить на phone
        elif message.text == 'нет':
            mess_2 = bot.send_message(message.chat.id, "Отправляю назад,чтобы продолжить, напишите что-то", reply_markup=types.ReplyKeyboardRemove())
            bot.register_next_step_handler(mess_2, start)  # изменить на phone
        else:
            mess = bot.send_message(message.chat.id, "Ошибка. Отправьте номер телефона через кнопку!")
            bot.register_next_step_handler(mess, reg_or_auth) # изменить на phone

@bot.message_handler(content_types=['text'])
def error_start(message):
    if message.text == '/start' or '/phone':
        bot.send_message(message.chat.id,'Напишите /phone чтобы продолжить')
        return ''

@bot.message_handler(content_types=['text'])
def choose_action_passenger(message, user_phone, teg_id = None):  # auth passenger action
        if message.text == 'Мои заказы':

            # connect to base
            mydb = sqlite3.connect('base.db')
            mycursor = mydb.cursor()

            # find orders for history orders to passenger
            mycursor.execute('SELECT * FROM orders')
            orders = mycursor.fetchall()
            c=0


            for order in orders:
                if order[1] == user_phone:
                    c=c+1
                    first_checkpoint = coords_to_address(order[2], order[3])  # start address
                    second_checkpoint = coords_to_address(order[4], order[5])  # end address
                    bot.send_message(message.chat.id,
                                     f"<i><b>Заказ №{order[0]}.</b></i>\n\n<i><b>Начальная точка:</b></i> {first_checkpoint}\n\n<i><b>Конечная точка:</b></i> {second_checkpoint}\n\n<i><b>Расстояние:</b></i> {order[7]} м\n\n<i><b>Время пути:</b></i> {order[8]} мин\n\n<b>Цена:</b> {order[6]} ₽\n\n<b>Комментарий:</b> {order[10]}",
                                     parse_mode='HTML', reply_markup=types.ReplyKeyboardRemove())
            if c==0:
                bot.send_message(message.chat.id,'На данный момент у вас нет активных заказов.')
                buttons_actions = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
                button_history_ways = types.KeyboardButton(text="Мои заказы")
                button_add_order = types.KeyboardButton(text="Новая поездка")
                buttons_actions.add(button_add_order)
                buttons_actions.add(button_history_ways)
                mess = bot.send_message(message.chat.id, "Выберите действие.", reply_markup=buttons_actions)
                bot.register_next_step_handler(mess, choose_action_passenger, user_phone, message.chat.id)
            else:
                markup_ord = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
                button_func_ord_1 = types.KeyboardButton(text="Назад")
                button_func_ord_2 = types.KeyboardButton(text="Удалить мои заказы")
                markup_ord.add(button_func_ord_1, button_func_ord_2)
                mess = bot.send_message(message.chat.id,'Выберите действие:',reply_markup=markup_ord)
                bot.register_next_step_handler(mess,error_ord,user_phone=user_phone)


        elif message.text == 'Новая поездка' or user_phone == None:
            # geolocation new order
            mydb = sqlite3.connect('base.db')
            mycursor = mydb.cursor()
            my_phone = user_phone
            ord = mycursor.execute(f"SELECT * FROM orders WHERE phone = {my_phone}")
            c = 0
            for users in ord:
                if users[1] == my_phone:
                    c = c + 1
            if c==2:
                bot.send_message(message.chat.id,'У вас привышен лимит заказов, удалите ваши заказы.')
                user_markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
                button_func_ord_1 = types.KeyboardButton(text="Мои заказы")
                button_func_ord_2 = types.KeyboardButton(text="Новая поездка")
                user_markup.add(button_func_ord_1, button_func_ord_2)
                msg = bot.send_message(message.chat.id,
                                       "Выберите действие",
                                       reply_markup=user_markup)
                bot.register_next_step_handler(msg,choose_action_passenger,user_phone=my_phone)
            else:
                keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
                button_loca = types.KeyboardButton(text="🌐 Определить местоположение", request_location=True)
                keyboard.add(button_loca)
                mess = bot.send_message(message.chat.id, "Включите GPS и отправьте вашу геолокацию.🌐", reply_markup=keyboard)
                bot.register_next_step_handler(mess, geo_location, user_phone, 'Пассажир')
        else:
            buttons_actions = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            button_history_ways = types.KeyboardButton(text="Мои заказы")
            button_add_order = types.KeyboardButton(text="Новая поездка")
            buttons_actions.add(button_add_order)
            buttons_actions.add(button_history_ways)
            mess_1 = bot.send_message(message.chat.id, 'Ошибка, выберите действие',reply_markup=buttons_actions)
            bot.register_next_step_handler(mess_1,choose_action_passenger,user_phone)

@bot.message_handler(content_types=['text'])
def error_ord(message,user_phone):
    if message.text == 'Удалить мои заказы':
        phone_us = user_phone
        mydb_ord = sqlite3.connect('base.db')
        mycursor_ord = mydb_ord.cursor()
        mycursor_ord.execute("DELETE FROM orders WHERE phone = {0}".format(phone_us))
        mydb_ord.commit()
        mess_1 = bot.send_message(message.chat.id,'Заказы успешно удалены, напшите что-нибудь чтобы продолжить.')
        bot.register_next_step_handler(mess_1,phone)
    elif message.text == 'Назад':
        mess = bot.send_message(message.chat.id,'Возращаю вас назад, напишите что нибудь чтобы продолжить.')
        bot.register_next_step_handler(mess, phone)
    else:
        mess = bot.send_message(message.chat.id, 'Ошибка,возращаю вас назад, напишите что нибудь чтобы продолжить.')
        bot.register_next_step_handler(mess, phone)
@bot.message_handler(content_types=['text'])
def error_start(message):
    if message.text == '/start' or '/phone':
        bot.send_message(message.chat.id,'Напишите /phone чтобы продолжить')
        return ''

@bot.message_handler(content_types=['text'])
def choose_action_taxi_driver(message, user_phone , teg_id):  # auth taxi driver action
    if message.text == 'Выбрать поездку':

        # connect to base
        mydb = sqlite3.connect('base.db')
        mycursor = mydb.cursor()
        print(user_phone)
        # choose order for taxi driver
        mycursor.execute(f'SELECT * FROM taxi_drivers')
        taxi_drivers = mycursor.fetchall()
        for taxi_driver in taxi_drivers:
            if taxi_driver[1] == user_phone:
                print(taxi_driver)

                keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
                button_loca = types.KeyboardButton(text="🌐 Определить местоположение", request_location=True)
                keyboard.add(button_loca)

                mess = bot.send_message(message.chat.id, "Включите GPS и отправьте вашу геолокацию.🌐", reply_markup=keyboard)
                bot.register_next_step_handler(mess, geo_location, user_phone, 'Таксист', firm=taxi_driver[2],
                                               car_numbers=taxi_driver[3], src_photo_car=taxi_driver[-2])
                break
    elif message.text == 'Настройки':
        markup_setting = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button_setting_profile = types.KeyboardButton("Удалить|Пересоздать профиль")
        button_setting_back = types.KeyboardButton("Назад")
        markup_setting.add(button_setting_profile,button_setting_back)
        mess_setting = bot.send_message(message.chat.id,'Выберите действие:',reply_markup=markup_setting)
        bot.register_next_step_handler(mess_setting,setting_taxi,user_phone,message.chat.id)

    else:
        mess_1 = bot.send_message(message.chat.id,'Ошибка, выберите действие')
        bot.register_next_step_handler(mess_1,choose_action_taxi_driver,phone,message.chat.id)

@bot.message_handler(content_types=['text'])
def setting_taxi(message,phone_taxi,teg_id):
    if message.text == 'Назад':
        bot.send_message(message.chat.id,'Возращаю назад',reply_markup=types.ReplyKeyboardRemove())
        markup_setting_back = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button_next = types.KeyboardButton('Выбрать поездку')
        markup_setting_back.add(button_next)
        mess_back = bot.send_message(message.chat.id,'Выберите действие',reply_markup=markup_setting_back)
        bot.register_next_step_handler(mess_back,choose_action_taxi_driver,phone_taxi,message.chat.id)

    elif message.text == 'Удалить|Пересоздать профиль':
        mydb = sqlite3.connect('base.db')
        mycursor_setting = mydb.cursor()
        mycursor_setting.execute("DELETE FROM taxi_drivers WHERE phone = {phone1}".format(phone1 = phone_taxi))
        mydb.commit()
        mess_delete = bot.send_message(message.chat.id,'Профиль успешно удалён.',reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(mess_delete,phone)
    else:
        mess_error_setting = bot.send_message(message.chat.id,'Не понял вас, корректно выберите дейсвтие:')
        bot.register_next_step_handler(mess_error_setting,setting_taxi,phone_taxi,message.chat.id)

@bot.message_handler(content_types=['text'])
def choose_character(message, user_phone):  # choose taxi_drivers or passenger
    if message.text == 'Таксист':
        mes = bot.send_message(message.chat.id,'Напишите код.Если у вас его нет, и вы хотите стать таксистом, то напишите сюда:@vesimeu',reply_markup=types.ReplyKeyboardRemove())
        markup_taxi = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button_taxi = types.KeyboardButton(text='Назад')
        markup_taxi.add(button_taxi)
        mes_back = bot.send_message(message.chat.id,'Можете вернуться назад:',reply_markup=markup_taxi)
        bot.register_next_step_handler(mes_back, taxi_password, phone = user_phone)
    elif message.text == 'Пассажир':
        # connect to base
        mydb = sqlite3.connect('base.db')
        mycursor = mydb.cursor()
        # Add new passenger in 'passengers' table
        sqlFormula = "INSERT INTO passengers ('phone', 'teg_id') VALUES (?,?)"
        mycursor.execute(sqlFormula, (user_phone, message.chat.id))
        mydb.commit()
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button_loca = types.KeyboardButton(text="🌐 Определить местоположение", request_location=True)
        keyboard.add(button_loca)
        mess = bot.send_message(message.chat.id, "Включите GPS и отправьте вашу геолокацию.🌐", reply_markup=keyboard)
        bot.register_next_step_handler(mess, geo_location, user_phone, 'Пассажир')

@bot.message_handler(content_types=['text'])
def taxi_password(message,phone):
    if message.text == '2907':
        bot.send_message(message.chat.id,'Успешно!')
        mess = bot.send_message(message.chat.id, "Введите марку и модель машины.",
                                reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(mess, machine_firm, phone)
    else:
        msg = bot.send_message(message.chat.id, "Возращаю назад... для продолжение что-нибудь напишите.",)
        bot.register_next_step_handler(msg, start)
@bot.message_handler(content_types=['text'])  # machine_firm
def machine_firm(message, phone):
    firm = message.text
    mess = bot.send_message(message.chat.id, "Введите номер машины.", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(mess, car_numbers_def, phone, firm)

@bot.message_handler(content_types=['text'])  # car_numbers
def car_numbers_def(message, phone, machine_firm):
    car_numbers = message.text
    car_numbers = str(car_numbers)
    if len(car_numbers) <= 9 and len(car_numbers) >= 6:
        mess = bot.send_message(message.chat.id, "Отправьте фото машины.")
        bot.register_next_step_handler(mess, handle_docs_photo, car_numbers, phone, machine_firm)
    else:
        mess_2 = bot.send_message(message.chat.id,'Некорректный номер машины!Напишите корректный номер.')
        bot.register_next_step_handler(mess_2,car_numbers_def,phone,machine_firm)


@bot.message_handler(content_types=['document'])  # function for get photo car from user
def handle_docs_photo(message, car_numbers, phone, machine_firm):
    try:
        chat_id = message.chat.id

        file_info = bot.get_file(message.photo[-1].file_id)

        downloaded_file = bot.download_file(file_info.file_path)

        src = 'photo_cars/' + car_numbers + '.jpg   ';  # save png photo name - car_numbers
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button_loca = types.KeyboardButton(text="🌐 Определить местоположение", request_location=True)
        keyboard.add(button_loca)

        mess = bot.send_message(message.chat.id, "Включите GPS и отправьте вашу геолокацию.🌐", reply_markup=keyboard)
        bot.register_next_step_handler(mess, geo_location, phone, 'Таксист', firm=machine_firm, car_numbers=car_numbers,
                                       src_photo_car=src)
    except:
        pass


@bot.message_handler(content_types=['text'])
def geo_location(message, phone = None, job = None, firm=None, car_numbers=None,
                 src_photo_car=None):  # firm and car_numbers if taxi, default passenger
    try:
        latitude = message.location.latitude #Координаты !
        longitude = message.location.longitude  #
        dict_length = {}
        address_location = coords_to_address(longitude, latitude)  # get address from coords, function file geocoder.py
        bot.send_message(message.chat.id, address_location, reply_markup=types.ReplyKeyboardRemove())

        mydb = sqlite3.connect('base.db')
        mycursor = mydb.cursor()

        if job == 'Таксист':
            c = 0
            mycursor.execute(f'SELECT * FROM taxi_drivers')
            taxi_drivers = mycursor.fetchall()
            for driver in taxi_drivers:
                if driver[1] != phone:
                    c += 1
            if c == len(taxi_drivers):
                sqlFormula = "INSERT INTO taxi_drivers ('phone', 'machine_firm', 'car_numbers', 'longitude', 'latitude', 'photo_car', 'teg_id') VALUES (?,?,?,?,?,?,?)"
                mycursor.execute(sqlFormula,(phone, firm, car_numbers, longitude, latitude, src_photo_car, message.chat.id))
                mydb.commit()

                mydb = sqlite3.connect('base.db')
                mycursor = mydb.cursor()

            mycursor.execute(f'SELECT * FROM orders')
            orders = mycursor.fetchall()
            c= 0
            for us in orders:
                user = us
                c=c+1

                first_checkpoint = coords_to_address(user[2], user[3])  # start address
                second_checkpoint = coords_to_address(user[4], user[5])  # end address
                bot.send_message(message.chat.id,
                                     f"<i><b>Заказ №{user[0]}.</b></i>\n\n<i><b>Начальная точка:</b></i> {first_checkpoint}\n\n<i><b>Конечная точка:</b></i> {second_checkpoint}\n\n<i><b>Расстояние:</b></i> {user[7]} м\n\n<i><b>Время пути:</b></i> {user[8]} мин\n\n<b>Цена:</b> {user[6]} ₽\n\n<b>Комментарий:</b> {user[-2]} ",
                                     parse_mode='HTML', reply_markup=types.ReplyKeyboardRemove())
                bot.send_message(message.chat.id, "*Введите номер заказа.*", parse_mode='markdown',
                                    reply_markup=types.ReplyKeyboardRemove())
            if c==0:
                bot.send_message(message.chat.id, 'В настоящие время заказов нет.Мы сообщим, когда появится заказ.')
            buttons_actions = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            button_obn = types.KeyboardButton(text="Обновить")
            button_back = types.KeyboardButton(text="Назад")
            buttons_actions.add(button_obn,button_back)
            mess = bot.send_message(message.chat.id, "Можете обновить список заказов, или вернуться назад.", reply_markup=buttons_actions)
            bot.register_next_step_handler(mess, choose_order,job,phone, longitude, latitude,firm,src_photo_car, car_numbers = car_numbers)

            # mess = bot.send_message(message.chat.id, "Введите номер заказа.", parse_mode='HTML',
            #                         reply_markup=types.ReplyKeyboardRemove())


        elif job == 'Пассажир' or job == 'None':
            job = 'Пассажир'
            mess = bot.send_message(message.chat.id, "<b>Куда едем?( Например: Новые Ляды, Пушкина 6 ) ИЛИ укажите точку на карте через геопозицию.</b>", parse_mode='HTML',
                                    reply_markup=types.ReplyKeyboardRemove())
            bot.register_next_step_handler(mess, where_go, phone, longitude, latitude)

        else:
            bot.send_message(message.chat.id,'Ошибка, корректно укажите геолокацию!')
            bot.register_next_step_handler(message,choose_action_passenger,phone)
    except:
        # mess_exc = bot.send_message(message.chat.id,'Произошла ошибка,возращаю вас назад..')
        # bot.register_next_step_handler(mess_exc,choose_action_passenger,phone)
        if job == 'Таксист':
            bot.send_message(message.chat.id,'Произошла ошибка')
            buttons_actions = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            button_settings = types.KeyboardButton(text="Настройки")
            button_choose_order = types.KeyboardButton(text="Выбрать поездку")
            buttons_actions.add(button_settings)
            buttons_actions.add(button_choose_order)
            mess = bot.send_message(message.chat.id, "Выберите действие.", reply_markup=buttons_actions)
            bot.register_next_step_handler(mess, choose_action_taxi_driver,phone, message.chat.id)
        else:
            buttons_geo_ex = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            button_history_ways = types.KeyboardButton(text="Мои заказы")
            button_add_order = types.KeyboardButton(text="Новая поездка")
            buttons_geo_ex.add(button_add_order)
            buttons_geo_ex.add(button_history_ways)
            mess_1 = bot.send_message(message.chat.id, 'Ошибка, выберите действие', reply_markup=buttons_geo_ex)
            bot.register_next_step_handler(mess_1, choose_action_passenger, user_phone = phone)



@bot.message_handler(content_types=['text'])
def choose_order(message,job,phone, longitude, latitude,firm,src_photo_car,car_numbers):  # num order
    if message.text == 'Обновить':
        bot.send_message(message.chat.id,'Обновляю список..')
        time.sleep(1)
        mydb = sqlite3.connect('base.db')
        mycursor = mydb.cursor()
        if job == 'Таксист':
            c = 0
            mycursor.execute(f'SELECT * FROM taxi_drivers')
            taxi_drivers = mycursor.fetchall()
            for driver in taxi_drivers:
                if driver[1] != phone:
                    c += 1
            if c == len(taxi_drivers):
                sqlFormula = "INSERT INTO taxi_drivers ('phone', 'machine_firm', 'car_numbers', 'longitude', 'latitude', 'photo_car', 'teg_id') VALUES (?,?,?,?,?,?,?)"
                mycursor.execute(sqlFormula,
                                 (phone, firm, car_numbers, longitude, latitude, src_photo_car, message.chat.id))
                mydb.commit()

                mydb = sqlite3.connect('base.db')
                mycursor = mydb.cursor()

            mycursor.execute(f'SELECT * FROM orders')
            orders = mycursor.fetchall()
            c=0
            for us in orders:
                user = us
                c=c+1
                first_checkpoint = coords_to_address(user[2], user[3])  # start address
                second_checkpoint = coords_to_address(user[4], user[5])  # end address
                bot.send_message(message.chat.id,
                                     f"<i><b>Заказ №{user[0]}.</b></i>\n\n<i><b>Начальная точка:</b></i> {first_checkpoint}\n\n<i><b>Конечная точка:</b></i> {second_checkpoint}\n\n<i><b>Расстояние:</b></i> {user[7]} м\n\n<i><b>Время пути:</b></i> {user[8]} мин\n\n<b>Цена:</b> {user[6]} ₽\n\n<b>Комментарий:</b> {user[-2]} ",
                                     parse_mode='HTML', reply_markup=types.ReplyKeyboardRemove())
                bot.send_message(message.chat.id, "*Введите номер заказа.*", parse_mode='markdown',
                                     reply_markup=types.ReplyKeyboardRemove())
            if c==0:
                bot.send_message(message.chat.id, 'Заказов пока нет, мы уведомим вас когда будет заказ.')
            buttons_actions = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            button_obn = types.KeyboardButton(text="Обновить")
            button_back = types.KeyboardButton(text="Назад")
            buttons_actions.add(button_obn, button_back)
            mess = bot.send_message(message.chat.id, "Можете обновить список заказов, или вернуться назад.",
                                    reply_markup=buttons_actions)
            bot.register_next_step_handler(mess, choose_order,job,phone, longitude, latitude,firm,src_photo_car,car_numbers=car_numbers)
    elif message.text == 'Назад':
        mes = bot.send_message(message.chat.id, 'Отправляю вас назад..')
        user_markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
        button_phone = types.KeyboardButton(text="Отправить номер телефона", request_contact=True)
        user_markup.add(button_phone)
        msg = bot.send_message(message.chat.id,
                               "Согласны ли вы предоставить ваш номер телефона для регистрации в системе?",
                               reply_markup=user_markup)
        bot.register_next_step_handler(msg, reg_or_auth)
    else:
        num_order = message.text
        mybdord = sqlite3.connect('base.db')
        mycursor_order = mybdord.cursor()
        mycursor_order.execute("SELECT * FROM orders")
        ord = mycursor_order.fetchall()
        ord_count = []
        for number_ord in ord:
            ord_count.append(number_ord[0])
        if num_order.isdigit() == True and int(num_order) in ord_count:
            num_order = int(num_order)
            mydb = sqlite3.connect('base.db')
            mycursor = mydb.cursor()
            mycursor.execute(f'SELECT * FROM orders')
            users = mycursor.fetchall()
            passenger = []
            for us in users:  # find order in table by id
                if us[0] == int(num_order):
                    passenger.append(us)

            first_checkpoint = coords_to_address(passenger[0][2], passenger[0][3])  # start address
            second_checkpoint = coords_to_address(passenger[0][4], passenger[0][5])  # end address
            bot.send_message(message.chat.id,
                             f"<i><b>Начальная точка:</b></i> {first_checkpoint}\n\n<i><b>Конечная точка:</b></i> {second_checkpoint}\n\n<i><b>Расстояние:</b></i> {passenger[0][7]} м\n\n<i><b>Время пути:</b></i> {passenger[0][8]} мин\n\n<b>Цена:</b> {passenger[0][6]} ₽\n\n<b>Комментарий:</b> {passenger[0][-2]} ",
                             parse_mode='HTML', reply_markup=types.ReplyKeyboardRemove())

            # create map_point.png for choose order
            create_static_map_order(f'{passenger[0][2]},{passenger[0][3]}',teg_id=passenger[0][-3])

            # send map_point.png to taxi driver  <i><b>Номер пассажира: {passenger[0][1]}.</b></i>\n\n
            bot.send_photo(message.chat.id, open(f'C:/TaxiBotTelegram-master/map_img/{passenger[0][-3]}.png', 'rb'));
            bot.send_message(message.chat.id,'Геопозиция на карте до пассажира.')
            bot.send_location(message.chat.id, passenger[0][5], passenger[0][4])
            bot.send_message(message.chat.id, f"Номер телефона пассажира: +{passenger[0][1]}")

            # send photo taxi_car to passenger
            mydb = sqlite3.connect('base.db')
            mycursor = mydb.cursor()
            mycursor.execute(f'SELECT * FROM taxi_drivers WHERE teg_id={message.chat.id}')
            user_taxi = mycursor.fetchall()
            src_photo_car = user_taxi[0][6]  # src_photo_car
            mydb1 = sqlite3.connect('base.db')
            mycursor1 = mydb1.cursor()
            mycursor1.execute(f'SELECT * FROM taxi_drivers WHERE teg_id={message.chat.id}')
            info_taxi = mycursor1.fetchall()
            phone_taxi = info_taxi[0][1]
            marka_taxi = info_taxi[0][2]
            number_texi = info_taxi[0][3]


            # mycursor.execute(f'SELECT * FROM taxi_drivers WHERE teg_id={message.chat.id}')
            # numbers_taxi = mycursor[]

            bot.send_message(passenger[0][-3], 'Заказ принят!')
            bot.send_message(passenger[0][-3], f"Номер таксиста: +{phone_taxi}")
            bot.send_message(passenger[0][-3], f'Марка машины: {marka_taxi}')
            bot.send_message(passenger[0][-3], f'Номер машины: {number_texi}')
            bot.send_photo(passenger[0][-3], open(src_photo_car, 'rb'));  # passenger[0][-1] - teg_id user

            sql = 'DELETE FROM orders WHERE id=?'
            mycursor.execute(sql, (int(num_order),))
            mydb.commit()
            bot.send_message(message.chat.id, 'Заказ принят!Чтобы вернуться назад напишите /phone')

        else:
            mess_1 = bot.send_message(message.chat.id, 'Введён некорректный номер заказа. Введите корректный номер заказа.')
            bot.register_next_step_handler(mess_1, choose_order,job,phone, longitude, latitude,firm,src_photo_car,car_numbers = car_numbers)


@bot.message_handler(content_types=['text'])
def where_go(message, phone=None, longitude_start=None, latitude_start=None):  # end address for passenger
    try:
        if message.text == None:
            latitude = message.location.latitude  # Координаты !
            longitude = message.location.longitude  #
            dict_length = {}

            address_location = coords_to_address(longitude, latitude)
            address_go = address_location
            longitude_end, latitude_end = [float(x) for x in addess_to_coords(address_go).split(' ')]

            mess = bot.send_message(message.chat.id,
                                    "<b>Укажите желаемую цену в ₽. Устанавливайте адеватную цену поездки, иначе заказ никто не возьмёт.Мин. ставка - 100руб.</b>",
                                    parse_mode='HTML',
                                    reply_markup=types.ReplyKeyboardRemove())
            bot.register_next_step_handler(mess, price_way, phone, longitude_start, latitude_start, longitude_end,
                                           latitude_end)
        else:
            address_go = message.text
            longitude_end, latitude_end = [float(x) for x in addess_to_coords(address_go).split(' ')]

            mess = bot.send_message(message.chat.id, "<b>Укажите желаемую цену в ₽. Устанавливайте адеватную цену поездки, иначе заказ никто не возьмёт.Мин. ставка - 100руб.</b>", parse_mode='HTML',
                                    reply_markup=types.ReplyKeyboardRemove())
            bot.register_next_step_handler(mess, price_way, phone, longitude_start, latitude_start, longitude_end, latitude_end)
    except:
        bot.send_message(message.chat.id,'Место не найдено, попробуйте ещё раз.Напишите что-нибудь чтобы продолжить.') ## ЕСЛИ НЕ ВЕРНО УКАЗАЛ КУДА
        bot.register_next_step_handler(message,choose_action_passenger,user_phone = phone)


@bot.message_handler(content_types=['text'])
def price_way(message, phone, longitude_start, latitude_start, longitude_end,
              latitude_end):  # end address for passenger
    price = message.text
    if price.isdigit() == True and len(price) <= 5 and int(price) >= 100:
        # if int(price) >= 100:
            price_way_mes = int(message.text)

            # length of way
            x1, y1 = longitude_start, latitude_start
            x2, y2 = longitude_end, latitude_end

            y = math.radians((y1 + y2) / 2)
            x = math.cos(y)
            n = abs(x1 - x2) * 111000 * x
            n2 = abs(y1 - y2) * 111000
            length_way = round(math.sqrt(n * n + n2 * n2))
            # ---------------

            # time way
            time_way = round(length_way / (40 * 1000) * 60)
            # --------

            first_checkpoint = coords_to_address(longitude_start, latitude_start)
            second_checkpoint = coords_to_address(longitude_end, latitude_end)
            mess_comment = bot.send_message(message.chat.id,'Напишите комментарий, например время подачи, сколько пассажиров, где конкретно находитесь, есть ли багаж или животные.')
            bot.register_next_step_handler(mess_comment,comment,phone, longitude_start, latitude_start, longitude_end,
              latitude_end,price_way_mes,length_way,time_way,first_checkpoint,second_checkpoint)
    else:
        mess_error = bot.send_message(message.chat.id,'Ошибка, не верно введена стоимость заказа или цена меньше 100руб.Напишите корректную стоимость поездки.')
        bot.register_next_step_handler(mess_error,price_way,phone, longitude_start, latitude_start, longitude_end,
              latitude_end)
@bot.message_handler(content_types=['text'])
def func_ord(message,phone,comment_users,price):
    if message.text == 'Да':
        phone_users_local = phone
        mybd_ord = sqlite3.connect('base.bd')
        mycursor_ord = mybd_ord.cursor()
        # mycursor_ord.execute(f"DELETE FROM orders WHERE phone = {phone_users_local} and price = {price}")
        order = mycursor_ord.fetchall()
        for value in order:
            longitube_ord = value[2]
            latitude_ord = value[3]
            mydb = sqlite3.connect('base.db')
            mycursor = mydb.cursor()
            mycursor.execute(f'SELECT * FROM taxi_drivers')
            taxi_drivers = mycursor.fetchall()
            for num in taxi_drivers:
                longitube_taxi = num[4]
                latitube_taxi = num[5]
                x1, y1 = longitube_ord, latitude_ord
                x2, y2 = longitube_taxi, latitube_taxi

                y = math.radians((y1 + y2) / 2)
                x = math.cos(y)
                n = abs(x1 - x2) * 111000 * x
                n2 = abs(y1 - y2) * 111000
                length_way = round(math.sqrt(n * n + n2 * n2))
                # ---------------

                # time way
                time_way = round(length_way / (40 * 1000) * 60)
                bot.send_message(num[-1],'Пришёл новый заказ в ' + str(length_way) + "от вас")




        bot.send_message(message.chat.id,'Отлично, ваш заказ сохранён!Ждите когда ваш заказ примут, вам придёт уведомление.',reply_markup=types.ReplyKeyboardRemove())
        user_markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
        button_func_ord_1 = types.KeyboardButton(text="Мои заказы")
        button_func_ord_2 = types.KeyboardButton(text="Новая поездка")
        user_markup.add(button_func_ord_1,button_func_ord_2)
        msg = bot.send_message(message.chat.id,
                               "Выберите действие",
                               reply_markup=user_markup)
        bot.register_next_step_handler(msg, choose_action_passenger,user_phone = phone_users_local)

    else:
        bot.send_message(message.chat.id,'Ваш заказ удалён.',reply_markup=types.ReplyKeyboardRemove())
        phone_users_local = phone
        comment = comment_users
        mydb_1 = sqlite3.connect('base.db')
        mycursor = mydb_1.cursor()
        mycursor.execute(f"DELETE FROM orders WHERE phone = {phone_users_local} and price = {price}")
        mydb_1.commit()
        user_markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
        button_func_ord_1 = types.KeyboardButton(text="Мои заказы")
        button_func_ord_2 = types.KeyboardButton(text="Новая поездка")
        user_markup.add(button_func_ord_1, button_func_ord_2)
        msg = bot.send_message(message.chat.id,
                               "Выберите действие",
                               reply_markup=user_markup)
        bot.register_next_step_handler(msg,choose_action_passenger,user_phone = phone_users_local)

@bot.message_handler(content_types=['text'])
def comment(message,phone,longitude_start, latitude_start, longitude_end,
              latitude_end,price_way_mes,length_way,time_way,first_checkpoint,second_checkpoint):
    comment = message.text
    second_time = time.time().__round__()
    bot.send_message(message.chat.id,
                     f"<i><b>Ваш заказ.</b></i>\n\n<i><b>Начальная точка:</b></i> {first_checkpoint}\n\n<i><b>Конечная точка:</b></i> {second_checkpoint}\n\n<i><b>Расстояние:</b></i> {length_way} м\n\n<i><b>Время пути:</b></i> {time_way} мин\n\n<b>Цена:</b> {price_way_mes} ₽\n\n<i><b>Комментарий:</b></i> {comment}",
                     parse_mode='HTML', reply_markup=types.ReplyKeyboardRemove())
    mydb = sqlite3.connect('base.db')
    mycursor = mydb.cursor()
    sqlFormula = "INSERT INTO orders ('phone', 'longitude_start', 'latitude_start', 'longitude_end', 'latitude_end', 'price', 'length_way', 'time_way', 'teg_id', 'comment','time') VALUES (?,?,?,?,?,?,?,?,?,?,?)"
    mycursor.execute(sqlFormula, (
        phone, longitude_start, latitude_start, longitude_end, latitude_end, price_way_mes, length_way, time_way,
        message.chat.id, comment,second_time))
    mydb.commit()
    markup_ord = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_ord_yes = types.KeyboardButton(text="Да")
    button_ord_no = types.KeyboardButton(text="Нет")
    markup_ord.add(button_ord_yes)
    markup_ord.add(button_ord_no)
    msg_ord = bot.send_message(message.chat.id, "Всё верно?", reply_markup=markup_ord)
    bot.register_next_step_handler(msg_ord, func_ord, phone = phone,comment_users = comment,price = price_way_mes)

if __name__ == '__main__':
    bot.polling(none_stop=True)
