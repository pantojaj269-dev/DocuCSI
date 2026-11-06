# MEMORIA TÉCNICA, BITÁCORA Y GUÍA DE SUSTENTACIÓN
## Proyecto DocuCSI: Suite Neuro-Simbólica de Peritaje Documental Forense

---

### 1. Evolución del Proyecto (De la Idea a la Suite Forense)
1. **Origen de la Propuesta:**
   * Al inicio se buscaban proyectos relacionados con Criminalística y Ciencias Forenses con uso de cámara.
   * Se descartaron balística y manchas de sangre por la dificultad de acceso a muestras biológicas reales siendo estudiante.
   * Se eligió el peritaje grafotécnico y documentoscopía documental.
2. **Evolución del Alcance:**
   * Para ir más allá de un clasificador de firmas simple, se transformó en un **Agente Inteligente Integral (DocuCSI)** que cubre **todas las unidades temáticas del sílabo del curso**:
     - No supervisado (K-Means, PCA, Silhouette) para espectrometría de tintas.
     - Supervisado (LogReg, KNN, SVM, Decision Tree, Random Forest, Gradient Boosting) para enmiendas de cifras.
     - Deep Learning (PyTorch MLP con BCELoss y Adam) y Regresión Ridge para dinámica motora de firmas (Leyes de Solange Pellat).
     - Búsqueda informada ($A^*$) para orden cronológico de trazos y fraude de firma en blanco.
     - Sistema Experto con reglas formales y Cadena de Custodia Criptográfica (SHA-256).
     - Modo Cotejo Grafotécnico Dual (Firma original vs. Firma imitada en una misma hoja).

---

### 2. Conceptos Técnicos y Forenses Fundamentales (Para Estudiar)

#### A. Espectrometría de Tintas (K-Means, PCA y Silhouette Score)
* **¿Qué hace?** En un documento, aísla los píxeles de tinta y extrae sus vectores cromáticos en espacios **HSV** y **CIELAB**.
* **¿Cómo detecta la enmienda?** K-Means ($k=2$) agrupa los píxeles. En un mismo bolígrafo (incluso con sombras o cambios de presión), el ángulo de tono químico es idéntico ($\Delta \text{Hue} \le 6^\circ$). Si alguien usa otro bolígrafo (incluso ambos siendo azules o negros de distinta marca), la fórmula química cambia ($\Delta \text{Hue} \ge 13^\circ$).
* **PCA 2D y Silhouette Score:** PCA reduce las dimensiones para graficar los datos en la pantalla. El *Silhouette Score* mide cuantitativamente qué tan separados están los grupos químicos de tinta.

#### B. Detección de Enmiendas en Cifras (Gradient Boosting & Branch Points)
* **¿Qué hace?** Analiza cada número o palabra (como en la casilla de monto de un cheque).
* **Branch points (puntos de ramificación):** Al adelgazar el trazo a su esqueleto de 1 píxel, se cuentan los cruces de líneas. Una letra natural tiene 2 o 3 cruces; si alguien retoca un número (ej. convertir un `100` en `1000` o alterar un `3` a un `8`), se generan ramificaciones forzadas y bordes anómalos que el clasificador **Gradient Boosting** detecta al instante.

#### C. Biomecánica de Firmas (Segunda Ley de Solange Pellat & PyTorch MLP)
* **¿Qué es la Segunda Ley de Pellat?** 
  - Al firmar el titular genuino, su cerebro ejecuta el trazo por **automatismo motor espontáneo** (rápido, continuo y fluido).
  - Al intentar **imitar o copiar** una firma, el falsificador dibuja con lentitud y miedo a equivocarse, provocando **micro-temblores involuntarios (*ataxia gráfica*)** y una fuerte caída en la velocidad.
* **PyTorch MLP:** Red neuronal densa que procesa descriptores morfológicos para clasificar firmas auténticas vs. imitaciones serviles.

#### D. Cruce Cronológico de Trazos y Abuso de Firma en Blanco (Algoritmo $A^*$)
* **El delito de Firma en Blanco:** Cuando alguien hace firmar una hoja vacía y luego imprime un texto abusivo encima de la firma.
* **Búsqueda informada $A^*$:** Modela la intersección física como un grafo de costos. El trazo impreso que superpone físicamente a la firma conserva un camino continuo de tinta sin cortes (menor costo heurístico para $A^*$), demostrando concluyentemente que el texto fue redactado **después** de firmar.

#### E. Modo Cotejo Dual (2 Firmas en la Misma Hoja)
* Permite escribir en una hoja la firma original a la izquierda (**Indubitada**) y la imitación a la derecha (**Dubitada**).
* El algoritmo segmenta ambas mitades, calcula la **similitud morfológica** (coseno vectorial) y contrasta los índices de temblor y velocidad, demostrando que aunque la forma se parezca, la firma imitada sufre inhibición motora.

---

### 3. La Gran Lección Experimental: Cámara Web vs. Foto de Celular
* **El experimento:** En el mismo documento en papel, una foto de celular activaba 2 reglas, mientras que la cámara web de la laptop activaba 4 reglas.
* **La razón científica (Relación Señal/Ruido y Resolución Óptica):**
  - La foto de celular (12 a 48 MP) entrega un trazo limpio, nítido y congelado.
  - La cámara de laptop (0.9 MP a 720p) sufre de desenfoque, compresión WebRTC y micro-movimiento al sostener la hoja en el aire. La baja resolución genera **escalonamiento digital de píxeles (aliasing o efecto sierra)**; los algoritmos matemáticos confunden ese serrucho digital con temblores de mano (ataxia) y ensanchamiento de trazo.
* **Conexión con el Sílabo:** Demuestra la importancia de la fase de percepción y calibración de sensores en un Agente Inteligente, y cumple con las normas de evidencia digital forense (**ISO/IEC 17025**).

---

### 4. Preguntas Típicas del Jurado / Profesor y Respuestas Magistrales

* **P1: ¿Por qué usaron K-Means en HSV/LAB y no simplemente distancia RGB?**  
  *R:* "Profesor, el espacio RGB mezcla la luz con el color, por lo que una sombra engañaría al sistema. HSV y LAB desacoplan la luminancia de la crominancia. Al medir el ángulo espectral ($\Delta \text{Hue}$), detectamos la fórmula química del colorante independientemente de la iluminación ambiental."

* **P2: ¿Por qué usaron A\* para el cruce de líneas y no un modelo de Deep Learning convolucional?**  
  *R:* "Por el principio de Transparencia y Explicabilidad (XAI). En un tribunal penal, un modelo de caja negra puede ser impugnado por la defensa. El algoritmo $A^*$ ofrece una demostración matemática formal y reproducible de la continuidad del flujo de tinta en el grafo de intersección."

* **P3: ¿Cómo se protege la integridad de la prueba para que no se altere en el software?**  
  *R:* "Implementamos Cadena de Custodia Digital mediante Hashing Criptográfico SHA-256. Al ingresar la imagen, se genera su firma digital única; si se alterara un solo bit de la evidencia, el hash del dictamen cambiaría por completo, invalidando el peritaje."

---

### 5. Archivos del Proyecto Generados para Presentación
* `Propuesta_Proyecto_DocuCSI.docx`: Documento formal de propuesta académica para el profesor.
* `Memoria_Completa_y_Guia_Sustentacion.docx`: Memoria técnica detallada en Word con todas las respuestas y explicaciones.
* `Frontend/`: Dashboard web con la nueva paleta beige minimalista y modo de cotejo dual de firmas.
* `Backend/`: Microservicio en FastAPI con los modelos de PyTorch, Scikit-Learn y OpenCV.
