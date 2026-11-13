import cv2
import numpy as np
import base64
from io import BytesIO
from PIL import Image, UnidentifiedImageError
from typing import Tuple, Dict, Any, Optional

class DocumentProcessor:
    @staticmethod
    def decode_image(image_bytes: bytes) -> np.ndarray:
        if not image_bytes:
            raise ValueError('La imagen está vacía.')
        # Consultar dimensiones antes de que OpenCV asigne el bitmap entero.
        try:
            with Image.open(BytesIO(image_bytes)) as header:
                if header.width * header.height > 24_000_000:
                    raise ValueError('La imagen supera 24 megapíxeles. Sube una versión más pequeña.')
        except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as exc:
            raise ValueError('No se pudo leer una imagen compatible o sus dimensiones son excesivas.') from exc
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError('No se pudo decodificar la imagen enviada.')
        if img.shape[0] * img.shape[1] > 24_000_000:
            raise ValueError('La imagen supera 24 megapíxeles. Sube una versión más pequeña.')
        return img

    @staticmethod
    def decode_base64(b64_str: str) -> np.ndarray:
        if ',' in b64_str:
            b64_str = b64_str.split(',')[1]
        img_bytes = DocumentProcessor.decode_base64_bytes(b64_str)
        return DocumentProcessor.decode_image(img_bytes)

    @staticmethod
    def decode_base64_bytes(b64_str: str) -> bytes:
        if len(b64_str) > 22_000_000:
            raise ValueError('La imagen es demasiado pesada. El máximo es 16 MB.')
        encoded = b64_str.split(',', 1)[-1]
        try:
            image_bytes = base64.b64decode(encoded, validate=True)
        except (ValueError, base64.binascii.Error) as exc:
            raise ValueError('El contenido de la imagen no es Base64 válido.') from exc
        if len(image_bytes) > 16_000_000:
            raise ValueError('La imagen es demasiado pesada. El máximo es 16 MB.')
        return image_bytes

    @staticmethod
    def prepare_for_analysis(image: np.ndarray) -> np.ndarray:
        h, w = image.shape[:2]
        if min(h, w) < 64:
            raise ValueError('La imagen debe medir al menos 64 píxeles por lado.')
        scale = min(1.0, 1600.0 / max(h, w))
        if scale < 1.0:
            return cv2.resize(image, (round(w * scale), round(h * scale)), interpolation=cv2.INTER_AREA)
        return image

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
            bx, by, bw, bh = cv2.boundingRect(approx)
            if (len(approx) == 4 and cv2.isContourConvex(approx)
                    and cv2.contourArea(c) > (w * h * 0.50)
                    and bw >= w * .65 and bh >= h * .65):
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
        if min(max_w, max_h) < 64:
            return image, False

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
        Verifica si la imagen capturada por la cámara corresponde a un soporte documental válido.
        1. Filtro Anti-Selfie / Personas: Detecta tonos de piel humana en espacio YCrCb.
        2. Detección de Soporte de Papel: Evalúa el porcentaje de fondo blanco/neutro con baja saturación.
        3. Detección de Trazos de Tinta: Comprueba presencia de líneas contrastantes.
        """
        h, w = image.shape[:2]
        total_pixels = float(h * w)
        
        # 1. Detección de personas / rostros (Tonos de piel en espacio YCrCb)
        ycrcb = cv2.cvtColor(image, cv2.COLOR_BGR2YCrCb)
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        # Rango cromático estándar de pigmentación dérmica humana: Cr [133, 173], Cb [77, 127]
        skin_mask = cv2.inRange(ycrcb, np.array([0, 133, 77]), np.array([255, 173, 127]))
        # Papel crema e iluminación cálida también entran en YCrCb de piel.
        # No tratarlos como personas: exigir saturación cromática apreciable.
        skin_mask[hsv[:, :, 1] < 55] = 0
        skin_ratio = float(np.sum(skin_mask > 0) / total_pixels)

        if skin_ratio >= 0.12:
            return False, f"RECHAZO DE ENTRADA: Predominan colores de fondo incompatibles con el soporte claro esperado ({skin_ratio*100:.1f}%). Enfoca el documento con iluminación neutra. Este filtro cromático no detecta rostros.", {
                "reason": "UNSUITABLE_BACKGROUND_COLORS",
                "skin_ratio": round(skin_ratio, 3)
            }

        # 2. Detección de fondo de papel (espacio HSV: baja saturación y alto valor de brillo)
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        sat = hsv[:, :, 1]
        val = hsv[:, :, 2]
        paper_mask = (sat < 40) & (val > 110)
        paper_ratio = float(np.sum(paper_mask) / total_pixels)

        if paper_ratio < 0.22:
            return False, f"RECHAZO DE ENTRADA: La imagen no corresponde a un soporte documental (el fondo claro de papel es de apenas {paper_ratio*100:.1f}%). Asegurese de enfocar una hoja de papel bien iluminada.", {
                "reason": "INSUFFICIENT_PAPER_BACKGROUND",
                "paper_ratio": round(paper_ratio, 3)
            }

        # 3. Detección de trazos de tinta contrastantes
        ink_mask, _ = cls.extract_ink_mask(image)
        ink_ratio = float(cv2.countNonZero(ink_mask) / total_pixels)

        if ink_ratio < 0.0015:
            return False, "RECHAZO DE ENTRADA: Hoja en blanco sin trazos graficos legibles. Coloque un documento que contenga firmas, texto o cifras.", {
                "reason": "BLANK_DOCUMENT",
                "ink_ratio": round(ink_ratio, 4)
            }

        if ink_ratio > 0.65:
            return False, "RECHAZO DE ENTRADA: Densidad grafica excesiva o textura ambiental compleja. Enfoca directamente el documento.", {
                "reason": "TOO_COMPLEX_SCENE",
                "ink_ratio": round(ink_ratio, 4)
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
        _, thresh_otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # 2. Umbral adaptativo local (para compensar sombras en fotos reales de celular)
        thresh_adapt = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 31, 7
        )
        
        # El umbral absoluto anterior borraba lápiz claro junto a tinta oscura.
        # Estimar el soporte local permite retener trazos con contraste >= 8
        # niveles incluso si el píxel de grafito es más claro que 195.
        background = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, np.ones((31, 31), np.uint8))
        contrast = background.astype(np.int16) - gray.astype(np.int16)
        candidates = cv2.bitwise_or(thresh_otsu, thresh_adapt) > 0
        mask = ((contrast >= 8) & candidates).astype(np.uint8) * 255
        
        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(mask)
        # No abrir con un kernel de 2 px: destruye escritura a lápiz de 1 px.
        min_size = 8
        keep = stats[:, cv2.CC_STAT_AREA] >= min_size
        keep[0] = False
        clean_mask = (keep[labels].astype(np.uint8) * 255)

        return clean_mask, gray



    @staticmethod
    def assess_capture(image: np.ndarray, ink_mask: np.ndarray) -> Dict[str, Any]:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        focus = float(cv2.Laplacian(gray, cv2.CV_32F).var())
        background = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, np.ones((31,31),np.uint8))
        contrasts = (background.astype(np.int16)-gray.astype(np.int16))[ink_mask > 0]
        median_contrast = float(np.median(contrasts)) if len(contrasts) else 0.0
        warnings = []
        if max(gray.shape) < 700:
            warnings.append('Resolución reducida: los trazos pequeños o tenues pueden no resolverse.')
        if focus < 25:
            warnings.append('Nitidez baja según el criterio exploratorio; repetir con mejor enfoque puede revelar trazos omitidos.')
        if median_contrast < 20:
            warnings.append('Contraste de escritura bajo; una ausencia de diferencias no permite descartar otro material.')
        return {'focus_indicator': round(focus,2), 'median_stroke_contrast': round(median_contrast,2),
                'warnings': warnings, 'status': 'capture_requires_review' if warnings else 'no_capture_warning',
                'scope': 'Indicadores exploratorios de captura, no una validación pericial.'}

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

