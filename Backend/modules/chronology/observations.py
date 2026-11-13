"""Cruces visibles entre una línea y escritura de color, sin inferir orden físico."""
import base64
import cv2
import numpy as np


def analyze_visible_intersections(search, image, ink_mask):
    h, w = ink_mask.shape
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    # Separación cromática: una línea neutra puede cruzar escritura de color.
    # Si ambos trazos son indistinguibles, no hay evidencia para ordenar capas.
    colored = ((ink_mask > 0) & (hsv[:, :, 1] >= 60)).astype(np.uint8)
    neutral = ((ink_mask > 0) & (hsv[:, :, 1] < 60) & (hsv[:, :, 2] < 170)).astype(np.uint8) * 255
    min_length = max(40, int(w * .18))
    lines = cv2.HoughLinesP(neutral, 1, np.pi / 360, threshold=max(25, min_length // 3),
                            minLineLength=min_length, maxLineGap=max(5, int(w * .015)))
    candidates = []
    radius = max(12, min(28, int(h * .035)))
    if lines is not None:
        # Priorización geométrica, no por orden dependiente de OpenCV.
        segments = sorted(lines.reshape(-1, 4).tolist(), key=lambda p: -abs(p[2] - p[0]))[:80]
        for x1, y1, x2, y2 in segments:
            if x2 < x1:
                x1, y1, x2, y2 = x2, y2, x1, y1
            if x2 == x1 or abs(y2 - y1) / (x2 - x1) > .15:
                continue
            if not (.12 * h < (y1+y2)/2 < .88 * h):
                continue
            xs = np.arange(max(x1 + 6, int(w*.10)), min(x2 - 5, int(w*.90)))
            if not len(xs):
                continue
            ys = np.rint(y1 + (xs-x1) * (y2-y1) / (x2-x1)).astype(int)
            # Exigir trazo coloreado suficientemente cerca EN AMBOS lados,
            # no sólo letras que tocan una línea de formulario desde arriba.
            offsets = np.arange(5, radius + 1)
            above = colored[np.clip(ys[:, None]-offsets, 0, h-1), xs[:, None]].sum(axis=1)
            below = colored[np.clip(ys[:, None]+offsets, 0, h-1), xs[:, None]].sum(axis=1)
            # Tolerancia lateral para firmas oblicuas y pequeñas inclinaciones.
            width = max(11, int(radius * 1.4) | 1)
            upper = cv2.dilate((above >= 2).astype(np.uint8)[None, :], np.ones((1, width), np.uint8))[0]
            lower = cv2.dilate((below >= 2).astype(np.uint8)[None, :], np.ones((1, width), np.uint8))[0]
            support = np.flatnonzero(upper & lower)
            if len(support) < 3:
                continue
            # Preferir cruces con evidencia cerca de la línea en ambas caras.
            index = int(support[len(support)//2])
            candidates.append((len(support), int(xs[index]), int(ys[index]), (x1,y1,x2,y2)))

    vis = image.copy()
    cost_h = cost_v = None
    nodes = 0
    path_h, path_v = [], []
    has_crossing = bool(candidates)
    if has_crossing:
        _, cx, cy, line = max(candidates)
        # A* ilustra conectividad en una ventana local acotada. Sus costos
        # no se convierten en una fecha, autoría o prueba del orden de tintas.
        left, top = max(0, cx-65), max(0, cy-radius-5)
        right, bottom = min(w, cx+66), min(h, cy+radius+6)
        local_mask = ink_mask[top:bottom, left:right]
        gray = cv2.cvtColor(image[top:bottom, left:right], cv2.COLOR_BGR2GRAY)
        costs = np.where(local_mask > 0, 1.0 + gray.astype(np.float32)/255.0*10.0, 255.0)
        lx, ly = cx-left, cy-top
        x1,y1,x2,y2 = line
        def line_point(x):
            y = int(round(y1 + (x-x1)*(y2-y1)/max(1,x2-x1)))
            return (x-left, min(costs.shape[0]-1, max(0, y-top)))
        start = line_point(max(left, cx-45))
        goal = line_point(min(right-1, cx+45))
        path_h, ch, nh = search.a_star_search(costs, start, goal)
        color_roi = colored[top:bottom, left:right]
        ay, ax = np.where(color_roi[:max(0, ly-4)] > 0)
        by, bx = np.where(color_roi[min(ly+5, color_roi.shape[0]):] > 0)
        if len(ax) and len(bx):
            a = int(np.argmin(np.abs(ax-lx) + np.abs(ay-(ly-radius))*.2))
            by = by + min(ly+5, color_roi.shape[0])
            b = int(np.argmin(np.abs(bx-lx) + np.abs(by-(ly+radius))*.2))
            path_v, cv, nv = search.a_star_search(costs, (int(ax[a]),int(ay[a])), (int(bx[b]),int(by[b])))
        else:
            cv, nv = float('inf'), 0
        nodes = nh + nv
        if path_h:
            cost_h = round(float(ch)/max(1,len(path_h)-1), 3)
        if path_v:
            cost_v = round(float(cv)/max(1,len(path_v)-1), 3)
        for path, color in [(path_h, (255,180,0)), (path_v, (0,140,255))]:
            for px,py in path:
                cv2.circle(vis, (px+left,py+top), 1, color, -1)
        cv2.circle(vis, (cx,cy), 16, (20,150,230), 2)
        cv2.putText(vis, 'CRUCE VISIBLE: ORDEN FISICO NO CONCLUYENTE',
                    (max(8,cx-210),max(25,cy-24)), cv2.FONT_HERSHEY_SIMPLEX,.45,(20,110,160),1)

    encoded = cv2.imencode('.png', vis)[1]
    return {
        'success': True,
        'has_intersection': has_crossing,
        'crossing_point': [cx, cy] if has_crossing else None,
        'candidate_line': list(line) if has_crossing else None,
        'possible_overwriting': has_crossing,
        'requires_review': has_crossing,
        'chronology_status': 'inconclusive' if has_crossing else 'no_crossing_detected',
        'top_stroke': 'Orden físico no determinable en esta imagen' if has_crossing else 'Sin cruce cromático detectado',
        'is_signature_top': None,
        'blank_signature_fraud': None,
        'horizontal_path_cost': cost_h,
        'vertical_path_cost': cost_v,
        'nodes_explored_a_star': nodes,
        'visualization_b64': 'data:image/png;base64,' + base64.b64encode(encoded).decode(),
        'chronology_verdict': (
            'CRUCE DE TRAZOS VISIBLE: una línea y escritura de color presentan continuidad a ambos lados. '
            'Revisar posible superposición. A* mide conectividad de píxeles, pero una fotografía RGB '
            'no demuestra cuál tinta fue depositada primero ni confirma abuso de firma en blanco.'
            if has_crossing else
            'No se detectó un cruce entre línea neutra y escritura de color con este método. '
            'No descarta cruces del mismo color, trazos muy finos o zonas sin suficiente contraste.'
        ),
    }
