# Revisión para la presentación — 12 de noviembre de 2026

## Resultado verificado localmente

- Backend: 9 pruebas de integración aprobadas, con las 4 muestras incluidas.
- Frontend: 7 pruebas del cliente HTTP aprobadas; build de producción y lint correctos, sin advertencias.
- Prueba de concurrencia: la API de salud sigue respondiendo durante un análisis; otra petición pesada recibe 503 con un mensaje para reintentar, evitando acumular trabajo en la memoria de Render.
- Los resultados repetidos de tintas son estables para la misma imagen.
- Cheque limpio sin alertas; las otras tres muestras activan alertas del prototipo.

## Demora del peritaje

En esta computadora, las muestras tardaron aproximadamente 0,24–1,06 s antes y 0,16–0,34 s después de los cambios. Son mediciones locales de solicitudes con el servidor ya iniciado, no tiempos garantizados en producción. El arranque completo medido pasó aproximadamente de 7,5 a 6,2 s.

Se vectorizaron el filtrado de componentes de tinta y el mapa de costos de A*, se limitó el uso de hilos de las bibliotecas numéricas y se acotó la resolución de análisis a 1600 píxeles en el lado mayor, conservando la proporción. Las imágenes aceptadas pueden tener hasta 16 MB y 24 megapíxeles; el análisis se realiza sobre la copia reducida. Las fotos muy grandes pueden perder detalle fino en esta copia.

Los modelos aún se entrenan al iniciar cada proceso. No se entrenan en cada clic en ejecutar. Ese costo se suma al arranque de Render; no se implementó almacenamiento persistente de modelos.

Render documenta que sus servicios gratuitos se suspenden después de 15 minutos sin tráfico y pueden tardar alrededor de un minuto en arrancar: https://render.com/docs/free y https://render.com/docs/faq. El código del proyecto declara un plan gratuito en render.yaml; no se verificó el plan real de la cuenta.

La interfaz ahora conecta primero con /api/health, muestra el estado y el tiempo transcurrido, limita cada espera de red a 120 segundos y presenta errores HTTP o de conexión. El chequeo inicial y el análisis son dos solicitudes separadas, por lo que el límite total puede superar dos minutos. No se reintentan automáticamente los análisis para evitar duplicarlos.

## Otras correcciones

- Al cambiar de imagen se descartan los resultados de ambos tipos de análisis. Las respuestas de una imagen anterior no se muestran sobre la nueva.
- El cotejo dual distingue respuestas exitosas de rechazos y errores.
- El botón de cámara ya no recibe el evento del clic como si fuera un identificador de dispositivo; la cámara libera sus pistas al desmontar la aplicación.
- La captura espera un fotograma válido; la carga comprueba formato y tamaño.
- Las muestras se localizan respecto del archivo del backend, independientemente del directorio de ejecución.
- El hash SHA-256 corresponde al archivo recibido antes de transformaciones.
- Los expedientes tienen identificadores distintos y fecha explícita en UTC.
- Se añadieron reglas de impresión para incluir el informe completo, sin limitarlo a la altura del visor. Pendiente de verificación visual en navegador.
- Docker instala PyTorch desde el índice exclusivo de CPU para evitar descargar paquetes de GPU innecesarios.

## Qué explicar con precisión en la sustentación

DocuCSI es un prototipo académico. El benchmark de seis clasificadores, el MLP y Ridge se entrenan con datos sintéticos. Sus métricas no demuestran precisión sobre documentos reales.

En el código actual, el resultado individual de firmas se calcula con una heurística de contornos/temblores. Aunque el MLP y Ridge se entrenan y se muestra la curva de pérdida, no producen ese resultado de inferencia. El cotejo dual usa descriptores y distancias morfológicas. La interfaz y el informe aclaran su alcance orientativo.

El análisis RGB de tintas identifica diferencias de color; no prueba composición química o fabricante. A* explora continuidad de píxeles; no demuestra por sí solo qué tinta se depositó primero. Cuando no encuentra un recorrido, la implementación usa un costo de referencia de 999; ese comportamiento es parte de la heurística y no una medición física.

La puntuación de las reglas es una suma de pesos, no una probabilidad calibrada. Un hash identifica bytes y ayuda a comparar integridad entre copias; por sí solo no acredita procedencia ni una cadena de custodia judicial completa. Se ajustó la conclusión global del informe para evitar declarar autenticidad o fraude concluyentes.

## Verificación pendiente de producción

No se dispuso de la URL real de Vercel ni de Render. No se verificaron el estado del despliegue, las variables de entorno, los logs, el consumo real de memoria ni los tiempos del servicio publicado. El navegador de pruebas de esta sesión no estuvo disponible, por lo que tampoco se comprobó visualmente el diseño, la cámara real o la vista previa de impresión.

Estos cambios están en la copia local: requieren subir los archivos modificados y completar los despliegues de backend y frontend. No se ejecutó commit, push ni despliegue. Las modificaciones previas del usuario, incluidos documentos y eliminaciones de imágenes, se dejaron intactas.

Para Vercel, confirmar VITE_API_BASE_URL con la URL HTTPS del servicio real de Render y volver a desplegar el frontend si se cambia. Esa variable se incorpora durante el build.

## Ensayo recomendado para mañana

1. Abrir la web 5–10 minutos antes y esperar a que indique servidor conectado.
2. Ejecutar el cheque limpio y comprobar las seis pestañas.
3. Ejecutar el cheque adulterado, contrato y firma en blanco.
4. Ensayar el cotejo dual con dos firmas claramente separadas.
5. Revisar Imprimir / Exportar PDF antes de la presentación.
6. Tener lista la ejecución local con iniciar_proyecto.bat como respaldo si falla Internet.

Para repetir las comprobaciones automáticas:

```powershell
cd Backend
python -m unittest discover -s tests -v
cd ../Frontend
npm.cmd test
npm.cmd run lint
npm.cmd run build
```

Las pruebas del backend requieren las dependencias de Backend/requirements.txt y httpx, disponibles en el entorno usado para esta revisión.
