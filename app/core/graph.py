import uuid

class Node:
    """
    Класс, описывающий Узел (Состояние/Экран).
    """
    def __init__(self, name ="New State"):
        self.id = str(uuid.uuid4())
        self.name = name

        self.properties = {}

    def __repr__(self):
        return f"Node(name='{self.name}', id={self.id[:4]}...)"
    
class Transition:
    """
    Класс, описавающий переход (Стрелку)
    Связывает два узла: откуда -> куда
    """
    def __init__(self, source_node: Node, target_node: Node, action_name="Action"):
        self.id = str(uuid.uuid4())
        self.source = source_node
        self.target = target_node
        self.action = action_name

        self.properties = {}

    def __repr__(self):
        return f"Transition({self.source.name} -> {self.target.name}, action='{self.action}')"
    
class Graph:
    """
    Главный класс, который хранит всю модель целиком
    """
    def __init__(self):
        self.nodes = [] # Список всех узлов
        self.transitions = [] # Список всех переходов

    def add_node(self, name="New State") -> Node:
        """Создает новый узел и добавляет его в граф"""
        new_node = Node(name)
        self.nodes.append(new_node)
        return new_node
    
    def add_transition(self, source: Node, target: Node, action="Action") -> Transition:
        """Создаёт переход между двумя узлами"""
        new_transition = Transition(source, target, action)
        self.transitions.append(new_transition)
        return new_transition
    
    def delete_node(self, node_id: str):
        """Удаляет узел и все связанные с ним переходы"""
        self.nodes = [n for n in self.nodes if n.id != node_id]

        self.transitions = [
            t for t in self.transitions
            if t.source.id != node_id and t.target.id != node_id
        ]

    def clear(self):
        """Очищает весь граф"""
        self.nodes = []
        self.transitions = []