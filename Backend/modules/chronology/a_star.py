import cv2
import numpy as np
import heapq
from typing import Dict, Any, Tuple, List, Optional
import base64 as b64

class Node:
    def __init__(self, x: int, y: int, g: float, h: float, parent=None):
        self.x = x
        self.y = y
        self.g = g
        self.h = h
        self.f = g + h
        self.parent = parent

    def __lt__(self, other):
        return self.f < other.f

class ChronologyAnalyzer:
    """
    Modulo de Cronologia de Trazos Cruzados mediante Busqueda Informada (A*):
    - Resuelve el problema forense del orden de impresion/escritura en intersecciones.
    - Modela la zona de cruce como un grafo de costos ponderados segun gradiente y densidad de tinta.
    - Aplica el algoritmo A* con heuristica euclidiana para determinar cual trazo mantiene
      continuidad fisica ininterrumpida (trazo superior) y cual fue interrumpido (trazo inferior).
    """

    @staticmethod
    def heuristic(p1: Tuple[int, int], p2: Tuple[int, int]) -> float:
        return np.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

    @classmethod
    def a_star_search(cls, cost_map: np.ndarray, start: Tuple[int, int], goal: Tuple[int, int]) -> Tuple[List[Tuple[int, int]], float, int]:
        h, w = cost_map.shape[:2]
        open_set = []
        start_node = Node(start[0], start[1], 0.0, cls.heuristic(start, goal))
        heapq.heappush(open_set, start_node)
        
        visited = set()
        best_g = {start: 0.0}
        nodes_explored = 0
        max_iterations = 8000

        neighbors = [
            (-1, 0, 1.0), (1, 0, 1.0), (0, -1, 1.0), (0, 1, 1.0),
            (-1, -1, 1.414), (-1, 1, 1.414), (1, -1, 1.414), (1, 1, 1.414)
        ]

        while open_set and nodes_explored < max_iterations:
            current = heapq.heappop(open_set)
            nodes_explored += 1

            if (current.x, current.y) == goal or cls.heuristic((current.x, current.y), goal) <= 1.5:
                # Reconstruir camino
                path = []
                curr = current
                while curr:
                    path.append((curr.x, curr.y))
                    curr = curr.parent
                return path[::-1], current.g, nodes_explored

            if (current.x, current.y) in visited:
                continue
            visited.add((current.x, current.y))

            for dx, dy, step_cost in neighbors:
                nx, ny = current.x + dx, current.y + dy
                if 0 <= nx < w and 0 <= ny < h:
                    if (nx, ny) in visited:
                        continue
                    edge_penalty = float(cost_map[ny, nx])
                    if edge_penalty >= 250.0: # Obstaculo o fondo vacio
                        continue
                    new_g = current.g + step_cost + (edge_penalty * 0.1)
                    if new_g >= best_g.get((nx, ny), float('inf')):
                        continue
                    best_g[(nx, ny)] = new_g
                    new_h = cls.heuristic((nx, ny), goal)
                    neighbor_node = Node(nx, ny, new_g, new_h, current)
                    heapq.heappush(open_set, neighbor_node)

        return [], float('inf'), nodes_explored

    @classmethod
    def analyze_intersection(cls, image_bgr: np.ndarray, ink_mask: np.ndarray) -> Dict[str, Any]:
        from .observations import analyze_visible_intersections
        return analyze_visible_intersections(cls, image_bgr, ink_mask)
