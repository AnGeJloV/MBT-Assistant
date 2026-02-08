from PyQt6.QtWidgets import QGraphicsEllipseItem, QGraphicsTextItem, QInputDialog
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
        self.update_text_position()

    def update_text_position(self):
        """Центрирует текст внутри круга"""
        text_rect = self.text_item.boundingRect()
        node_rect = self.boundingRect()
        self.text_item.setPos(
            (node_rect.width() - text_rect.width()) / 2,
            (node_rect.height() - text_rect.height()) / 2
        )
    
    def mouseDoubleClickEvent(self, event):
        """Событие двойного клика - меняем имя узла"""
        # Вызываем стандартное диалоговое окно Python
        new_name, ok = QInputDialog.getText(
            None, "Редактирование", "Введите название состояния:",
            text=self.logical_node.name
        )
        
        # Если пользователь нажал OK и ввел текст
        if ok and new_name:
            # Обновляем в логике (в объекте Node)
            self.logical_node.name = new_name
            # Обновляем визуально на холсте
            self.text_item.setPlainText(new_name)
            # Пересчитываем центр (имя могло стать длиннее)
            self.update_text_position()
            
        super().mouseDoubleClickEvent(event) # Пробрасываем событие дальше по цепочке

