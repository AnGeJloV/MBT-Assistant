import math
from PyQt6.QtWidgets import QGraphicsPathItem, QGraphicsRectItem, QGraphicsPolygonItem
from PyQt6.QtGui import QPen, QColor, QPainterPath, QPolygonF, QBrush
from PyQt6.QtCore import QLineF, QPointF, Qt

from .property_dialogs import TransitionPropertiesDialog

class GraphTransitionItem(QGraphicsPathItem):
    """Визуальная стрелка с точкой изгиба"""
    def __init__(self, source_item, target_item, logical_transition):
        super().__init__()
        self.source_item = source_item
        self.target_item = target_item
        self.logical_transition = logical_transition

        # Настройка линии
        self.setPen(QPen(QColor("#555555"), 2))
        self.setBrush(QBrush(Qt.BrushStyle.NoBrush))

        # Создаем отдельный объект для наконечника
        self.arrow_head = QGraphicsPolygonItem(self)
        self.arrow_head.setBrush(QBrush(QColor("#555555")))
        self.arrow_head.setPen(QPen(QColor("#555555"), 1))

        # Создаем якорь (точку изгиба)
        self.anchor = TransitionAnchor(self)
        
        # Начальное положение якоря - середина между узлами
        p1 = self.source_item.sceneBoundingRect().center()
        p2 = self.target_item.sceneBoundingRect().center()
        self.anchor.setPos((p1 + p2) / 2)

        self.update_position()

    def itemChange(self, change, value):
        # Если стрелку добавили на сцену, добавляем и якорь
        if change == QGraphicsPathItem.GraphicsItemChange.ItemSceneHasChanged:
            if self.scene():
                self.scene().addItem(self.anchor)
        return super().itemChange(change, value)

    def update_position(self):
        """Пересчет геометрии линии и наконечника"""
        p_start_center = self.source_item.sceneBoundingRect().center()
        p_end_center = self.target_item.sceneBoundingRect().center()
        p_anchor = self.anchor.scenePos()

        # Линии для расчета касания границ кругов
        line_to_anchor = QLineF(p_start_center, p_anchor)
        line_from_anchor = QLineF(p_anchor, p_end_center)

        # Вычисляем точки на границах (радиус 50)
        s_point = line_to_anchor.pointAt(50 / line_to_anchor.length()) if line_to_anchor.length() > 50 else p_start_center
        e_point = line_from_anchor.pointAt((line_from_anchor.length() - 50) / line_from_anchor.length()) if line_from_anchor.length() > 50 else p_end_center

        # Обновляем путь самой линии
        path = QPainterPath()
        path.moveTo(s_point)
        path.lineTo(p_anchor)
        path.lineTo(e_point)
        self.setPath(path)

        # Обновляем наконечник
        angle = math.atan2(-line_from_anchor.dy(), line_from_anchor.dx())
        arrow_size = 14
        arrow_angle = math.pi / 6

        p3 = e_point - QPointF(math.cos(angle + arrow_angle) * arrow_size,
                               -math.sin(angle + arrow_angle) * arrow_size)
        p4 = e_point - QPointF(math.cos(angle - arrow_angle) * arrow_size,
                               -math.sin(angle - arrow_angle) * arrow_size)

        self.arrow_head.setPolygon(QPolygonF([e_point, p3, p4]))

    def mouseDoubleClickEvent(self, event):
        current_action = self.logical_transition.action
        current_input = self.logical_transition.properties.get("input_data", "")

        from .property_dialogs import TransitionPropertiesDialog
        dialog = TransitionPropertiesDialog(current_action, current_input)
        
        if dialog.exec():
            new_action, new_input, now_delete = dialog.get_values()
            
            if now_delete:
                # Удаляем из логики
                main_window = self.scene().views()[0].window()
                main_window.graph_model.delete_transition(self.logical_transition.id)
                
                # Удаляем из списков узлов
                if self in self.source_item.transitions:
                    self.source_item.transitions.remove(self)
                if self in self.target_item.transitions:
                    self.target_item.transitions.remove(self)
                
                # Удаляем со сцены якорь и саму стрелку
                if self.anchor.scene():
                    self.scene().removeItem(self.anchor)
                self.scene().removeItem(self)
                return

            # Обновление данных
            self.logical_transition.action = new_action
            self.logical_transition.properties["input_data"] = new_input

class TransitionAnchor(QGraphicsRectItem):
    """Точка изгиба"""
    def __init__(self, parent_transition):
        super().__init__(-4, -4, 8, 8)
        self.parent_transition = parent_transition
        self.setBrush(QBrush(Qt.GlobalColor.white))
        self.setPen(QPen(QColor("#555555"), 1))
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemSendsScenePositionChanges)

        self.setZValue(10) 

    def mousePressEvent(self, event):
        """Срабатывает при нажатии на якорь"""
        # Очищаем выделение сцены, чтобы узлы не двигались вместе с якорем
        if self.scene():
            self.scene().clearSelection()
        
        # Делаем сам якорь выделенным
        self.setSelected(True)
        
        # Вызываем стандартный метод, чтобы перетаскивание работало
        super().mousePressEvent(event)

    def itemChange(self, change, value):
        if change == QGraphicsRectItem.GraphicsItemChange.ItemPositionChange:
            self.parent_transition.update_position()
        return super().itemChange(change, value)