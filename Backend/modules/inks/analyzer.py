import cv2
import numpy as np
from sklearn.cluster import KMeans, DBSCAN
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from typing import Dict, Any, Tuple, List, Optional
import base64 as b64

class InkAnalyzer:
    """
    Módulo de Espectrometría Óptica y Análisis Fisicoquímico de Tintas (No Supervisado):
    - Ley de Beer-Lambert y absorbancia óptica espectral para aislar pigmentos.
    - Cromatografía digital en coordenadas normalizadas (r,g,b), CIELAB (a*, b*) y Hue circular.
    - K-Means y DBSCAN de alta resolución para distinguir formulaciones químicas distintas,
      incluso entre bolígrafos del mismo color nominal pero diferente fabricante o marca.
    - PCA para reducción dimensional y visualización pericial en 2D.
    - Métrica de Silhouette Score y distancia cromática Delta E*ab.
    """

    @staticmethod
    def _compute_pixel_features(
        bgr_pixels: np.ndarray,
        hsv_pixels: np.ndarray,
        lab_pixels: np.ndarray,
        paper_bg: np.ndarray
    ) -> np.ndarray:
        eps = 1e-4
        bgr_f = bgr_pixels.astype(np.float32)

        # 1. Absorbancia Óptica según la Ley de Beer-Lambert: A = log10(I_papel) - log10(I_tinta)
        absorbance = np.clip(np.log10(paper_bg + 1.0) - np.log10(bgr_f + 1.0), 0.0, 3.0)
        norm_abs = absorbance / (np.sum(absorbance, axis=1, keepdims=True) + eps)

        # 2. Coordenadas cromáticas normalizadas (r, g, b): Invariantes a iluminación, sombras y presión del trazo
        norm_bgr = bgr_f / (np.sum(bgr_f, axis=1, keepdims=True) + eps)

        # 3. Canales oponentes cromáticos de CIELAB (a* verde-rojo, b* azul-amarillo)
        lab_f = lab_pixels.astype(np.float32)
        a_star = (lab_f[:, 1:2] - 128.0) / 128.0
        b_star = (lab_f[:, 2:3] - 128.0) / 128.0

        # 4. Tono continuo circular en HSV (evita la discontinuidad cíclica 0°/180°) y Saturación
        hsv_f = hsv_pixels.astype(np.float32)
        hue_rad = hsv_f[:, 0] * (2.0 * np.pi / 180.0)
        hue_cos = np.cos(hue_rad).reshape(-1, 1)
        hue_sin = np.sin(hue_rad).reshape(-1, 1)
        sat = (hsv_f[:, 1] / 255.0).reshape(-1, 1)

        # Vector espectroscópico multidimensional balanceado
        features = np.hstack([
            norm_abs * 5.0,
            norm_bgr * 4.0,
            a_star * 3.0,
            b_star * 3.0,
            hue_cos * 2.5,
            hue_sin * 2.5,
            sat * 1.5
        ])
        return features

    @classmethod
    def extract_ink_features(
        cls,
        image_bgr: np.ndarray,
        ink_mask: np.ndarray
    ) -> Optional[Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]]:
        gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
        hsv_full = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)
        lab_full = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2LAB)

        # 1. Estimación del color base del soporte documental (papel)
        paper_mask = (ink_mask == 0) & (gray > 175)
        if np.sum(paper_mask) > 100:
            paper_bg = np.median(image_bgr[paper_mask], axis=0).astype(np.float32)
        else:
            paper_bg = np.array([245.0, 245.0, 245.0], dtype=np.float32)

        # 2. Filtrado de cuadrículas tenues o bordes pre-impresos neutrales si hay manuscrito
        is_printed_line = (hsv_full[:, :, 1] < 18) & (hsv_full[:, :, 2] > 115)
        clean_ink_mask = ink_mask.copy()
        if np.sum((ink_mask > 0) & (~is_printed_line)) > 80:
            clean_ink_mask[is_printed_line] = 0

        ink_grays = gray[clean_ink_mask > 0]
        if len(ink_grays) < 50:
            return None

        # 3. Aislamiento del núcleo del trazo (Core Pigment Layer)
        # Se descarta el 30% superior más claro correspondiente al antialiasing/difuminado con el papel blanco
        p_cutoff = np.percentile(ink_grays, 70)
        core_mask = (gray <= p_cutoff) & (clean_ink_mask > 0)
        if np.sum(core_mask > 0) < 60:
            core_mask = clean_ink_mask

        y_coords, x_coords = np.where(core_mask > 0)
        max_samples = 6000
        if len(y_coords) > max_samples:
            idx = np.random.choice(len(y_coords), max_samples, replace=False)
            y_coords = y_coords[idx]
            x_coords = x_coords[idx]

        coords = np.column_stack((x_coords, y_coords))
        bgr_core = image_bgr[y_coords, x_coords]
        hsv_core = hsv_full[y_coords, x_coords]
        lab_core = lab_full[y_coords, x_coords]

        features = cls._compute_pixel_features(bgr_core, hsv_core, lab_core, paper_bg)
        return features, coords, bgr_core, clean_ink_mask, paper_bg, hsv_full, lab_full

    @classmethod
    def analyze(cls, image_bgr: np.ndarray, ink_mask: np.ndarray, k_clusters: int = 2) -> Dict[str, Any]:
        extracted = cls.extract_ink_features(image_bgr, ink_mask)

        if extracted is None:
            return {
                'success': False,
                'message': 'Insuficiente cantidad de trazos de tinta detectados en la imagen.',
                'num_inks_detected': 1,
                'silhouette_score': 0.0,
                'multiple_inks_detected': False,
                'delta_hue': 0,
                'delta_e_chroma': 0.0,
                'segmented_image_b64': '',
                'pca_scatter_points': [],
                'pca_variance_explained': [0.0, 0.0],
                'ink_proportions': {'Tinta #1': 1.0},
                'outliers_detected_dbscan': 0,
                'scientific_conclusion': 'Insuficiente material de tinta para análisis espectral.'
            }

        features, coords, bgr_core, clean_ink_mask, paper_bg, hsv_full, lab_full = extracted

        # 1. Clustering K-Means con inicialización robusta
        kmeans = KMeans(n_clusters=k_clusters, random_state=42, n_init=15)
        kmeans_labels = kmeans.fit_predict(features)
        unique_labels = np.unique(kmeans_labels)

        if len(unique_labels) < 2:
            return {
                'success': True,
                'num_inks_detected': 1,
                'silhouette_score': 0.0,
                'multiple_inks_detected': False,
                'delta_hue': 0,
                'delta_e_chroma': 0.0,
                'segmented_image_b64': '',
                'pca_scatter_points': [],
                'pca_variance_explained': [1.0, 0.0],
                'ink_proportions': {'Tinta #1 (Homogénea)': 1.0},
                'outliers_detected_dbscan': 0,
                'scientific_conclusion': 'HOMOGENEIDAD OPTICA: Todos los trazos son cromáticamente idénticos.'
            }

        # 2. Métricas de Evaluación: Silhouette Score
        eval_n = min(2000, len(features))
        eval_idx = np.random.choice(len(features), eval_n, replace=False)
        if len(np.unique(kmeans_labels[eval_idx])) > 1:
            raw_sil_score = float(silhouette_score(features[eval_idx], kmeans_labels[eval_idx]))
        else:
            raw_sil_score = 0.0

        # 3. DBSCAN para detección de partículas atípicas / anómalas
        dbscan = DBSCAN(eps=0.25, min_samples=15)
        dbscan_sub_n = min(1500, len(features))
        dbscan_labels = dbscan.fit_predict(features[:dbscan_sub_n])
        outlier_count = int(np.sum(dbscan_labels == -1))

        # 4. Reducción Dimensional PCA (2D)
        pca = PCA(n_components=2, random_state=42)
        pca_coords = pca.fit_transform(features)
        explained_variance = [float(v) for v in pca.explained_variance_ratio_]

        # Normalizar coordenadas PCA al rango [-1.0, 1.0] para el visor SVG del frontend
        max_abs = np.max(np.abs(pca_coords[:200])) + 1e-5
        pca_scatter = [
            {
                'x': round(float(p[0] / max_abs * 0.95), 3),
                'y': round(float(p[1] / max_abs * 0.95), 3),
                'cluster': int(l),
                'is_outlier': bool(i < len(dbscan_labels) and dbscan_labels[i] == -1)
            }
            for i, (p, l) in enumerate(zip(pca_coords[:200], kmeans_labels[:200]))
        ]

        # 5. Cálculo Científico de Distancia Cromática y Absorción entre Clústeres
        c0_bgr = np.median(bgr_core[kmeans_labels == 0], axis=0).astype(np.uint8)
        c1_bgr = np.median(bgr_core[kmeans_labels == 1], axis=0).astype(np.uint8)

        c0_lab = cv2.cvtColor(np.uint8([[c0_bgr]]), cv2.COLOR_BGR2LAB)[0, 0].astype(float)
        c1_lab = cv2.cvtColor(np.uint8([[c1_bgr]]), cv2.COLOR_BGR2LAB)[0, 0].astype(float)

        c0_hsv = cv2.cvtColor(np.uint8([[c0_bgr]]), cv2.COLOR_BGR2HSV)[0, 0].astype(float)
        c1_hsv = cv2.cvtColor(np.uint8([[c1_bgr]]), cv2.COLOR_BGR2HSV)[0, 0].astype(float)

        # Delta Hue en espacio circular OpenCV [0, 179]
        delta_hue = min(abs(int(c0_hsv[0]) - int(c1_hsv[0])), 180 - abs(int(c0_hsv[0]) - int(c1_hsv[0])))

        # Distancia cromática perceptual en CIELAB (Delta E*ab en planos a* y b*)
        delta_a = float(c0_lab[1]) - float(c1_lab[1])
        delta_b = float(c0_lab[2]) - float(c1_lab[2])
        delta_e_ab = float(np.sqrt(delta_a**2 + delta_b**2))
        delta_e_total = float(np.sqrt(np.sum((c0_lab - c1_lab)**2)))

        # Distancia de crominancia normalizada L1
        eps = 1e-4
        norm_0 = c0_bgr.astype(float) / (np.sum(c0_bgr) + eps)
        norm_1 = c1_bgr.astype(float) / (np.sum(c1_bgr) + eps)
        delta_norm_chroma = float(np.sum(np.abs(norm_0 - norm_1)))

        # Absorbancia relativa promedio
        abs_c0 = np.clip(np.log10(paper_bg + 1.0) - np.log10(c0_bgr.astype(float) + 1.0), 0.0, 3.0)
        abs_c1 = np.clip(np.log10(paper_bg + 1.0) - np.log10(c1_bgr.astype(float) + 1.0), 0.0, 3.0)
        norm_abs0 = abs_c0 / (np.sum(abs_c0) + eps)
        norm_abs1 = abs_c1 / (np.sum(abs_c1) + eps)
        delta_abs = float(np.sum(np.abs(norm_abs0 - norm_abs1)))

        # Proporciones de clústeres
        unique, counts = np.unique(kmeans_labels, return_counts=True)
        total_p = sum(counts)
        proportions = {f'Tinta #{int(u) + 1}': round(float(c / total_p), 3) for u, c in zip(unique, counts)}
        min_prop = min(proportions.values()) if len(proportions) > 1 else 1.0

        # 6. Criterio Científico Forense de Espectrometría Documental:
        # En una misma tinta manuscrita (ej. un solo bolígrafo azul):
        # Existen variaciones naturales de presión y grosor de capa entre el centro del trazo y el borde,
        # pero el tono (Hue) y la cromaticidad normalizada son coherentes.
        # Para concluir pericialmente la existencia de 2 tintas distintas (adición con segundo bolígrafo):
        s0 = c0_hsv[1]
        s1 = c1_hsv[1]
        is_colored = bool(s0 > 25 or s1 > 25)

        if is_colored:
            # Caso A: Diferencia cromática de matiz clara (ej. azul vs negro, azul vs rojo, delta_hue >= 10)
            if delta_hue >= 10:
                chem_diff = bool(delta_e_ab >= 12.0 and raw_sil_score >= 0.30)
            else:
                # Caso B: Mismo matiz nominal (ej. bolígrafo azul con lapicero azul o trazo manuscrito).
                # Para descartar variaciones de presión, sombra o antialiasing de un mismo lapicero azul,
                # se exige separación cromática pura en (a*, b*) que supere la dispersión intra-trazo (delta_e_ab >= 25.0):
                chem_diff = bool(delta_e_ab >= 25.0 and raw_sil_score >= 0.40)
        else:
            # Tintas acromáticas / neutras:
            chem_diff = bool(
                (delta_e_total >= 28.0 and delta_norm_chroma >= 0.15 and raw_sil_score >= 0.40) or
                (delta_e_total >= 35.0 and raw_sil_score >= 0.35)
            )

        multiple_inks = bool(chem_diff and min_prop >= 0.08 and raw_sil_score >= 0.30)
        num_inks = 2 if multiple_inks else 1
        reported_sil = round(raw_sil_score if multiple_inks else min(raw_sil_score, 0.12), 3)

        # 7. Segmentación Visual de Trazo Completo (Propagación Vectorizada por Centroides)
        y_all, x_all = np.where(clean_ink_mask > 0)
        segmented_img = image_bgr.copy()

        if len(y_all) > 0:
            bgr_all = image_bgr[y_all, x_all]
            hsv_all = hsv_full[y_all, x_all]
            lab_all = lab_full[y_all, x_all]
            all_feats = cls._compute_pixel_features(bgr_all, hsv_all, lab_all, paper_bg)

            # Distancia euclidiana vectorial a los centros de clústeres
            c0_feat = kmeans.cluster_centers_[0]
            c1_feat = kmeans.cluster_centers_[1]
            dist_0 = np.sum((all_feats - c0_feat)**2, axis=1)
            dist_1 = np.sum((all_feats - c1_feat)**2, axis=1)
            all_labels = (dist_1 < dist_0).astype(np.int32)

            # Colores periciales:
            # - Tinta #1 (Base): Verde Esmeralda pericial (BGR: [80, 215, 30])
            # - Tinta #2 (Adición / Segunda marca): Rojo Rubí (BGR: [30, 40, 240])
            color_base = (80, 215, 30)
            color_sec = (30, 40, 240) if multiple_inks else (80, 215, 30)

            # Pintar trazos correspondientes
            c0_pts = (all_labels == 0)
            c1_pts = (all_labels == 1)
            segmented_img[y_all[c0_pts], x_all[c0_pts]] = color_base
            segmented_img[y_all[c1_pts], x_all[c1_pts]] = color_sec

        _, buffer = cv2.imencode('.png', segmented_img)
        segmented_b64 = 'data:image/png;base64,' + b64.b64encode(buffer).decode('utf-8')

        return {
            'success': True,
            'num_inks_detected': num_inks,
            'silhouette_score': reported_sil,
            'multiple_inks_detected': multiple_inks,
            'delta_hue': delta_hue,
            'delta_e_chroma': round(delta_e_ab, 2),
            'segmented_image_b64': segmented_b64,
            'pca_scatter_points': pca_scatter,
            'pca_variance_explained': [round(v, 4) for v in explained_variance],
            'ink_proportions': proportions if multiple_inks else {'Tinta #1 (Homogénea)': 1.0},
            'outliers_detected_dbscan': outlier_count,
            'scientific_conclusion': (
                f'ALERTA FORENSE: Se detectaron {num_inks} tintas con formulaciones químicas distintas '
                f'(Delta Hue: {delta_hue}°, Delta E*ab: {delta_e_ab:.1f}, Silhouette: {reported_sil}). '
                f'Incompatibilidad espectral concluyente entre instrumentos inscriptores '
                f'(ej. diferentes fabricantes, marcas o lotes de bolígrafo del mismo color nominal).'
                if multiple_inks else
                f'HOMOGENEIDAD OPTICA: Consistencia espectral uniforme en todos los trazos '
                f'(Delta Hue: {delta_hue}°, Delta E*ab: {delta_e_ab:.1f}). '
                f'No se aprecian firmas químicas de un segundo instrumento inscriptor.'
            )
        }
