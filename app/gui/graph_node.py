from PyQt6.QtWidgets import QGraphicsEllipseItem, QGraphicsTextItem, QInputDialog, QCheckBox
from PyQt6.QtGui import QBrush, QColor
from PyQt6.QtCore import Qt

from ..core.graph import Node
from .property_dialogs import NodePropertiesDialog

class GraphNodeItem(QGraphicsEllipseItem):
    """
    Визуальное представление узла (Состояния) на сцене
    """
    def __init__(self, logical_node: Node):
        super().__init__(0, 0, 100, 100)
        self.logical_node = logical_node 

        # Список всех стрелок, которые присоединены к этому узлу
        self.transitions = [] 

        # Цвет состояния
        self.setBrush(QBrush(QColor("#aaddff"))) # Цвет заливки

        # Флаги
        self.setFlag(QGraphicsEllipseItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsEllipseItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsEllipseItem.GraphicsItemFlag.ItemSendsScenePositionChanges)

        # Имя поверх кружка
        self.text_item = QGraphicsTextItem(self.logical_node.name, self)
        self.text_item.setDefaultTextColor(QColor("black"))
        self.update_text_position()

        self.setZValue(1) # Узлы на нижнем слое

    def update_text_position(self):
        """Центрирует текст внутри круга"""
        text_rect = self.text_item.boundingRect()
        node_rect = self.boundingRect()
        self.text_item.setPos(
            (node_rect.width() - text_rect.width()) / 2,
            (node_rect.height() - text_rect.height()) / 2
        )

    def itemChange(self, change, value):
        """Событие срабатывает при любом движении узла"""
        if change == QGraphicsEllipseItem.GraphicsItemChange.ItemPositionChange:
            # Просим все связанные стрелки обновить свои координаты
            for transition in self.transitions:
                transition.update_position()
        return super().itemChange(change, value)
    
    def mouseDoubleClickEvent(self, event):
        current_name = self.logical_node.name
        current_expected = self.logical_node.properties.get("expected_result", "")
        is_initial = self.logical_node.properties.get("is_initial", False)

        from .property_dialogs import NodePropertiesDialog
        dialog = NodePropertiesDialog(current_name, current_expected, is_initial)
        
        if dialog.exec():
            # Получаем 4 значения
            new_name, new_expected, now_initial, now_delete = dialog.get_values()
            
            if now_delete:
                # Удаляем из логики (из класса Graph)
                main_window = self.scene().views()[0].window()
                main_window.graph_model.delete_node(self.logical_node.id)
                
                # Удаляем все связанные стрелки со сцены
                for trans in self.transitions[:]: # копируем список для безопасного удаления
                    if trans.scene():
                        if trans.anchor.scene():
                            self.scene().removeItem(trans.anchor)
                        self.scene().removeItem(trans)
                
                # Удаляем сам узел со сцены
                self.scene().removeItem(self)
                return

            # Иначе просто обновляем данные
            self.logical_node.name = new_name
            self.text_item.setPlainText(new_name)
            self.update_text_position()
            self.logical_node.properties["expected_result"] = new_expected
            self.logical_node.properties["is_initial"] = now_initial

            if now_initial:
                for item in self.scene().items():
                    if isinstance(item, GraphNodeItem) and item != self:
                        item.logical_node.properties["is_initial"] = False
                        item.refresh_color()
            self.refresh_color()

    def refresh_color(self):
        """Устанавливает цвет узла в зависимости от его статуса"""
        if self.logical_node.properties.get("is_initial", False):
            self.setBrush(QBrush(QColor("#ccffcc"))) # Зеленый для начального
        else:
            self.setBrush(QBrush(QColor("#aaddff"))) # Голубой для обычного

