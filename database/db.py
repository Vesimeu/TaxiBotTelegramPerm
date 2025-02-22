import sqlite3
import config

import sqlite3
import config

def init_db():
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE,
        phone TEXT,
        role TEXT CHECK(role IN ('passenger', 'driver'))
    )
    """)  # Закрываем скобку

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        start_lat REAL,
        start_lon REAL,
        end_lat REAL,
        end_lon REAL,
        price INTEGER,
        comment TEXT,
        status TEXT CHECK(status IN ('waiting', 'accepted', 'completed'))
    )
    """)  # Закрываем скобку

    conn.commit()
    conn.close()

def add_user(user_id, phone, role):
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id, phone, role) VALUES (?, ?, ?)", (user_id, phone, role))
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def create_order(user_id, start_lat, start_lon, end_lat, end_lon, price, comment):
    """
    Создает новый заказ в базе данных.
    """
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO orders (user_id, start_lat, start_lon, end_lat, end_lon, price, comment, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, 'waiting')
    """, (user_id, start_lat, start_lon, end_lat, end_lon, price, comment))
    conn.commit()
    conn.close()
def get_orders_by_user(user_id):
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders WHERE user_id=?", (user_id,))
    orders = cursor.fetchall()
    conn.close()
    return orders


def get_available_orders():
    """Получить список всех активных заказов."""
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders WHERE status='waiting'")
    orders = cursor.fetchall()
    conn.close()
    return orders

def get_order_by_id(order_id):
    """Получить заказ по ID."""
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders WHERE id=?", (order_id,))
    order = cursor.fetchone()
    conn.close()
    return order

def accept_order(order_id, driver_id):
    """Принять заказ водителем."""
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE orders SET status='accepted' WHERE id=?", (order_id,))
    conn.commit()
    conn.close()


def get_all_users():
    """Получить список всех пользователей."""
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    conn.close()
    return users

def ban_user(user_id):
    """Забанить пользователя."""
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET banned=1 WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()

def unban_user(user_id):
    """Разбанить пользователя."""
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET banned=0 WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()

def get_banned_users():
    """Получить список забаненных пользователей."""
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE banned=1")
    users = cursor.fetchall()
    conn.close()
    return users

def get_order_stats():
    """Получить статистику заказов."""
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*), SUM(CASE WHEN status='completed' THEN 1 ELSE 0 END) FROM orders")
    stats = cursor.fetchone()
    conn.close()
    return stats or (0, 0)

def get_all_orders():
    """Получить список всех заказов."""
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders")
    orders = cursor.fetchall()
    conn.close()
    return orders

def complete_order(order_id):
    """Завершить заказ."""
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE orders SET status='completed' WHERE id=?", (order_id,))
    conn.commit()
    conn.close()

def get_driver_for_order(order_id):
    """Получить водителя, принявшего заказ."""
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT driver_id FROM orders WHERE id=?", (order_id,))
    driver_id = cursor.fetchone()
    conn.close()
    return driver_id

def add_user(user_id, phone, role):
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id, phone, role) VALUES (?, ?, ?)", (user_id, phone, role))
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def get_orders_by_user(user_id, active_only=False):
    """
    Возвращает список заказов пользователя.

    :param user_id: ID пользователя.
    :param active_only: Если True, возвращает только активные заказы.
    :return: Список заказов.
    """
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()

    # Формируем SQL-запрос в зависимости от параметра active_only
    if active_only:
        query = "SELECT * FROM orders WHERE user_id=? AND status='active'"
    else:
        query = "SELECT * FROM orders WHERE user_id=?"

    cursor.execute(query, (user_id,))
    orders = cursor.fetchall()
    conn.close()
    return orders
def delete_order_from_db(order_id):
    """
    Удаляет заказ из базы данных по его ID.
    """
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM orders WHERE id=?", (order_id,))
    conn.commit()
    conn.close()
def get_available_orders():
    """Получить список всех активных заказов."""
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders WHERE status='waiting'")
    orders = cursor.fetchall()
    conn.close()
    return orders

def get_order_by_id(order_id):
    """Получить заказ по ID."""
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders WHERE id=?", (order_id,))
    order = cursor.fetchone()
    conn.close()
    return order

def accept_order(order_id, driver_id):
    """Принять заказ водителем."""
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE orders SET status='accepted' WHERE id=?", (order_id,))
    conn.commit()
    conn.close()


def get_all_users():
    """Получить список всех пользователей."""
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    conn.close()
    return users

def ban_user(user_id):
    """Забанить пользователя."""
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET banned=1 WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()

def unban_user(user_id):
    """Разбанить пользователя."""
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET banned=0 WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()

def get_banned_users():
    """Получить список забаненных пользователей."""
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE banned=1")
    users = cursor.fetchall()
    conn.close()
    return users

def get_order_stats():
    """Получить статистику заказов."""
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*), SUM(CASE WHEN status='completed' THEN 1 ELSE 0 END) FROM orders")
    stats = cursor.fetchone()
    conn.close()
    return stats or (0, 0)
