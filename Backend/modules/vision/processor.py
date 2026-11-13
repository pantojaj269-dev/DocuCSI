import cv2
import numpy as np
import base64
from typing import Tuple, Dict, Any, Optional

class DocumentProcessor:
    @staticmethod
    def decode_image(image_bytes: bytes) -> np.ndarray:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError('No se pudo decodificar la imagen enviada.')
        return img

    @staticmethod
    def decode_base64(b64_str: str) -> np.ndarray:
        if ',' in b64_str:
            b64_str = b64_str.split(',')[1]
        img_bytes = base64.b64decode(b64_str)
        return DocumentProcessor.decode_image(img_bytes)

    @staticmethod
    def encode_base64(img: np.ndarray, format: str = '.png') -> str:
        _, buffer = cv2.imencode(format, img)
        b64 = base64.b64encode(buffer).decode('utf-8')
        ext = format.replace('.', '')
        return f'data:image/{ext};base64,{b64}'

    @staticmethod
    def order_points(pts: np.ndarray) -> np.ndarray:
        rect = np.zeros((4, 2), dtype='float32')
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]
        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]
        return rect

    @classmethod
    def rectify_perspective(cls, image: np.ndarray) -> Tuple[np.ndarray, bool]:
        h, w = image.shape[:2]
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edged = cv2.Canny(blurred, 50, 200)

        contours, _ = cv2.findContours(edged, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]

        doc_contour = None
        for c in contours:
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02 * peri, True)
            if len(approx) == 4 and cv2.contourArea(c) > (w * h * 0.15):
                doc_contour = approx
                break

        if doc_contour is None:
            return image, False

        pts = doc_contour.reshape(4, 2)
        rect = cls.order_points(pts)
        (tl, tr, br, bl) = rect

        width_a = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
        width_b = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
        max_w = max(int(width_a), int(width_b))

        height_a = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
        height_b = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
        max_h = max(int(height_a), int(height_b))

        dst = np.array([
            [0, 0],
            [max_w - 1, 0],
            [max_w - 1, max_h - 1],
            [0, max_h - 1]
        ], dtype='float32')

        M = cv2.getPerspectiveTransform(rect, dst)
        warped = cv2.warpPerspective(image, M, (max_w, max_h))
        return warped, True

    @classmethod
    def validate_document(cls, image: np.ndarray) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Validador de Entrada Pericial (Guardia de Percepción del Agente Inteligente):
        Verifica si la imagen (capturada por cámara o cargada desde archivo) corresponde a un soporte documental válido.
        1. Detección de Soporte de Papel: Evalúa el porcentaje de fondo blanco/neutro con baja saturación.
        2. Filtro Anti-Selfie / Rostros Humanos: Detecta presencia predominante de personas sin soporte documental.
        3. Detección de Trazos de Tinta: Comprueba presencia de líneas contrastantes de grafía.
        """
        h, w = image.shape[:2]
        total_pixels = float(h * w)

        # 1. Detección de fondo de papel (espacio HSV: baja saturación y alto valor de brillo)
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        sat = hsv[:, :, 1]
        val = hsv[:, :, 2]
        paper_mask = (sat < 40) & (val > 110)
        paper_ratio = float(np.sum(paper_mask) / total_pixels)

        # 2. Detección de tonos de piel dérmica humana (espacio YCrCb combinado con HSV)
        # Acotamos el espacio dérmico para evitar que escritorios de madera, manteles rojos
        # o fondos cálidos de mesas se confundan con rostros humanos.
        ycrcb = cv2.cvtColor(image, cv2.COLOR_BGR2YCrCb)
        skin_mask_ycrcb = cv2.inRange(ycrcb, np.array([0, 133, 77]), np.array([255, 173, 127]))
        skin_mask_hsv = (sat >= 20) & (sat <= 150) & ((hsv[:, :, 0] <= 20) | (hsv[:, :, 0] >= 165))
        skin_mask = skin_mask_ycrcb & skin_mask_hsv
        skin_ratio = float(np.sum(skin_mask > 0) / total_pixels)

        # Si el documento está sobre un escritorio de cualquier color y tiene papel claro, no debe rechazarse.
        # Solo se rechaza por persona/rostro si el tono dérmico es dominante Y NO existe suficiente soporte de papel
        if (skin_ratio >= 0.35 and paper_ratio < 0.30) or skin_ratio >= 0.55:
            return False, f"RECHAZO DE ENTRADA: Se detectó la presencia predominante de una persona o rostro en el encuadre (densidad de tono de piel: {skin_ratio*100:.1f}%). Por favor enfoque o suba exclusivamente un documento sobre una superficie plana.", {
                "reason": "FACE_OR_PERSON_DETECTED",
                "skin_ratio": round(skin_ratio, 3),
                "paper_ratio": round(paper_ratio, 3)
            }

        if paper_ratio < 0.20:
            return False, f"RECHAZO DE ENTRADA: La imagen no corresponde a un soporte documental (el fondo claro de papel es de apenas {paper_ratio*100:.1f}%). Asegúrese de enfocar una hoja de papel bien iluminada.", {
                "reason": "INSUFFICIENT_PAPER_BACKGROUND",
                "paper_ratio": round(paper_ratio, 3),
                "skin_ratio": round(skin_ratio, 3)
            }

        # 3. Detección de trazos de tinta contrastantes
        ink_mask, _ = cls.extract_ink_mask(image)
        ink_ratio = float(cv2.countNonZero(ink_mask) / total_pixels)

        if ink_ratio < 0.0015:
            return False, "RECHAZO DE ENTRADA: Hoja en blanco sin trazos gráficos legibles. Coloque un documento que contenga firmas, texto o cifras.", {
                "reason": "BLANK_DOCUMENT",
                "ink_ratio": round(ink_ratio, 4),
                "paper_ratio": round(paper_ratio, 3)
            }

        if ink_ratio > 0.65:
            return False, "RECHAZO DE ENTRADA: Densidad gráfica excesiva o textura ambiental compleja. Enfoca directamente el documento.", {
                "reason": "TOO_COMPLEX_SCENE",
                "ink_ratio": round(ink_ratio, 4),
                "paper_ratio": round(paper_ratio, 3)
            }

        return True, "Soporte documental validado correctamente.", {
            "reason": "VALID_DOCUMENT",
            "paper_ratio": round(paper_ratio, 3),
            "ink_ratio": round(ink_ratio, 4),
            "skin_ratio": round(skin_ratio, 4)
        }

    @staticmethod
    def extract_ink_mask(image: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 1. Umbral de Otsu global
        otsu_val, thresh_otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # 2. Umbral adaptativo local (para compensar sombras en fotos reales de celular)
        thresh_adapt = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 31, 14
        )
        
        # 3. Techo estricto de oscuridad: ningun pixel con brillo cercano al papel blanco/cuaderno es tinta
        max_ink_gray = min(195, int(otsu_val + 20))
        valid_dark_pixels = (gray < max_ink_gray).astype(np.uint8) * 255
        
        mask = cv2.bitwise_and(cv2.bitwise_or(thresh_otsu, thresh_adapt), valid_dark_pixels)
        
        # 4. Apertura morfologica para eliminar cuadriculas tenues de 1px y ruido de camara
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        
        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(mask)
        min_size = 20
        clean_mask = np.zeros_like(mask)
        for i in range(1, num_labels):
            if stats[i, cv2.CC_STAT_AREA] >= min_size:
                clean_mask[labels == i] = 255

        return clean_mask, gray



    @staticmethod
    def skeletonize(mask: np.ndarray) -> np.ndarray:
        skel = np.zeros(mask.shape, np.uint8)
        element = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
        temp_mask = mask.copy()

        while True:
            eroded = cv2.erode(temp_mask, element)
            opened = cv2.morphologyEx(eroded, cv2.MORPH_OPEN, element)
            subset = cv2.subtract(eroded, opened)
            skel = cv2.bitwise_or(skel, subset)
            temp_mask = eroded.copy()
            if cv2.countNonZero(temp_mask) == 0:
                break

        return skel

