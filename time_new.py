import time
import telebot
from telebot import types
import sqlite3
token = "5544251503:AAGk7nbwdirjy_4h1GqwCIGzlxxrjYHYeC0"
bot = telebot.TeleBot(token)
# time_second = time.time().__round__()
time_second = time.time().__round__()
while True:
    time.sleep(5)
    time_second = time_second + 5
    mydb = sqlite3.connect('base.db')
    mycursor = mydb.cursor()
    orders = mycursor.execute("SELECT * FROM orders")
    for times in orders:
        if time_second - times[-1] >= 7000:
            phone_number = times[1]
            print('Я зашёл сюда!', times[-3], 'заказ',phone_number,' удалён!')
            bot.send_message(times[-3], 'У вашего заказа истекло время ожидания.Ваш заказ удалён.')
            mycursor.execute(f"DELETE FROM orders WHERE phone = {phone_number}")
            mydb.commit()