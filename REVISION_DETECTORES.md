# Corrección de detectores — versión 1.1.0

## Problema reproducido

Las imágenes nuevas con escritura a lapicero expusieron defectos que las muestras iniciales no revelaban: impresión gris contada como segunda tinta, rugosidad de contornos convertida en falsificación y un detector de cruces dependiente de líneas horizontales/verticales perfectas. El papel crema también se confundía con piel.

## Comportamiento corregido

- El análisis cromático separa trazos neutros de escritura saturada cuando existen suficientes píxeles de color. Informa grupos de color, sin inferir composición química, fabricante ni fecha de escritura. Cambios de brillo dentro de un mismo tono no se convierten en otra tinta. Silhouette se informa sin el recorte artificial anterior; su valor no es una probabilidad de fraude.
- La firma se evalúa con suavizado leve, normalización de tamaño y diferencia de rugosidad entre escalas. El resultado describe morfología; no declara auténtica o falsa una firma aislada ni inventa probabilidad de autenticidad, presión o velocidad físicas. Si otro trazo cruza la región de firma, la morfología mezclada queda no concluyente y no suma automáticamente una segunda alerta de firma.
- Se buscan líneas neutras mediante Hough y evidencia de escritura coloreada a ambos lados del cruce, con tolerancia a inclinación. A* explora conectividad en una ventana acotada. Nunca se convierte el recorrido ausente en costo 999 para declarar un orden físico. Se muestran costos ausentes como tales y cero nodos si no se ejecutó búsqueda.
- Se informa «cruce detectado: orden no concluyente». El indicador de fraude de firma en blanco queda sin determinar: el orden de depósito de tintas no se demuestra a partir de estas fotos RGB.
- Los colores de papel cálido con baja saturación no activan por sí solos el filtro cromático de fondo. Ese filtro ya no afirma detectar rostros.
- El sistema experto y la interfaz usan observaciones de evidencia y estados de incertidumbre. Varios colores por sí solos generan una observación contextual, no una declaración de fraude.

## Verificación

23 métodos de prueba del backend y 7 del cliente HTTP aprobados, más compilación de producción y lint del frontend. Dentro de esos métodos se prueban, entre otros, 18 combinaciones de cruces con inclinación, escala y orden de dibujo; 12 combinaciones de las cuatro fotos con escala y contraste; impresión de varios niveles de gris, tinta del mismo tono con diferentes intensidades, rojo/azul, firma sin referencia y papel crema.

Las cuatro muestras rápidas originales mantienen análisis exitosos; el cheque limpio queda sin alertas relevantes. Los cuatro cheques originales generados y los cuatro de estilo lapicero también se analizaron durante la revisión local.

Resultados locales de los cuatro cheques de estilo lapicero:

| Archivo | Resultado del módulo pertinente |
| --- | --- |
| 01 limpio | Sin diferencia cromática significativa, sin anomalía morfológica y sin cruce; puntuación de reglas 0. |
| 02 alterado | Dos grupos cromáticos; observación contextual, sin alerta de firma ni cruce. |
| 03 firma imitada | Irregularidad morfológica; requiere cotejo, sin declarar falsificación. |
| 04 firma en blanco simulada | Cruce visible; orden físico y morfología de firma mezclada no concluyentes. |

## Límites de la validación

Son pruebas de regresión sobre imágenes generadas y geometrías sintéticas. No constituyen evaluación de precisión sobre una población independiente de documentos reales ni permiten prometer ausencia de falsos positivos. La normalización de firmas y sus umbrales siguen siendo heurísticos. El recorte de firma aún parte de la región inferior derecha y puede no corresponder a una firma en otros diseños.

La detección de cruces requiere línea neutra y escritura de color con contraste suficiente; no resuelve cruces de un mismo color ni todos los trazos curvos. No detectar un cruce no equivale a certificar su ausencia. Excluir trazos neutros del análisis de color también implica no clasificar un posible segundo bolígrafo negro en ese módulo; el informe explicita ese alcance.

Los seis clasificadores, el MLP y Ridge siguen entrenados con datos sintéticos. El MLP y Ridge son parte del entrenamiento ilustrativo, no de la decisión morfológica de firma. No se añadieron reglas por nombre, hash o identidad de las imágenes de presentación. Las fotos no se alteraron para esta corrección.

Referencias técnicas de los operadores usados: [Hough en OpenCV](https://docs.opencv.org/4.x/d9/db0/tutorial_hough_lines.html) y [contornos y aproximación poligonal en OpenCV](https://docs.opencv.org/4.x/dd/d49/tutorial_py_contour_features.html).

La verificación de despliegue debe comprobar /api/health con versión 1.1.0 y repetir las cargas contra el servicio publicado. Los resultados de producción se guardarán junto a las imágenes locales al terminar esa comprobación.
