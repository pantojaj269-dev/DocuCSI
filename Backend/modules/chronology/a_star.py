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
                    new_h = cls.heuristic((nx, ny), goal)
                    neighbor_node = Node(nx, ny, new_g, new_h, current)
                    heapq.heappush(open_set, neighbor_node)

        return [], float('inf'), nodes_explored

    @classmethod
    def analyze_intersection(cls, image_bgr: np.ndarray, ink_mask: np.ndarray) -> Dict[str, Any]:
        h, w = image_bgr.shape[:2]
        gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
        
        # Mapa de costos inversos: donde hay tinta densa, el costo de avance es bajo (0-50); fuera de tinta es 255.
        cost_map = np.full((h, w), 255.0, dtype=np.float32)
        ink_indices = np.where(ink_mask > 0)
        
        # Penalizacion por saltos de gradiente
        sobelx = cv2.Sobel(gray, cv2.CV_32F, 1, 0)
        sobely = cv2.Sobel(gray, cv2.CV_32F, 0, 1)
        grad_mag, _ = cv2.cartToPolar(sobelx, sobely)
        
        for y, x in zip(ink_indices[0], ink_indices[1]):
            # Costo menor = mayor fluidez de tinta
            intensity_cost = (255 - gray[y, x]) / 255.0 * 20.0
            grad_cost = grad_mag[y, x] * 0.15
            cost_map[y, x] = max(1.0, 30.0 - intensity_cost + grad_cost)

        # 1. Deteccion de interseccion real entre lineas horizontales (renglon/clausula) y trazos verticales/manuscritos
        min_line_len = max(60, int(w * 0.20))
        h_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (min_line_len, 1))
        v_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, max(12, int(h * 0.025))))
        h_lines = cv2.morphologyEx(ink_mask, cv2.MORPH_OPEN, h_kernel)
        v_strokes = cv2.morphologyEx(ink_mask, cv2.MORPH_OPEN, v_kernel)

        # Excluir margenes perimetrales exteriores (bordes de marco del cheque)
        my, mx = int(h * 0.12), int(w * 0.1)
        inner_overlap = np.zeros_like(ink_mask)
        inner_overlap[my:h-my, mx:w-mx] = cv2.bitwise_and(h_lines[my:h-my, mx:w-mx], v_strokes[my:h-my, mx:w-mx])

        overlap_pts = np.where(inner_overlap > 0)
        has_intersection = len(overlap_pts[0]) >= 28


        # Si NO hay interseccion fisica real en el cuerpo del documento, no hay conflicto de firma en blanco
        if not has_intersection:
            return {
                'success': True,
                'has_intersection': False,
                'top_stroke': 'Sin cruces de trazos contradictorios',
                'is_signature_top': True,
                'blank_signature_fraud': False,
                'horizontal_path_cost': 0.0,
                'vertical_path_cost': 0.0,
                'nodes_explored_a_star': 0,
                'visualization_b64': '',
                'chronology_verdict': (
                    'CONFORMIDAD CRONOLOGICA: No se detectaron cruces de trazos contradictorios ni clausulas superpuestas a la firma.'
                )
            }

        # Si HAY interseccion real, localizar el punto de cruce critico sobre la tinta
        mid_idx = len(overlap_pts[0]) // 2
        cy_cross = int(overlap_pts[0][mid_idx])
        cx_cross = int(overlap_pts[1][mid_idx])

        # Definir ventana de busqueda de A* alrededor de la interseccion real
        win_w = min(100, int(w * 0.3))
        win_h = min(80, int(h * 0.3))

        start_h = (max(0, cx_cross - win_w // 2), cy_cross)
        goal_h  = (min(w - 1, cx_cross + win_w // 2), cy_cross)

        start_v = (cx_cross, max(0, cy_cross - win_h // 2))
        goal_v  = (cx_cross, min(h - 1, cy_cross + win_h // 2))

        path_h, cost_h, nodes_h = cls.a_star_search(cost_map, start_h, goal_h)
        path_v, cost_v, nodes_v = cls.a_star_search(cost_map, start_v, goal_v)

        vis = image_bgr.copy()
        for pt in path_h:
            cv2.circle(vis, pt, 2, (255, 200, 0), -1)
        for pt in path_v:
            cv2.circle(vis, pt, 2, (0, 140, 255), -1)

        cv2.circle(vis, (cx_cross, cy_cross), 12, (0, 255, 0), 2)
        cv2.putText(vis, "INTERSECCION CRITICA (A*)", (max(10, cx_cross - 90), max(25, cy_cross - 18)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 1)

        norm_cost_h = (cost_h / (len(path_h) + 1e-5)) if path_h else 999.0
        norm_cost_v = (cost_v / (len(path_v) + 1e-5)) if path_v else 999.0

        is_signature_top = norm_cost_v < norm_cost_h
        top_stroke = "Trazo de Firma/Manuscrito (Continuo)" if is_signature_top else "Linea de Texto/Clausula (Superpuesta)"
        blank_signature_fraud = bool(not is_signature_top)

        _, buffer = cv2.imencode('.png', vis)
        vis_b64 = 'data:image/png;base64,' + b64.b64encode(buffer).decode('utf-8')

        return {
            'success': True,
            'has_intersection': True,
            'top_stroke': top_stroke,
            'is_signature_top': is_signature_top,
            'blank_signature_fraud': blank_signature_fraud,
            'horizontal_path_cost': round(float(norm_cost_h), 3),
            'vertical_path_cost': round(float(norm_cost_v), 3),
            'nodes_explored_a_star': nodes_h + nodes_v,
            'visualization_b64': vis_b64,
            'chronology_verdict': (
                'CONFORMIDAD CRONOLOGICA: El trazo de la firma superpone fisicamente a la clausula. Secuencia de suscripcion normal.'
                if is_signature_top else
                'ALERTA MAXIMA DE FRAUDE: El trazo del texto/clausula superpone fisicamente a la firma. EVIDENCIA DE ABUSO DE FIRMA EN BLANCO (el papel fue firmado antes de la redaccion del texto).'
            )
        }

