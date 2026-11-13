import cv2
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.linear_model import Ridge
from typing import Dict, Any, Tuple, List
import base64 as b64

class SignatureMLP(nn.Module):
    """
    Red Neuronal Densa Multicapa en PyTorch (Deep Learning):
    - Capa de entrada (descriptores morfologicos) -> BatchNorm -> ReLU -> Dropout -> Capa Oculta -> Sigmoid.
    - Cumple los requisitos del silabo: epocas, batch, funcion de activacion, perdida (BCELoss), optimizador (Adam).
    """
    def __init__(self, input_dim=12):
        super(SignatureMLP, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Dropout(0.25),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )

    def forward(self, x):
        return self.net(x)

class SignatureVerifier:
    @staticmethod
    def account_for_overlap(result, chronology, image_shape):
        """No atribuir al gesto de firma la rugosidad de trazos superpuestos."""
        point = chronology.get('crossing_point')
        h, w = image_shape[:2]
        if point and point[0] >= w * .45 and h * .55 <= point[1] < h * .95:
            result = dict(result)
            result['raw_morphology_status'] = result.get('morphology_status')
            result.update({
                'morphology_status': 'inconclusive',
                'anomaly_detected': False,
                'verdict': 'FIRMA CON CRUCE: MORFOLOGIA NO CONCLUYENTE',
                'explanation': 'La región de firma contiene un cruce con otro trazo. La rugosidad del contorno mezclado no se atribuye automáticamente a la firma; se requiere aislar los trazos y realizar cotejo.',
            })
        return result

    def __init__(self):
        self.device = torch.device('cpu')
        torch.manual_seed(42)
        self.model = SignatureMLP(input_dim=12).to(self.device)
        self.pressure_regressor = Ridge(alpha=1.0)
        self.loss_history = []
        self._train_models()

    def _extract_signature_features(self, gray_roi: np.ndarray, mask_roi: np.ndarray) -> np.ndarray:
        h, w = mask_roi.shape[:2]
        if h == 0 or w == 0:
            return np.zeros(12, dtype=np.float32)

        area = float(h * w)
        ink_count = float(cv2.countNonZero(mask_roi))
        density = ink_count / (area + 1e-5)
        aspect_ratio = float(w) / float(h + 1e-5)

        # Contornos y circularidad
        contours, _ = cv2.findContours(mask_roi, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        perimeter = 0.0
        for c in contours:
            perimeter += cv2.arcLength(c, True)
        circularity = (4 * np.pi * ink_count) / ((perimeter ** 2) + 1e-5)

        # Proyecciones horizontal y vertical (centroides de masa)
        h_proj = np.sum(mask_roi, axis=1) / 255.0
        v_proj = np.sum(mask_roi, axis=0) / 255.0
        y_indices = np.arange(len(h_proj))
        x_indices = np.arange(len(v_proj))
        cy = float(np.sum(y_indices * h_proj) / (np.sum(h_proj) + 1e-5)) / (h + 1e-5)
        cx = float(np.sum(x_indices * v_proj) / (np.sum(v_proj) + 1e-5)) / (w + 1e-5)

        # Varianza de masa en cuadrantes (distribucion espacial 2x2)
        q1 = np.sum(mask_roi[:h//2, :w//2]) / 255.0 / (ink_count + 1e-5)
        q2 = np.sum(mask_roi[:h//2, w//2:]) / 255.0 / (ink_count + 1e-5)
        q3 = np.sum(mask_roi[h//2:, :w//2]) / 255.0 / (ink_count + 1e-5)
        q4 = np.sum(mask_roi[h//2:, w//2:]) / 255.0 / (ink_count + 1e-5)

        # Analisis de bordes y micro-temblores (ataxia grafica)
        edges = cv2.Canny(mask_roi, 50, 150)
        edge_count = float(cv2.countNonZero(edges))
        edge_complexity = edge_count / (ink_count + 1e-5)

        # Gradientes de Sobel (variabilidad de flujo de tinta)
        sobelx = cv2.Sobel(gray_roi, cv2.CV_32F, 1, 0, ksize=3)
        sobely = cv2.Sobel(gray_roi, cv2.CV_32F, 0, 1, ksize=3)
        mag, _ = cv2.cartToPolar(sobelx, sobely)
        gradient_std = float(np.std(mag))

        return np.array([
            aspect_ratio,
            density,
            circularity,
            cx, cy,
            float(q1), float(q2), float(q3), float(q4),
            edge_complexity,
            gradient_std,
            perimeter / (w + h + 1e-5)
        ], dtype=np.float32)

    def _train_models(self):
        # 1. Entrenar el Regresor Lineal de Presion Motora
        np.random.seed(42)
        torch.manual_seed(42)
        N = 300
        # Caracteristicas sinteticas para calibrar regresion de presion
        X_reg = np.random.uniform(0.1, 1.0, (N, 3))
        # Presion fisica real simulada: f(densidad, gradiente, complejidad)
        y_pressure = 45.0 + 35.0 * X_reg[:, 0] + 20.0 * X_reg[:, 1] - 10.0 * X_reg[:, 2] + np.random.normal(0, 2.0, N)
        self.pressure_regressor.fit(X_reg, y_pressure)

        # 2. Entrenar la Red Neuronal PyTorch MLP (Autentica vs Falsificada)
        # 150 muestras genuinas (gesto fluido, densidad media-alta, bajo temblor)
        X_gen = np.random.normal(loc=[3.2, 0.22, 0.35, 0.52, 0.48, 0.28, 0.22, 0.24, 0.26, 0.65, 16.0, 1.8],
                                 scale=[0.4, 0.04, 0.06, 0.05, 0.05, 0.04, 0.04, 0.04, 0.04, 0.08, 2.5, 0.25],
                                 size=(150, 12)).astype(np.float32)
        y_gen = np.ones((150, 1), dtype=np.float32)

        # 150 muestras falsificadas (lentas, temblores elevados, mayor complejidad perimetral)
        X_forg = np.random.normal(loc=[3.6, 0.34, 0.21, 0.44, 0.58, 0.35, 0.18, 0.30, 0.17, 1.15, 26.0, 2.6],
                                  scale=[0.5, 0.06, 0.05, 0.07, 0.07, 0.06, 0.05, 0.05, 0.05, 0.14, 3.8, 0.35],
                                  size=(150, 12)).astype(np.float32)
        y_forg = np.zeros((150, 1), dtype=np.float32)

        X_all = np.vstack([X_gen, X_forg])
        y_all = np.vstack([y_gen, y_forg])

        dataset = torch.utils.data.TensorDataset(torch.from_numpy(X_all), torch.from_numpy(y_all))
        dataloader = torch.utils.data.DataLoader(dataset, batch_size=32, shuffle=True)

        criterion = nn.BCELoss()
        optimizer = optim.Adam(self.model.parameters(), lr=0.008, weight_decay=1e-4)

        self.model.train()
        self.loss_history = []
        for epoch in range(25):
            epoch_loss = 0.0
            for batch_x, batch_y in dataloader:
                optimizer.zero_grad()
                preds = self.model(batch_x)
                loss = criterion(preds, batch_y)
                loss.backward()
                optimizer.step()
                epoch_loss += loss.item()
            avg_loss = epoch_loss / len(dataloader)
            self.loss_history.append({'epoch': epoch + 1, 'loss': round(float(avg_loss), 4)})

        self.model.eval()

    def verify(self, image_bgr: np.ndarray, ink_mask: np.ndarray) -> Dict[str, Any]:
        gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape[:2]

        # 1. Localizar la region de la firma (mitad inferior derecha o inferior general)
        sig_roi_gray = gray[int(h * 0.55):int(h * 0.95), int(w * 0.45):]
        sig_roi_mask = ink_mask[int(h * 0.55):int(h * 0.95), int(w * 0.45):]
        
        if cv2.countNonZero(sig_roi_mask) < 30:
            sig_roi_gray = gray[int(h * 0.55):int(h * 0.95), :]
            sig_roi_mask = ink_mask[int(h * 0.55):int(h * 0.95), :]

        hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)
        roi_saturation = hsv[int(h * 0.55):int(h * 0.95), int(w * 0.45):, 1]
        if roi_saturation.shape == sig_roi_mask.shape and np.count_nonzero((sig_roi_mask > 0) & (roi_saturation >= 60)) >= 40:
            sig_roi_mask = sig_roi_mask.copy()
            sig_roi_mask[roi_saturation < 60] = 0

        # 2. Medicion pericial de temblores (Ataxia Grafica / Segunda Ley de Pellat)
        # Suavizado leve contra escalones de rasterización. Comparamos dos
        # escalas sobre un contorno de tamaño canónico; no usamos su longitud
        # absoluta como prueba de falsificación.
        smooth_mask = cv2.threshold(cv2.GaussianBlur(sig_roi_mask, (3, 3), 0), 100, 255, cv2.THRESH_BINARY)[1]
        contours, _ = cv2.findContours(smooth_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        usable = False
        roughness_growth = 0.0
        if contours:
            cnt = max(contours, key=lambda c: len(c))
            x, y, cw, ch = cv2.boundingRect(cnt)
            usable = cw >= max(30, w * 0.04) and ch >= 8 and len(cnt) >= 40
            if usable:
                canonical = ((cnt.astype(np.float32) - [x, y]) * (300.0 / max(cw, ch))).astype(np.float32)
                perimeter = cv2.arcLength(canonical, True)
                fine = cv2.arcLength(cv2.approxPolyDP(canonical, 1.0, True), True)
                coarse = cv2.arcLength(cv2.approxPolyDP(canonical, 3.0, True), True)
                roughness_growth = max(0.0, (fine - coarse) / max(perimeter, 1.0))
        tremor_score = float(np.clip(roughness_growth * 2000.0, 0.0, 100.0))
        anomaly_detected = bool(usable and roughness_growth >= 0.03)
        status = 'irregular' if anomaly_detected else 'regular' if usable and roughness_growth < 0.02 else 'inconclusive'

        # Estimacion de Presion Motora y Velocidad

        verdict = {
            'regular': 'SIN IRREGULARIDAD MORFOLOGICA DESTACADA',
            'irregular': 'IRREGULARIDAD DE TRAZO: REQUIERE COTEJO',
            'inconclusive': 'MORFOLOGIA NO CONCLUYENTE: REQUIERE COTEJO',
        }[status]

        return {
            'success': True,
            'verdict': verdict,
            'is_genuine': None,
            'authenticity_probability': None,
            'anomaly_detected': anomaly_detected,
            'morphology_status': status,
            'roughness_growth': round(roughness_growth, 5),
            'motor_pressure_index': None,
            'kinematic_speed_index': None,
            'tremor_score': round(tremor_score, 1),
            'training_epochs_loss': self.loss_history[::2],
            'model_architecture': 'Heurística morfológica de temblores; MLP y Ridge entrenados con datos sintéticos para demostración',
            'explanation': (
                f'Contorno evaluado a dos escalas; índice de irregularidad {tremor_score:.1f}/100. '
                'La rugosidad puede depender de la captura, del útil o de variación natural. '
                'Sin una firma de referencia no se determina autoría, autenticidad, coacción, presión física ni velocidad real.'
            )
        }

    def compare_dual_signatures(self, image_bgr: np.ndarray, ink_mask: np.ndarray) -> Dict[str, Any]:
        """
        Cotejo Grafotecnico Comparativo (Firma Indubitada vs. Firma Dubitada en la misma hoja).
        - Firma Izquierda: Considerada el Patron Indubitado de referencia.
        - Firma Derecha: Considerada la Firma Cuestionada / Imitacion.
        """
        h, w = image_bgr.shape[:2]
        mid_x = w // 2

        # Particion izquierda y derecha
        mask_left = ink_mask[:, :mid_x]
        mask_right = ink_mask[:, mid_x:]
        gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
        gray_left = gray[:, :mid_x]
        gray_right = gray[:, mid_x:]

        # Verificar cantidad suficiente de tinta en ambas mitades
        count_l = cv2.countNonZero(mask_left)
        count_r = cv2.countNonZero(mask_right)

        if count_l < 40 or count_r < 40:
            return {
                'success': False,
                'message': 'No se detectaron dos firmas claramente separadas. Asegurate de colocar la firma original a la izquierda y la imitacion a la derecha en la misma hoja.',
                'left_signature': None,
                'right_signature': None,
                'verdict': 'INSUFICIENTE_MUESTRA',
                'annotated_image_b64': None
            }

        # 1. Encontrar bounding box de cada firma
        cnts_l, _ = cv2.findContours(mask_left, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts_r, _ = cv2.findContours(mask_right, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        xl, yl, wl, hl = cv2.boundingRect(np.vstack(cnts_l) if cnts_l else np.array([[[0, 0]]]))
        xr, yr, wr, hr = cv2.boundingRect(np.vstack(cnts_r) if cnts_r else np.array([[[0, 0]]]))
        xr_global = xr + mid_x

        # 2. Extraer caracteristicas individuales
        feats_l = self._extract_signature_features(gray_left[yl:yl+hl, xl:xl+wl], mask_left[yl:yl+hl, xl:xl+wl])
        feats_r = self._extract_signature_features(gray_right[yr:yr+hr, xr:xr+wr], mask_right[yr:yr+hr, xr:xr+wr])

        # 3. Metricas biomecanicas y dimensionales
        scales = np.array([1.0, 0.2, 0.1, 0.5, 0.5, 0.3, 0.3, 0.5, 0.3, 0.2, 50.0, 3.0], dtype=np.float32)
        norm_l = feats_l / scales
        norm_r = feats_r / scales
        euclidean_dist = float(np.linalg.norm(norm_l - norm_r))
        morph_similarity = float(np.clip(1.0 / (1.0 + euclidean_dist * 0.45), 0.0, 1.0))

        aspect_diff = float(abs(feats_l[0] - feats_r[0]) / (max(feats_l[0], feats_r[0]) + 1e-5))
        quadrant_diff = float(np.sum(np.abs(feats_l[5:9] - feats_r[5:9])))
        centroid_diff = float(np.sqrt((feats_l[3] - feats_r[3])**2 + (feats_l[4] - feats_r[4])**2))
        pen_lifts = len(cnts_r) - len(cnts_l)

        tremor_l = float(np.clip(15.0 + centroid_diff * 30.0, 12.0, 90.0))
        divergence_penalty = (aspect_diff + quadrant_diff * 0.8) * 60.0 + max(0, pen_lifts) * 10.0
        tremor_r = float(np.clip(15.0 + divergence_penalty, 12.0, 92.0))
        speed_l = float(np.clip(95.0 - tremor_l * 0.6, 20.0, 95.0))
        speed_r = float(np.clip(95.0 - tremor_r * 0.8, 15.0, 90.0))
        pressure_l = float(np.clip(68.0 - (tremor_l * 0.3), 15.0, 95.0))
        pressure_r = float(np.clip(68.0 - (tremor_r * 0.3), 15.0, 95.0))

        diff_tremor = tremor_r - tremor_l
        diff_speed = speed_l - speed_r

        # Criterio forense integral de falsificacion por imitacion servil (Solange Pellat)
        is_forgery = bool(
            aspect_diff >= 0.18 or 
            quadrant_diff >= 0.35 or 
            centroid_diff >= 0.10 or 
            pen_lifts >= 2 or 
            morph_similarity < 0.85 or
            diff_tremor >= 8.0
        )

        if is_forgery:
            verdict = "DIVERGENCIA MORFOLOGICA: REQUIERE REVISION"
            reasons = []
            if aspect_diff >= 0.18:
                reasons.append(f"deformacion de proporciones espaciales ({aspect_diff*100:.1f}%)")
            if quadrant_diff >= 0.35:
                reasons.append("desbalance severo en la distribucion de masa grafica")
            if pen_lifts >= 1:
                reasons.append(f"interrupciones y paradas anormales del util inscriptor (+{pen_lifts})")
            if diff_speed >= 12.0:
                reasons.append(f"inhibicion cinematica y lentitud propia del calco servil (-{diff_speed:.1f} pts de velocidad)")
            if not reasons:
                reasons.append("irregularidades en la trayectoria y temblores de ejecucion")

            conclusion = (
                f"Similitud descriptiva: {morph_similarity*100:.1f}%. Se observan diferencias en proporciones, "
                "distribución de tinta o contornos. La comparación de una imagen no determina autoría ni "
                "presión o velocidad físicas; requiere muestras de referencia y revisión especializada."
            )
        else:
            verdict = "SIMILITUD MORFOLOGICA: AUTORIA NO DETERMINADA"
            conclusion = (
                f"Similitud descriptiva: {morph_similarity*100:.1f}%. No se superaron los umbrales de divergencia "
                "morfológica del prototipo. La similitud no demuestra que las firmas sean del mismo autor."
            )

        # 6. Dibujar visualizacion anotada con bounding boxes
        annotated = image_bgr.copy()
        cv2.line(annotated, (mid_x, 10), (mid_x, h - 10), (180, 180, 180), 1, cv2.LINE_AA)
        
        # Caja Izquierda (Verde Esmeralda - Patron)
        cv2.rectangle(annotated, (xl, yl), (xl + wl, yl + hl), (40, 180, 50), 2, cv2.LINE_AA)
        cv2.putText(annotated, "FIRMA INDUBITADA (PATRON)", (xl, max(20, yl - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (40, 180, 50), 1, cv2.LINE_AA)

        # Caja Derecha (Rojo si es falsificacion, Verde si es autentica)
        color_r = (30, 30, 225) if is_forgery else (40, 180, 50)
        label_r = "DUBITADA: DIVERGENCIA" if is_forgery else "DUBITADA: SIMILITUD"
        cv2.rectangle(annotated, (xr_global, yr), (xr_global + wr, yr + hr), color_r, 2, cv2.LINE_AA)
        cv2.putText(annotated, label_r, (xr_global, max(20, yr - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.48, color_r, 1, cv2.LINE_AA)

        _, buf = cv2.imencode('.png', annotated)
        annotated_b64 = 'data:image/png;base64,' + b64.b64encode(buf).decode('utf-8')

        return {
            'success': True,
            'verdict': verdict,
            'is_forgery': is_forgery,
            'morphological_similarity': round(morph_similarity, 3),
            'left_signature': {
                'label': 'Referencia proporcionada por el usuario',
                'aspect_ratio': round(float(feats_l[0]), 3),
                'ink_density': round(float(feats_l[1]), 3),
                'contour_count': len(cnts_l),
                'status': 'REFERENCIA'
            },
            'right_signature': {
                'label': 'Muestra comparada',
                'aspect_ratio': round(float(feats_r[0]), 3),
                'ink_density': round(float(feats_r[1]), 3),
                'contour_count': len(cnts_r),
                'status': 'DIVERGENTE' if is_forgery else 'SIMILAR'
            },
            'delta_tremor': round(diff_tremor, 1),
            'delta_speed': round(diff_speed, 1),
            'scientific_conclusion': conclusion,
            'annotated_image_b64': annotated_b64
        }


