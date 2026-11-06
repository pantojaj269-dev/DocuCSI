# DocuCSI: Suite Neuro-Simbólica de Peritaje Documental Forense

Plataforma inteligente de investigación criminalística de documentos basada en visión computacional, aprendizaje automático (supervisado y no supervisado), redes neuronales profundas (Deep Learning), búsqueda informada ($A^*$) y sistemas expertos basados en reglas.

---

## 🎯 Mapeo Sistemático con los Temas del Sílabo

| Unidad / Tema del Sílabo | Módulo en DocuCSI | Implementación Técnica |
| :--- | :--- | :--- |
| **Agentes Inteligentes & Arquitectura** | Agente Pericial PEAS | Percepción (Cámara web / archivos), Entorno (Documentos y cheques), Actuadores (Dictamen judicial, alertas, segmentación), Arquitectura cliente-servidor FastAPI + React. |
| **Visión & Procesamiento de Imágenes** | `modules/vision/processor.py` | Homografía de 4 puntos (rectificación de perspectiva), umbralización combinada Otsu y adaptativa, esqueletización morfológica (Zhang-Suen). |
| **Aprendizaje No Supervisado** | `modules/inks/analyzer.py` | **K-Means y DBSCAN** sobre espacio de color LAB/HSV para detección de múltiples tintas y anomalías; **PCA (2D)** para reducción de dimensionalidad; **Silhouette Score** para validación científica. |
| **Aprendizaje Supervisado I y II** | `modules/tampering/detector.py` | Detección de cifras adulteradas y enmiendas. Comparativa de **Regresión Logística, KNN, SVM, Árboles de Decisión, Random Forest y Gradient Boosting**. Matriz de confusión, Accuracy, Precision, Recall, F1 y curvas ROC-AUC. |
| **Deep Learning & Redes Neuronales** | `modules/signatures/verifier.py` | Red Densa Multicapa (MLP) en **PyTorch** con Dropout, BatchNorm, Sigmoid, función de pérdida BCELoss y optimizador Adam; curva de pérdida por épocas. |
| **Regresión Numérica** | `modules/signatures/verifier.py` | **Regresión Ridge** para estimación de velocidad cinemática y presión motora sobre el trazo. |
| **Búsqueda Informada ($A^*$)** | `modules/chronology/a_star.py` | Algoritmo **$A^*$ con heurística euclidiana** para resolver la cronología de trazos cruzados (fraude de "Firma en Blanco"). |
| **Sistemas Expertos & IA Simbólica** | `modules/expert_system/engine.py` | Base de conocimiento formal con las **Leyes de la Grafotecnia (Solange Pellat)** y reglas procesales; motor de inferencia explicable (Forward Chaining). |
| **Ética, IA Responsable & Custodia** | `modules/expert_system/engine.py` | Cadena de custodia forense con **Hash SHA-256**, explicabilidad transparente de decisiones y prevención de condenas erróneas. |

---

## 🚀 Cómo Iniciar el Proyecto

### Opción 1: Ejecución Rápida con 1 Clic (Recomendada en Windows)
Haz doble clic en:
* `iniciar_proyecto.bat`: Inicia automáticamente el Backend en `http://127.0.0.1:8000` y el Frontend en `http://localhost:5173`.

### Opción 2: Desde Terminales Separadas

**Terminal 1 (Backend):**
```bash
cd Backend
python main.py
```

**Terminal 2 (Frontend):**
```bash
cd Frontend
npm run dev
```

Abre tu navegador en: `http://localhost:5173`

---

## 🔬 Cómo Realizar las Pruebas y Exposición

1. **Uso de la Cámara Web en Vivo:**
   - Haz clic en **"Cámara en Vivo"**.
   - Coloca una hoja con una firma o un cheque bajo la cámara de tu laptop.
   - Haz clic en **"Capturar Documento para Peritaje"**.

2. **Uso de Casos Simulados (Demo Instantánea con 1 Clic):**
   - **Cheque Legítimo:** Documento limpio con tinta homogénea y firma fluida.
   - **Cheque Adulterado:** Cifra alterada de `$100` a `$1000` con adición de un cero en tinta distinta (activa K-Means, Silhouette > 0.60 y Random Forest).
   - **Contrato con Firma Falsificada:** Firma lenta con temblores espasmódicos (activa la Red Densa PyTorch y la Segunda Ley de Pellat).
   - **Abuso de Firma en Blanco:** Cláusula impresa por encima de una firma previa (activa el algoritmo $A^*$ demostrando que el texto está en la capa superior).

3. **Descarga del Dictamen Judicial:**
   - En la pestaña **6. Dictamen Judicial**, puedes revisar el informe pericial formal y hacer clic en **"Imprimir / Exportar PDF"** para tu informe académico.
