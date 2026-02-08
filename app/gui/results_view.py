from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QLabel, QPushButton, QHeaderView

class ResultsView(QWidget):
    def __init__(self, back_callback):
        super().__init__()
        layout = QVBoxLayout(self)

        # Заголовок
        self.label = QLabel("Сгенерированные тест-кейсы")
        self.label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(self.label)

        # Таблица
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID Теста", "Шаг", "Действие (Action)", "Ввод (Input)", "Ожидаемый результат"])
        
        # Растягиваем колонки, чтобы они занимали всё место
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(self.table)

        # Кнопка возврата
        self.back_btn = QPushButton("Вернуться к редактору")
        self.back_btn.setHeight = 40
        self.back_btn.clicked.connect(back_callback)
        layout.addWidget(self.back_btn)

    def display_tests(self, test_cases):
        """Заполняет таблицу данными из генератора"""
        self.table.setRowCount(0) # Очищаем старое
        
        row = 0
        for test in test_cases:
            test_id = test["id"]
            for i, step in enumerate(test["steps"]):
                self.table.insertRow(row)
                
                # Если это первый шаг теста, пишем его ID
                id_item = QTableWidgetItem(f"Test #{test_id}" if i == 0 else "")
                
                self.table.setItem(row, 0, id_item)
                self.table.setItem(row, 1, QTableWidgetItem(str(i + 1)))
                self.table.setItem(row, 2, QTableWidgetItem(step["action"]))
                self.table.setItem(row, 3, QTableWidgetItem(step["input"]))
                self.table.setItem(row, 4, QTableWidgetItem(step["expected"]))
                row += 1