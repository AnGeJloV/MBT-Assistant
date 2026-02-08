class TestGenerator:
    def __init__(self, graph):
        self.graph = graph
    
    def find_start_node(self):
        """Ищет узел, помеченный как начальный"""
        for node in self.graph.nodes:
            if node.properties.get("is_initial", False):
                return node
            return None
        
    def generate_all_paths(self):
        """
        Генерирует список путей от начального узла до всех конечных точек
        База для формирования тест-кейсов
        """
        start_node = self.find_start_node()
        if not start_node:
            return []
        
        all_path = []
        # Запускаем рекурсивный обход
        self._dfs(start_node, [], all_path, set())
        return all_path
    
    def _dfs(self, current_node, current_path, all_path, visited_transitions):
        """Внутренний обход графа"""
        # Находим все выходящие стрелки из графа
        outgoing_transitions = {
            t for t in self.graph.transitions if t.source.id == current_node.id
        }

        # Если идти некуда - мы дошли до конца сценария
        if not outgoing_transitions:
            if current_path:
                all_path.append(list(current_path))
            return
        
        for trans in outgoing_transitions:
            # Защита от бесконечного цикла
            if trans.id in outgoing_transitions:
                # Если уперлись в цикл, сохраняем то, что успели собрать
                all_path.append(list(current_path))
                continue

            # Добавляем переход в текущий путь
            visited_transitions.add(trans.id)
            current_path.append(trans)

            # Идем глубже к след узлу
            self._dfs(trans.target, current_path, all_path, visited_transitions)

            # Откат для исследования других веток
            current_path.pop()
            visited_transitions.remove(trans.id)

    def format_test_cases(self, paths):
        """Превращает сырые пути в читаемые сценарии"""
        formatted_tests = []
        for i, path in enumerate(paths):
            test_case = {
                "id": i + 1,
                "steps": []
            }
            for step in path:
                test_case["steps"].append({
                    "action": step.action,
                    "input": step.properties.get("input_data", "N/A"),
                    "expected": step.target.properties.get("expected_result", "N/A"),
                    "target_node": step.target.name
                })
            formatted_tests.append(test_case)
        return formatted_tests