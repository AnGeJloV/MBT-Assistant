from PyQt6.QtWidgets import QMainWindow, QGraphicsView, QGraphicsScene, QToolBar, QMessageBox, QTextEdit, QDialog, QVBoxLayout
from PyQt6.QtGui import QAction, QBrush, QColor
from PyQt6.QtCore import Qt

from ..core.graph import Graph
from .graph_node import GraphNodeItem
from .graph_transition import GraphTransitionItem
from ..core.test_generator import TestGenerator

class MainWindow(QMainWindow):
    """
    Главное окно приложения. Здесь располагаются все эл. интерфейса
    """
    def __init__(self):
        super().__init__()

        # Хранилище данных
        self.graph_model = Graph()

        # Настройка окна
        self.setWindowTitle("MBT-Assistant")
        self.setGeometry(100, 100, 1200, 800)

        # Создание холста для рисования
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(0, 0, 2000, 2000)

        # Создание "камеры", которая смотрит на холст
        self.view = QGraphicsView(self.scene, self)
        self.view.setRenderHint(self.view.renderHints().Antialiasing) # Сглаживание
        self.setCentralWidget(self.view)

        self.first_node_for_link = None 

        self._create_menus()
        self._create_toolbar()

    def _create_menus(self):
        """Создание верхнего меню (Файл, Результаты и т.д.)"""
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("Файл")
        exit_action = QAction("Выход", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        edit_menu = menu_bar.addMenu("Результаты")

    def _create_toolbar(self):
        """Панель инструментов для быстрого доступа"""
        toolbar = QToolBar("Панель инструментов")
        self.addToolBar(toolbar)
        
        # Кнопка добавления состояния
        add_state_action = QAction("Добавить состояние", self)
        add_state_action.triggered.connect(self.add_state_node)
        toolbar.addAction(add_state_action)

        # Кнопка для соединения
        self.link_action = QAction("Соединить", self)
        self.link_action.setCheckable(True) # Кнопка-"переключатель"
        toolbar.addAction(self.link_action)

        # Кнопка для генерации тестов
        gen_action = QAction("Генерировать тесты", self)
        gen_action.triggered.connect(self.run_generation)
        toolbar.addAction(gen_action)

    def add_state_node(self):
        """Метод-обработчик для добавления нового узла-состояния"""
        # Создаем узел в логической модели
        logical_node = self.graph_model.add_node("Новое состояние")
        
        # Создаем визуальное представление для этого узла
        visual_node = GraphNodeItem(logical_node)

        if len(self.graph_model.nodes) == 1:
            logical_node.properties["is_initial"] = True
            visual_node.refresh_color()

        visual_node.mousePressEvent = lambda event: self.handle_node_click(visual_node, event)
        
        # Добавляем визуальный узел на сцену
        scene_center = self.view.mapToScene(self.view.viewport().rect().center())
        visual_node.setPos(scene_center.x() - 50, scene_center.y() - 50)
        self.scene.addItem(visual_node)
        
        print(f"Добавлен узел: {logical_node}. Всего узлов в модели: {len(self.graph_model.nodes)}")

    def handle_node_click(self, node_item, event):
        """Логика клика по узлу (для перемещения или для создания связи)"""
        if self.link_action.isChecked():
            if self.first_node_for_link is None:
                
                self.first_node_for_link = node_item
                node_item.setBrush(QBrush(QColor("#ffaa00"))) # Оранжевый (подсветка выбора)
            else:
                
                if self.first_node_for_link != node_item:
                    self.create_link(self.first_node_for_link, node_item)
                
                self.first_node_for_link.refresh_color() 
                self.first_node_for_link = None
                self.link_action.setChecked(False)
        
        # Вызываем стандартное поведение (чтобы круги можно было таскать)
        GraphNodeItem.mousePressEvent(node_item, event)
        
        # Вызываем стандартное поведение
        GraphNodeItem.mousePressEvent(node_item, event)

    def create_link(self, source, target):
        """Создает связь или удаляет существующую"""
        # Проверяем, существует ли уже такая связь в логике
        existing_logic_trans = self.graph_model.find_transition(source.logical_node, target.logical_node)

        if existing_logic_trans:
            # Удаляем из логики
            self.graph_model.delete_transition(existing_logic_trans.id)
            
            # Ищем визуальный объект связи, чтобы убрать с экрана
            for v_trans in source.transitions:
                if v_trans.logical_transition.id == existing_logic_trans.id:
                    # Удаляем регистрацию в узлах
                    source.transitions.remove(v_trans)
                    target.transitions.remove(v_trans)
                    # Убираем со сцены
                    self.scene.removeItem(v_trans)
                    self.scene.removeItem(v_trans.anchor)
                    break
            print(f"Связь удалена: {source.logical_node.name} -> {target.logical_node.name}")
        
        else:
            # Создаём связь
            logical_trans = self.graph_model.add_transition(source.logical_node, target.logical_node)
            visual_trans = GraphTransitionItem(source, target, logical_trans)
            self.scene.addItem(visual_trans)
            source.transitions.append(visual_trans)
            target.transitions.append(visual_trans)
            print(f"Связь создана: {source.logical_node.name} -> {target.logical_node.name}")

    def run_generation(self):
        generator = TestGenerator(self.graph_model)
        
        # Проверяем наличие старта
        if not generator.find_start_node():
            QMessageBox.warning(self, "Ошибка", "Не найден начальный узел! Откройте свойства узла и поставьте галочку 'Начальное состояние'.")
            return

        # Генерируем пути
        paths = generator.generate_all_paths()
        test_cases = generator.format_test_cases(paths)

        # Формируем текст для отображения (временно, пока нет вкладки Результаты)
        result_text = ""
        for test in test_cases:
            result_text += f"=== ТЕСТ-КЕЙС №{test['id']} ===\n"
            for j, step in enumerate(test['steps']):
                result_text += f"Шаг {j+1}: {step['action']}\n"
                result_text += f"   Ввод: {step['input']}\n"
                result_text += f"   Ожидаемый результат: {step['expected']}\n"
            result_text += "\n"

        # Показываем результат в простом окне
        self.show_results_popup(result_text)

    def show_results_popup(self, text):
        dialog = QDialog(self)
        dialog.setWindowTitle("Сгенерированные тесты")
        dialog.setMinimumSize(600, 400)
        layout = QVBoxLayout(dialog)
        
        text_area = QTextEdit()
        text_area.setPlainText(text)
        text_area.setReadOnly(True)
        
        layout.addWidget(text_area)
        dialog.exec()
