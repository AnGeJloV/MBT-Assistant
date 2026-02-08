from PyQt6.QtWidgets import QMainWindow, QGraphicsView, QGraphicsScene
from ..core.graph import Graph

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
        self.setCentralWidget(self.view)