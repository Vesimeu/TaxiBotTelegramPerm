import sqlite3
import time
# mydb = sqlite3.connect('base.db')
# # mydb = sqlite3.connect('base.db')
# mycursor = mydb.cursor()
# mycursor.execute("SELECT * FROM passengers")
# print(mycursor.fetchall())
# mycursor.execute("DELETE FROM passengers WHERE phone = '79519552739'")
# mydb.commit()


# mydb = sqlite3.connect('base.db')
# mycursor = mydb.cursor()
# orders = mycursor.execute("SELECT * FROM orders")
# print(time.time())
# time_second = time.time().__round__()
# for time in orders:
#     print(time_second - time[-1])
    # print(int(time.time()) - int(time[-1]))
    # if int(time.time()) - int(time[-1]) >= 60:
    #     print('Я зашёл сюда', time[-3], int(time.time()) - int(time[-1]) >= 60)




mydb = sqlite3.connect('base.db')
mycursor = mydb.cursor()
ord = mycursor.execute("SELECT * FROM orders")
print(ord.fetchall())
mydb.commit()

# mybdord = sqlite3.connect('base.db')
# mycursor_order = mybdord.cursor()
# price = 500
# number = '79519552739'
# mycursor_order.execute(f"DELETE FROM orders WHERE phone = {number,} and price = {price}")
# mybdord.commit()
# ord = mycursor_order.fetchall()
# print(ord)
# #
#

# mycursor.execute("DELETE FROM passengers WHERE phone = '+79519552739'")
# mydb.commit()
# mycursor.execute("SELECT * FROM passengers")
# print(mycursor.fetchall())
# mydb = sqlite3.connect('base.db')
# mycursor = mydb.cursor()
# mycursor.execute("SELECT * FROM taxi_drivers")
# mycursor.execute("DELETE FROM taxi_drivers WHERE phone = '+79519552739'")
# mydb.commit()
# mycursor.execute("SELECT * FROM taxi_drivers")
# print(mycursor.fetchall())
# mycursor = mydb.cursor()
# mycursor.execute("SELECT * FROM orders")
# mycursor.execute("DELETE FROM orders WHERE phone = '+79519552739'")
# mydb.commit()
# mycursor.execute("SELECT * FROM orders")
# print(mycursor.fetchall())

