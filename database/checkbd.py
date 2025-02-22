import sys
import sqlite3
from PySide6.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QPushButton, QWidget, QLabel, QComboBox, QMessageBox


class DatabaseViewer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Просмотр базы данных")
        self.setGeometry(200, 200, 800, 500)

        self.db_path = "base.db"  # 📌 Путь к базе данных
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # 📌 Заголовок
        self.label = QLabel("Выберите таблицу для просмотра:")
        layout.addWidget(self.label)

        # 📌 Выпадающий список с таблицами
        self.table_selector = QComboBox()
        self.table_selector.addItems(self.get_table_names())
        self.table_selector.currentTextChanged.connect(self.load_table_data)
        layout.addWidget(self.table_selector)

        # 📌 Таблица для отображения данных
        self.table_widget = QTableWidget()
        layout.addWidget(self.table_widget)

        # 📌 Кнопка обновления
        self.refresh_button = QPushButton("🔄 Обновить")
        self.refresh_button.clicked.connect(self.load_table_data)
        layout.addWidget(self.refresh_button)

        # 📌 Кнопка удаления
        self.delete_button = QPushButton("❌ Удалить выбранную строку")
        self.delete_button.clicked.connect(self.delete_row)
        layout.addWidget(self.delete_button)

        # 📌 Основной виджет
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.load_table_data()

    def get_table_names(self):
        """ Получает список всех таблиц в базе данных. """
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        return [row[0] for row in self.cursor.fetchall()]

    def load_table_data(self):
        """ Загружает данные из выбранной таблицы и отображает в QTableWidget. """
        table_name = self.table_selector.currentText()
        if not table_name:
            return

        self.cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [col[1] for col in self.cursor.fetchall()]  # 📌 Получаем список столбцов

        self.cursor.execute(f"SELECT * FROM {table_name}")
        rows = self.cursor.fetchall()

        self.table_widget.setColumnCount(len(columns))
        self.table_widget.setRowCount(len(rows))
        self.table_widget.setHorizontalHeaderLabels(columns)

        for row_idx, row in enumerate(rows):
            for col_idx, cell in enumerate(row):
                self.table_widget.setItem(row_idx, col_idx, QTableWidgetItem(str(cell)))

    def delete_row(self):
        """ Удаляет выбранную строку из таблицы и базы данных. """
        row = self.table_widget.currentRow()
        if row >= 0:
            table_name = self.table_selector.currentText()
            confirmation = QMessageBox.question(
                self, "Подтверждение", f"Вы уверены, что хотите удалить эту строку из таблицы '{table_name}'?",
                QMessageBox.Yes | QMessageBox.No
            )

            if confirmation == QMessageBox.Yes:
                # Получаем первичный ключ (id) для выбранной строки
                item = self.table_widget.item(row, 0)  # Предполагаем, что первый столбец - это ID
                if item:
                    record_id = item.text()

                    # Удаляем запись из базы данных
                    self.cursor.execute(f"DELETE FROM {table_name} WHERE id = ?", (record_id,))
                    self.conn.commit()

                    # Обновляем таблицу
                    self.load_table_data()
        else:
            QMessageBox.warning(self, "Предупреждение", "Пожалуйста, выберите строку для удаления.")

    def closeEvent(self, event):
        """ Закрываем соединение при выходе из приложения. """
        self.conn.close()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = DatabaseViewer()
    viewer.show()
    sys.exit(app.exec())
