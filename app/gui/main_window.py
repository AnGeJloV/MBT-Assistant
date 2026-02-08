import json
from PyQt6.QtWidgets import QMainWindow, QGraphicsView, QGraphicsScene, QToolBar, QMessageBox, QTextEdit, QDialog, QVBoxLayout, QStackedWidget, QFileDialog
from PyQt6.QtGui import QAction, QBrush, QColor
from PyQt6.QtCore import Qt

from ..core.graph import Graph
from .graph_node import GraphNodeItem
from .graph_transition import GraphTransitionItem
from ..core.test_generator import TestGenerator
from .results_view import ResultsView

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
        self.setGeometry(100, 100, 1100, 700)

        # Стек окон
        self.central_stack = QStackedWidget()
        self.setCentralWidget(self.central_stack)

        # Создание холста для рисования
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(0, 0, 2000, 2000)

        # Создание "камеры", которая смотрит на холст
        self.view = QGraphicsView(self.scene, self)
        self.view.setRenderHint(self.view.renderHints().Antialiasing) # Сглаживание

        # Страница результатов
        self.results_page = ResultsView()

        # Добавляем страницы в стек
        self.central_stack.addWidget(self.view)         # Индекс 0
        self.central_stack.addWidget(self.results_page)  # Индекс 1

        # Списки для управления видимостью кнопок тулбара
        self.editor_actions = []

        self.first_node_for_link = None 

        self._create_menus()
        self._create_toolbar()
        self.show_editor()

    def show_editor(self):
        """Переключить на редактор графов"""
        self.central_stack.setCurrentIndex(0)
        # Показываем кнопки редактора
        self.toolbar.show()

    def show_results(self):
        """Переключить на страницу с таблицей"""
        self.central_stack.setCurrentIndex(1)
        # Скрываем кнопки редактора
        self.toolbar.hide()

    def _create_menus(self):
        """Создание верхнего меню (Файл, Результаты)"""
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("Файл")

        new_project_act = QAction("Новый проект", self)
        new_project_act.triggered.connect(self.clear_editor)
        file_menu.addAction(new_project_act)
  
        save_act = QAction("Сохранить проект", self)
        save_act.triggered.connect(self.save_project)
        file_menu.addAction(save_act)
    
        load_act = QAction("Загрузить проект", self)
        load_act.triggered.connect(self.load_project)
        file_menu.addAction(load_act)
        
        file_menu.addSeparator()

        exit_action = QAction("Выход", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        results_menu = menu_bar.addMenu("Результаты")
        
        view_results_act = QAction("Посмотреть таблицу", self)
        view_results_act.triggered.connect(self.show_results)
        results_menu.addAction(view_results_act)
        
        view_editor_act = QAction("Вернуться в редактор", self)
        view_editor_act.triggered.connect(self.show_editor)
        results_menu.addAction(view_editor_act)

        results_menu.addSeparator()

        export_act = QAction("Экспортировать в Excel", self)
        export_act.triggered.connect(self.results_page.export_to_excel)
        results_menu.addAction(export_act)

    def _create_toolbar(self):
        """Панель инструментов для быстрого доступа"""
        self.toolbar = QToolBar("Панель инструментов")
        self.addToolBar(self.toolbar)
        
        # Кнопка добавления состояния
        add_state_action = QAction("Добавить состояние", self)
        add_state_action.triggered.connect(self.add_state_node)
        self.toolbar.addAction(add_state_action)
        self.editor_actions.append(add_state_action)

        # Кнопка для соединения
        self.link_action = QAction("Соединить", self)
        self.link_action.setCheckable(True) # Кнопка-"переключатель"
        self.toolbar.addAction(self.link_action)
        self.editor_actions.append(self.link_action)

        # Кнопка для генерации тестов
        gen_action = QAction("Генерировать тесты", self)
        gen_action.triggered.connect(self.run_generation)
        self.toolbar.addAction(gen_action)
        self.editor_actions.append(gen_action)

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

        # Заполняем таблицу данными
        self.results_page.display_tests(test_cases)
        
        # Переключаем экран
        self.show_results()

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

    def save_project(self):
        """Превращает весь граф в JSON и сохраняет в файл"""
        file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить проект", "", "JSON Files (*.json)")
        if not file_path:
            return

        project_data = {
            "nodes": [],
            "transitions": []
        }

        # Собираем данные об узлах
        for item in self.scene.items():
            if isinstance(item, GraphNodeItem):
                node_data = {
                    "id": item.logical_node.id,
                    "name": item.logical_node.name,
                    "x": item.scenePos().x(),
                    "y": item.scenePos().y(),
                    "properties": item.logical_node.properties
                }
                project_data["nodes"].append(node_data)

        # Собираем данные о переходах
        for item in self.scene.items():
            if isinstance(item, GraphTransitionItem):
                trans_data = {
                    "source_id": item.source_item.logical_node.id,
                    "target_id": item.target_item.logical_node.id,
                    "action": item.logical_transition.action,
                    "anchor_x": item.anchor.scenePos().x(),
                    "anchor_y": item.anchor.scenePos().y(),
                    "properties": item.logical_transition.properties
                }
                project_data["transitions"].append(trans_data)

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(project_data, f, ensure_ascii=False, indent=4)
        
        QMessageBox.information(self, "Успех", "Проект успешно сохранен!")

    def load_project(self):
        """Загружает проект из JSON-файла"""
        file_path, _ = QFileDialog.getOpenFileName(self, "Открыть проект", "", "JSON Files (*.json)")
        if not file_path:
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Очищаем текущий проект
            self.scene.clear()
            self.graph_model.clear()
            
            # Словарь для быстрого поиска созданных визуальных узлов по их ID
            id_to_visual_node = {}

            # Восстанавливаем узлы
            for n_data in data["nodes"]:
                logical_node = self.graph_model.add_node(n_data["name"])
                logical_node.id = n_data["id"] # Восстанавливаем оригинальный ID
                logical_node.properties = n_data["properties"]
                
                visual_node = GraphNodeItem(logical_node)
                visual_node.setPos(n_data["x"], n_data["y"])
                visual_node.mousePressEvent = lambda event, item=visual_node: self.handle_node_click(item, event)
                
                self.scene.addItem(visual_node)
                visual_node.refresh_color()
                id_to_visual_node[logical_node.id] = visual_node

            # Восстанавливаем переходы
            for t_data in data["transitions"]:
                source_item = id_to_visual_node.get(t_data["source_id"])
                target_item = id_to_visual_node.get(t_data["target_id"])
                
                if source_item and target_item:
                    # Создаем логический переход
                    logical_trans = self.graph_model.add_transition(
                        source_item.logical_node, 
                        target_item.logical_node, 
                        t_data["action"]
                    )
                    logical_trans.properties = t_data["properties"]
                    
                    # Создаем визуальный переход
                    visual_trans = GraphTransitionItem(source_item, target_item, logical_trans)
                    self.scene.addItem(visual_trans)
                    
                    # Восстанавливаем положение якоря (точки изгиба)
                    visual_trans.anchor.setPos(t_data["anchor_x"], t_data["anchor_y"])
                    
                    # Регистрируем стрелку в узлах
                    source_item.transitions.append(visual_trans)
                    target_item.transitions.append(visual_trans)

            QMessageBox.information(self, "Успех", "Проект успешно загружен!")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить файл:\n{str(e)}")

    def clear_editor(self):
        """Полностью очищает редактор после подтверждения пользователем"""
        # Создаем окно вопроса
        reply = QMessageBox.question(
            self, 
            "Подтверждение", 
            "Вы точно хотите очистить редактор? Все несохраненные данные будут потеряны.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Очищаем визуальную часть (сцену)
            self.scene.clear()
            # Очищаем логическую часть (модель графа)
            self.graph_model.clear()
            # Сбрасываем вспомогательные переменные
            self.first_node_for_link = None
            
            print("Редактор успешно очищен.")
