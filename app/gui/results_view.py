import pandas as pd
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QLabel, QPushButton, QHeaderView, QFileDialog, QMessageBox

class ResultsView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        # Заголовок
        self.label = QLabel("Сгенерированные тест-кейсы")
        self.label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(self.label)

        # Таблица
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID Теста", "Шаг", "Из состояния", "В состояние", "Действие (Action)", "Ожидаемый результат"
        ])
        
        # Растягиваем колонки, чтобы они занимали всё место
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)

        # Сохраним данные тестов в переменную класса, чтобы было что экспортировать
        self.current_test_cases = []

    def display_tests(self, test_cases):
        """Заполняет таблицу данными из генератора"""
        self.table.setRowCount(0) # Очищаем старое
        self.current_test_cases = test_cases # Сохраняем для экспорта
        
        row = 0
        for test in test_cases:
            test_id = test["id"]
            for i, step in enumerate(test["steps"]):
                self.table.insertRow(row)
                
                # Заполняем ячейки
                self.table.setItem(row, 0, QTableWidgetItem(f"Test #{test_id}" if i == 0 else ""))
                self.table.setItem(row, 1, QTableWidgetItem(str(i + 1)))
                self.table.setItem(row, 2, QTableWidgetItem(step["from_node"]))
                self.table.setItem(row, 3, QTableWidgetItem(step["to_node"]))
                action_with_input = f"{step['action']}\n(Input: {step['input']})"
                self.table.setItem(row, 4, QTableWidgetItem(action_with_input))
                
                self.table.setItem(row, 5, QTableWidgetItem(step["expected"]))
                row += 1
        
                 # Разрешаем перенос строк
                self.table.resizeRowsToContents()
    
    def export_to_excel(self):
        if not self.current_test_cases:
            QMessageBox.warning(self, "Ошибка", "Нет данных для экспорта!")
            return

        # Спрашиваем пользователя, куда сохранить файл
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить тесты", "", "Excel Files (*.xlsx)"
        )

        if file_path:
            if not file_path.endswith(".xlsx"):
                file_path += ".xlsx"

            try:
                # Подготавливаем данные для Pandas
                flat_data = []
                for test in self.current_test_cases:
                    for i, step in enumerate(test["steps"]):
                        flat_data.append({
                            "Test ID": f"Test #{test['id']}",
                            "Step #": i + 1,
                            "From State": step["from_node"],
                            "To State": step["to_node"],
                            "Action": step["action"],
                            "Input Data": step["input"],
                            "Expected Result": step["expected"]
                        })

                # Создаем DataFrame и сохраняем
                df = pd.DataFrame(flat_data)
                df.to_excel(file_path, index=False)
                
                QMessageBox.information(self, "Успех", f"Файл успешно сохранен:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить файл: {str(e)}")