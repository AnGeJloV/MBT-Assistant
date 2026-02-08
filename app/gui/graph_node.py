from PyQt6.QtWidgets import QGraphicsEllipseItem, QGraphicsTextItem
from PyQt6.QtGui import QBrush, QColor
from PyQt6.QtCore import Qt

from ..core.graph import Node

class GraphNodeItem(QGraphicsEllipseItem):
    """
    Визуальное представление узла (Состояния) на сцене
    """
    def __init__(self, logical_node: Node):
        super().__init__(0, 0, 100, 100)
        self.logical_node = logical_node 
        self.setBrush(QBrush(QColor("#aaddff"))) # Цвет заливки

        # Флаги
        self.setFlag(QGraphicsEllipseItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsEllipseItem.GraphicsItemFlag.ItemIsSelectable)

        # Имя поверх кружка
        self.text_item = QGraphicsTextItem(self.logical_node.name, self)

        # Центрируем текст внутри кружка
        text_width = self.text_item.boundingRect().width()
        text_height = self.text_item.boundingRect().height()
        rect = self.boundingRect()
        self.text_item.setPos(
            (rect.width() - text_width) / 2,
            (rect.height() - text_height) /2
        )

