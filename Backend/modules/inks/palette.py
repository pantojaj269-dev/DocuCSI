"""Inventario de trazos cromáticos y neutros, sin adivinar su instrumento."""
import cv2
import numpy as np


def inspect_palette(image, ink_mask):
    # Compensación global moderada del tono del soporte; no convierte el
    # brillo de un trazo en una prueba de grafito, impresión o fabricante.
    paper = np.percentile(image.reshape(-1, 3), 90, axis=0).astype(np.float32)
    balanced = np.clip((image.astype(np.float32)+1) / (paper+1) * 245, 0, 255).astype(np.uint8)
    saturation = cv2.cvtColor(balanced, cv2.COLOR_BGR2HSV)[:, :, 1]
    ink = ink_mask > 0
    colored = ink & (saturation >= 60)
    # El borde antialias de tinta azul puede ser casi gris. Conservar negro
    # y gris independientes, sin contar el halo del mismo trazo dos veces.
    color_halo = cv2.dilate(colored.astype(np.uint8), np.ones((5,5),np.uint8)) > 0
    neutral = ink & (saturation <= 35) & ~color_halo
    colored_count = int(np.count_nonzero(colored))
    neutral_count = int(np.count_nonzero(neutral))
    total = int(np.count_nonzero(ink))
    has_color = colored_count >= 30
    neutral_trace = neutral_count >= 8
    neutral_present = neutral_count >= max(25, int(total * .002))
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    background = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, np.ones((31,31),np.uint8))
    contrast = background.astype(np.int16)-gray.astype(np.int16)
    faint_count = int(np.count_nonzero(neutral & (contrast < 25)))
    return {
        'colored_marks_detected': has_color,
        'neutral_marks_detected': neutral_present,
        'neutral_trace_detected': neutral_trace,
        'mixed_colored_neutral': bool(has_color and neutral_trace),
        'colored_pixel_count': colored_count,
        'neutral_pixel_count': neutral_count,
        'faint_neutral_pixel_count': faint_count,
        'neutral_material_identity': 'undetermined',
        'neutral_confidence': 'sufficient_visible_support' if neutral_present else 'weak_visible_support' if neutral_trace else 'not_detected',
        '_neutral_mask': neutral,
    }
