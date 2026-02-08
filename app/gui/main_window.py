from PyQt6.QtWidgets import QMainWindow, QGraphicsView, QGraphicsScene, QToolBar
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt

from ..core.graph import Graph
from .graph_node import GraphNodeItem

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

        self._create_menus()
        self._create_toolbar()

    def _create_menus(self):
        """Создание верхнего меню (Файл, Правка и т.д.)"""
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("Файл")
        exit_action = QAction("Выход", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        edit_menu = menu_bar.addMenu("Правка")

    def _create_toolbar(self):
        """Панель инструментов для быстрого доступа"""
        toolbar = QToolBar("Панель инструментов")
        self.addToolBar(toolbar)
        
        # Кнопка добавления состояния
        add_state_action = QAction("Добавить состояние", self)
        add_state_action.triggered.connect(self.add_state_node)
        toolbar.addAction(add_state_action)

    def add_state_node(self):
        """
        Метод-обработчик для добавления нового узла-состояния.
        """
        # Создаем узел в логической модели
        logical_node = self.graph_model.add_node("Новое состояние")
        
        # Создаем визуальное представление для этого узла
        visual_node = GraphNodeItem(logical_node)
        
        # Добавляем визуальный узел на сцену
        view_center = self.view.viewport().rect().center()
        scene_center = self.view.mapToScene(view_center)
        visual_node.setPos(scene_center.x() - 50, scene_center.y() - 50)
        self.scene.addItem(visual_node)
        
        print(f"Добавлен узел: {logical_node}. Всего узлов в модели: {len(self.graph_model.nodes)}")
