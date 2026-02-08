from PyQt6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QDialogButtonBox, QTextEdit, QCheckBox, QPushButton, QHBoxLayout, QComboBox

class NodePropertiesDialog(QDialog):
    def __init__(self, name, expected_result, is_initial, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Свойства состояния")
        self.delete_requested = False
        
        layout = QVBoxLayout(self)
        form = QFormLayout()

        # Поле для имени (однострочное)
        self.name_edit = QLineEdit()
        self.name_edit.setText(str(name))
        
        # Поле для результата (многострочное)
        self.expected_edit = QTextEdit()
        self.expected_edit.setPlainText(str(expected_result))
        self.expected_edit.setMaximumHeight(100)

        # Галочка "Начальное состояние"
        self.initial_check = QCheckBox("Начальное состояние")
        self.initial_check.setChecked(is_initial)

        form.addRow("Название:", self.name_edit)
        form.addRow("Ожидаемый результат:", self.expected_edit)
        form.addRow(self.initial_check)
        
        layout.addLayout(form)

        # Панель кнопок
        btns_layout = QHBoxLayout()
        
        # Кнопка удаления
        self.del_btn = QPushButton("Удалить состояние")
        self.del_btn.clicked.connect(self.request_delete)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        btns_layout.addWidget(self.del_btn)
        btns_layout.addStretch()
        btns_layout.addWidget(self.button_box)
        layout.addLayout(btns_layout)

    def request_delete(self):
        self.delete_requested = True
        self.accept()

    def get_values(self):
        return self.name_edit.text(), self.expected_edit.toPlainText(), self.initial_check.isChecked(), self.delete_requested


class TransitionPropertiesDialog(QDialog):
    def __init__(self, action, input_data, trans_type="Neutral", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Свойства перехода")
        self.delete_requested = False

        layout = QVBoxLayout(self)
        form = QFormLayout()

        # Поле для действия (однострочное)
        self.action_edit = QLineEdit()
        self.action_edit.setText(str(action))
        
        # Поле для входных данных (многострочное)
        self.input_edit = QTextEdit()
        self.input_edit.setPlainText(str(input_data))
        self.input_edit.setMaximumHeight(100)

        # Выбор типа перехода
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Neutral", "Success", "Error"])
        self.type_combo.setCurrentText(trans_type)

        form.addRow("Действие (Action):", self.action_edit)
        form.addRow("Входные данные (Input):", self.input_edit)
        form.addRow("Тип перехода:", self.type_combo)

        layout.addLayout(form)

        btns_layout = QHBoxLayout()
        self.del_btn = QPushButton("Удалить переход")
        self.del_btn.clicked.connect(self.request_delete)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        btns_layout.addWidget(self.del_btn)
        btns_layout.addStretch()
        btns_layout.addWidget(self.button_box)
        layout.addLayout(btns_layout)

    def request_delete(self):
        self.delete_requested = True
        self.accept()

    def get_values(self):
        return self.action_edit.text(), self.input_edit.toPlainText(), self.type_combo.currentText(), self.delete_requested