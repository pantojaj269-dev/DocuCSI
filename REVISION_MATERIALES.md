# Revisión del caso azul + lápiz negro — versión 1.2.0

## Defecto confirmado

La corrección 1.1.0 excluía indiscriminadamente todos los trazos de baja saturación del análisis cromático al detectar azul. Eso también descartaba lápiz, tinta negra y marcas reales. La máscara de entrada combinaba un umbral absoluto de oscuridad con apertura de 2 px que podía borrar escritura tenue o de 1 px.

Además, el clasificador ilustrativo de formas anotaba «LEGÍTIMO» cuando no activaba su criterio, aunque no había evaluado la composición de los trazos ni la autenticidad del documento.

## Corrección

- Se conserva un inventario separado de trazos cromáticos y neutros. Negro/gris ya no se descarta por asumir que es impresión.
- Se estima contraste respecto del papel local, conservando trazos finos sin la apertura que los eliminaba. Se filtran componentes pequeños de ruido.
- Se compensa moderadamente el tono del papel y se separa el halo de antialias del azul de las marcas neutras independientes.
- Los resultados incluyen cantidad de píxeles de ambos tipos, presencia de mezcla, evidencia visible de trazos tenues e identidad material no determinada. Los neutros se resaltan en violeta en la segmentación.
- Mezcla azul + negro/gris exige contexto. Puede ser lápiz, impresión o tinta negra; no se declara cuál ni se confunde la observación con fraude. En un formulario legítimo con impresión gris, también se informa esa mezcla sin sumar puntos de sospecha por ella sola.
- Se eliminó «LEGÍTIMO» de las anotaciones del clasificador. Diferencia entre «sin señal del modelo» y «no evaluable» cuando no hay caracteres compatibles.
- El informe nunca certifica legitimidad al no encontrar una señal. Expone los límites del análisis y advertencias exploratorias de enfoque, contraste y resolución.
- La rectificación deja de elegir cajas internas pequeñas como si fueran el documento entero. Se comprueban dimensiones de imagen antes de reservar el bitmap completo.

## Validación local

La foto del usuario `lapicero azul y lapiz negro.jpeg` se aceptó con y sin depender de un borde de papel. En el análisis verificado se detectaron 49 105 píxeles cromáticos y 30 216 neutros, y el resultado global indicó mezcla visual que requiere contexto. Esa foto se mantiene local y no se incluye en Git.

La batería incluye azul + neutro en cinco intensidades de gris y tres grosores, lápiz de bajo contraste, papel cálido, sombras graduales, reducción de tamaño, JPEG, halos de tinta azul, ruido leve de papel, cajas internas, imágenes excesivamente grandes y el flujo de API completo. Se mantienen las pruebas de concurrencia, muestras originales, hash, errores de entrada, comparación dual y cruces de trazos.

Los ensayos anteriores se actualizaron para comprobar dos hechos distintos: impresión gris + azul debe conservar ambos, pero esa observación sola no debe convertirse en fraude; la separación entre dos colores saturados sigue siendo otro resultado. En una variante degradada de firma imitada, la morfología queda no concluyente en lugar de forzar la misma clasificación.

Estos ensayos no constituyen validación de identificación química de grafito o tintas ni una garantía sobre todas las fotografías. Los modelos supervisados siguen entrenados con datos sintéticos; las métricas mostradas no representan precisión real en documentos de usuarios. A* conserva su alcance de conectividad y no prueba el orden físico de escritura.

La comprobación de dimensiones usa la lectura diferida de cabeceras de [Pillow](https://pillow.readthedocs.io/en/stable/reference/Image.html). La segmentación y extracción de características se realizan con OpenCV y scikit-learn.

El despliegue se identifica con `/api/health` y `analysis_version` en la respuesta de análisis, ambos con versión 1.2.0. La comprobación de producción se efectúa después de publicar el commit.
