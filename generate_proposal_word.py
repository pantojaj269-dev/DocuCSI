import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def create_proposal_docx(output_path):
    doc = docx.Document()

    # Configuración de márgenes estándar (2.5 cm)
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    # Colores institucionales
    NAVY = RGBColor(16, 44, 87)       # #102C57
    CYAN = RGBColor(0, 141, 218)      # #008DDA
    DARK_GRAY = RGBColor(50, 50, 50)  # #323232
    WHITE = RGBColor(255, 255, 255)

    # -------------------------------------------------------------
    # ENCABEZADO Y TÍTULO
    # -------------------------------------------------------------
    p_cat = doc.add_paragraph()
    p_cat.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_cat = p_cat.add_run("PROPUESTA DE PROYECTO DE CURSO — MACHINE LEARNING & INTELIGENCIA ARTIFICIAL")
    run_cat.font.name = "Arial"
    run_cat.font.size = Pt(10)
    run_cat.font.bold = True
    run_cat.font.color.rgb = CYAN

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(4)
    p_title.paragraph_format.space_after = Pt(6)
    run_title = p_title.add_run("DocuCSI: Suite Neuro-Simbólica de Peritaje Documental Forense basada en Agentes Inteligentes, Visión Computacional y Aprendizaje Automático Híbrido")
    run_title.font.name = "Arial"
    run_title.font.size = Pt(18)
    run_title.font.bold = True
    run_title.font.color.rgb = NAVY

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_after = Pt(18)
    run_sub = p_sub.add_run("Área: Criminalística Digital, Documentoscopía Forense y Visión Artificial | Enfoque: Neuro-Simbólico")
    run_sub.font.name = "Arial"
    run_sub.font.size = Pt(10)
    run_sub.font.italic = True
    run_sub.font.color.rgb = DARK_GRAY

    # Separador horizontal
    p_line = doc.add_paragraph()
    p_line.paragraph_format.space_after = Pt(14)
    p_line_run = p_line.add_run("―" * 60)
    p_line_run.font.color.rgb = CYAN
    p_line.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Helper para encabezados de sección
    def add_section_header(title):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(title)
        run.font.name = "Arial"
        run.font.size = Pt(13)
        run.font.bold = True
        run.font.color.rgb = NAVY
        return p

    def add_body_p(text, bold_prefix=None, space_after=6):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = 1.15
        if bold_prefix:
            r_pre = p.add_run(bold_prefix)
            r_pre.font.name = "Arial"
            r_pre.font.size = Pt(10)
            r_pre.font.bold = True
            r_pre.font.color.rgb = DARK_GRAY
        r_text = p.add_run(text)
        r_text.font.name = "Arial"
        r_text.font.size = Pt(10)
        r_text.font.color.rgb = DARK_GRAY
        return p

    # -------------------------------------------------------------
    # 1. PLANTEAMIENTO DEL PROBLEMA
    # -------------------------------------------------------------
    add_section_header("1. Planteamiento del Problema y Justificación")
    add_body_p(
        "El fraude documental en contratos privados, pagarés, cheques de gerencia y títulos valores representa anualmente pérdidas millonarias en el sistema financiero y procesal judicial. Las modalidades delictivas de mayor incidencia en la práctica forense corresponden a:",
        None
    )

    bullet_points = [
        ("Adulteración de cifras y enmiendas morfológicas: ", "Modificación dolosa de montos o fechas (ejemplo: conversión de $100 a $1000 mediante adición de ceros o retoques de trazo forzados)."),
        ("Multiplicidad de instrumentos inscriptores (adulteración de tintas): ", "Intervención de un segundo bolígrafo del mismo color aparente pero de distinta formulación química con posterioridad a la suscripción original."),
        ("Falsificación de firmas por imitación servil: ", "Supresión del automatismo motor natural del titular, manifestándose en titubeos, temblores espasmódicos y variaciones bruscas de velocidad (ataxia grafotécnica)."),
        ("Abuso de firma en blanco: ", "Redacción dolosa de cláusulas o montos impresos por encima de una firma preexistente que fue estampada en una hoja vacía.")
    ]
    for b_title, b_desc in bullet_points:
        p_b = doc.add_paragraph(style='List Bullet')
        p_b.paragraph_format.space_after = Pt(4)
        p_b.paragraph_format.line_spacing = 1.15
        r1 = p_b.add_run(b_title)
        r1.font.name = "Arial"
        r1.font.size = Pt(10)
        r1.font.bold = True
        r1.font.color.rgb = DARK_GRAY
        r2 = p_b.add_run(b_desc)
        r2.font.name = "Arial"
        r2.font.size = Pt(10)
        r2.font.color.rgb = DARK_GRAY

    add_body_p(
        "Actualmente, la documentoscopía tradicional depende de costosos microscopios espectrales y de la subjetividad interpretativa del perito. Esta propuesta formula el desarrollo de un Agente Inteligente Neuro-Simbólico capaz de percibir ópticamente el soporte en papel a través de una cámara digital, aislar la tinta con visión artificial, y orquestar modelos de Aprendizaje No Supervisado, Aprendizaje Supervisado, Deep Learning y Búsqueda Informada (A*) para emitir un dictamen judicial fundado, transparente y con cadena de custodia criptográfica.",
        None, space_after=10
    )

    # -------------------------------------------------------------
    # 2. OBJETIVOS DEL PROYECTO
    # -------------------------------------------------------------
    add_section_header("2. Objetivos del Proyecto")
    add_body_p(
        "Diseñar, implementar y evaluar experimentalmente un sistema inteligente neuro-simbólico de peritaje forense capaz de procesar imágenes de documentos capturadas en tiempo real para determinar autenticidad documental, discriminación de tintas, detección de enmiendas morfológicas, falsificación de firmas y orden cronológico de trazos cruzados.",
        "2.1. Objetivo General: "
    )

    add_body_p("Para la consecución del objetivo general, se plantean los siguientes objetivos específicos:", "2.2. Objetivos Específicos: ")
    sp_objs = [
        "Implementar un módulo de visión computacional (OpenCV) para la validación pericial de soportes (filtro anti-personas YCrCb), rectificación de perspectiva mediante homografía y binarización adaptativa de tinta.",
        "Desarrollar un subsistema de espectrometría óptica no supervisada empleando K-Means y DBSCAN en espacios cromáticos HSV y CIELAB, reduciendo la dimensionalidad con PCA (2D) y evaluando la separabilidad de tintas con Silhouette Score.",
        "Construir y contrastar un benchmark de 6 algoritmos de Aprendizaje Supervisado (Regresión Logística, KNN, SVM, Árboles de Decisión, Random Forest y Gradient Boosting) para la detección de enmiendas en cifras, evaluando matrices de confusión y curvas ROC-AUC.",
        "Diseñar e implementar una Red Neuronal Densa (MLP) en PyTorch combinada con Regresión Ridge para la autenticación biométrica de firmas y la estimación de presión motora según la Segunda Ley de Solange Pellat.",
        "Modelar la intersección física de tintas como un grafo de costos y formular el algoritmo de búsqueda informada A* para resolver la cronología de superposición de trazos (fraude de firma en blanco).",
        "Integrar un Sistema Experto basado en reglas documentoscópicas que sintetice la evidencia en un Dictamen Judicial Explicable respaldado por sellado criptográfico SHA-256."
    ]
    for obj in sp_objs:
        p_obj = doc.add_paragraph(style='List Bullet')
        p_obj.paragraph_format.space_after = Pt(4)
        p_obj.paragraph_format.line_spacing = 1.15
        r_obj = p_obj.add_run(obj)
        r_obj.font.name = "Arial"
        r_obj.font.size = Pt(10)
        r_obj.font.color.rgb = DARK_GRAY

    # -------------------------------------------------------------
    # 3. DEFINICIÓN DEL AGENTE INTELIGENTE (MODELO PEAS)
    # -------------------------------------------------------------
    add_section_header("3. Definición del Agente Inteligente (Estructura PEAS)")
    add_body_p("El sistema se conceptualiza formalmente bajo el paradigma de un Agente Racional Basado en Metas y Utilidad:")

    peas_data = [
        ("P (Performance / Rendimiento):", "Exactitud diagnóstica en clasificación (>92%), métrica Silhouette Score (>0.40) en discriminación de tintas químicas, AUC-ROC (>0.90) en detección de enmiendas, latencia de inferencia menor a 2.5 segundos y minimización estricta de falsos positivos en documentos auténticos."),
        ("E (Environment / Entorno):", "Documentos físicos sobre soporte de celulosa (cheques bancarios, pagarés, contratos impresos y cuadernos manuscritos) sujetos a condiciones de iluminación no uniforme y ruido de digitalización."),
        ("A (Actuators / Actuadores):", "Emisión automatizada del Dictamen Judicial Formal, renderizado de mapas coloreados de segmentación de tintas, trazado visual del camino de superposición A*, generación de alertas periciales y firma digital SHA-256."),
        ("S (Sensors / Sensores):", "Cámara digital en vivo (Webcam integrada / Cámara de smartphone en alta definición) e interfaz de digitalización para recepción de archivos fotográficos.")
    ]
    for p_title, p_desc in peas_data:
        add_body_p(p_desc, p_title, space_after=4)

    # -------------------------------------------------------------
    # 4. MATRIZ DE CUMPLIMIENTO CON EL SÍLABO DEL CURSO
    # -------------------------------------------------------------
    add_section_header("4. Matriz de Mapeo Técnico con el Sílabo del Curso")
    add_body_p("La siguiente tabla certifica la integración directa de los contenidos teóricos y prácticos de todas las unidades temáticas del sílabo:")

    table_data = [
        ("Unidad / Tema del Sílabo", "Aplicación Específica en DocuCSI", "Algoritmos y Herramientas"),
        ("1. Agentes Inteligentes & Arquitectura", "Diseño de un agente pericial PEAS, percepción, decisiones y arquitectura desacoplada.", "FastAPI (Microservicio Backend) + React (Frontend Dashboard)"),
        ("2. Visión Computacional & OpenCV", "Guardia de percepción (filtro dérmico YCrCb), corrección de perspectiva y binarización.", "OpenCV (cv2.warpPerspective, cv2.threshold Otsu, Zhang-Suen)"),
        ("3. Aprendizaje No Supervisado", "Espectrometría óptica de pigmentos de tinta, análisis de anomalías y reducción dimensional.", "K-Means (k=2), DBSCAN (outliers), PCA 2D y Silhouette Score"),
        ("4. Aprendizaje Supervisado I y II", "Clasificación de cifras y letras legítimas vs. enmiendas y adulteraciones forzadas.", "Benchmark comparativo: Regresión Logística, KNN, SVM, Decision Tree, Random Forest y Gradient Boosting. Curvas ROC y Matrices de Confusión."),
        ("5. Deep Learning (Redes Neuronales)", "Cotejo cinemático de firmas y detección de falsificación por imitación servil.", "MLP en PyTorch (Linear, BatchNorm, Dropout, BCELoss, Optimizador Adam) y curvas de pérdida por época."),
        ("6. Regresión Numérica", "Modelado de la presión gráfica y velocidad de arrastre del lapicero.", "Regresión Ridge para estimación de gradiente de presión."),
        ("7. Búsqueda Informada (A*)", "Resolución de la cronología de trazos cruzados (fraude de firma en blanco).", "Algoritmo A* con heurística de distancia Manhattan/Euclidiana sobre tensor de costo."),
        ("8. Sistemas Expertos & Lógica", "Motor de inferencia pericial para consolidación de dictámenes explicables.", "Base de conocimiento basada en las Leyes de Solange Pellat y encadenamiento hacia adelante."),
        ("9. Ética, IA Responsable & Custodia", "Validación anti-selfie fuera de dominio y cadena de custodia forense inmutable.", "Algoritmo de Hashing Criptográfico SHA-256 y explicabilidad de decisiones.")
    ]

    table = doc.add_table(rows=len(table_data), cols=3)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    # Anchos de columna: 3.5 cm, 7.5 cm, 5.0 cm aprox en pulgadas
    col_widths = [Inches(1.8), Inches(2.7), Inches(2.0)]

    for row_idx, row in enumerate(table.rows):
        is_header = (row_idx == 0)
        trPr = row._tr.get_or_add_trPr()
        trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))
        if is_header:
            trPr.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))

        for col_idx, cell in enumerate(row.cells):
            cell.width = col_widths[col_idx]
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            set_cell_margins(cell, top=120, bottom=120, left=140, right=140)

            data_text = table_data[row_idx][col_idx]
            cell.text = ""
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.05

            run = p.add_run(data_text)
            run.font.name = "Arial"

            if is_header:
                set_cell_background(cell, "102C57")
                run.font.size = Pt(9.5)
                run.font.bold = True
                run.font.color.rgb = WHITE
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            else:
                bg_color = "F7F9FC" if (row_idx % 2 == 1) else "FFFFFF"
                set_cell_background(cell, bg_color)
                run.font.size = Pt(8.5)
                run.font.color.rgb = DARK_GRAY
                if col_idx == 0:
                    run.font.bold = True
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT

    # -------------------------------------------------------------
    # 5. METODOLOGÍA Y DISEÑO EXPERIMENTAL
    # -------------------------------------------------------------
    doc.add_paragraph().paragraph_format.space_before = Pt(10)
    add_section_header("5. Metodología de Desarrollo y Diseño Experimental")
    add_body_p(
        "El proyecto adoptará una metodología experimental cuantitativa estructurada en cuatro fases concurrentes:",
        None
    )

    fases = [
        ("Fase I: Adquisición y Normalización de Evidencias: ", "Recepción de imágenes mediante cámara web y carga directa. Implementación de una Guardia de Percepción capaz de descartar entradas fuera de dominio (como rostros o fondos oscuros) mediante análisis de crominancia dérmica en espacio YCrCb. Enderezamiento del documento mediante homografía planar."),
        ("Fase II: Extracción de Características Multidimensionales: ", "Segmentación binaria del documento. Extracción de descriptores de forma (relación de aspecto, densidad de masa, entropía de gradiente con operador Sobel normalizado, recuento de bifurcaciones o branch points en el esqueleto morfológico) y firmas cromáticas triestímulo (HSV y CIELAB)."),
        ("Fase III: Entrenamiento y Validación Cruzada de Modelos: ", "Partición experimental de datos en 70% entrenamiento y 30% prueba. Entrenamiento supervisado comparativo de los 6 modelos del sílabo. Optimización de la red neuronal PyTorch MLP utilizando entropía cruzada binaria (BCELoss) y regularización por Dropout."),
        ("Fase IV: Inferencia Neuro-Simbólica y Generación del Dictamen: ", "Fusión de los resultados del clustering de tintas, la clasificación de enmiendas, el análisis cinemático de firmas y la búsqueda A* mediante el motor de reglas del Sistema Experto para computar el Índice de Fraude Documental Global (0 a 100 puntos).")
    ]
    for f_title, f_desc in fases:
        add_body_p(f_desc, f_title, space_after=5)

    # -------------------------------------------------------------
    # 6. BANCO DE PRUEBAS EXPERIMENTALES
    # -------------------------------------------------------------
    add_section_header("6. Casos de Estudio y Validación Experimental")
    add_body_p(
        "Para validar la robustez del sistema ante el tribunal examinador, se evaluará el agente contra cuatro escenarios de prueba tipificados:",
        None
    )

    casos = [
        ("Caso 1 (Control / Auténtico): ", "Cheque legítimo sin alteraciones con una sola formulación de tinta (Delta Hue <= 5°), firma espontánea y cifras intactas. El sistema debe certificar DOCUMENTO AUTÉNTICO (0 puntos de fraude)."),
        ("Caso 2 (Fraude por Enmienda de Cifra y Tintas): ", "Cheque alterado donde se añade un cero al monto ('$ 100' a '$ 1000') utilizando un bolígrafo de diferente marca comercial. El sistema debe detectar 2 tintas con K-Means y señalar la cifra adulterada con Gradient Boosting."),
        ("Caso 3 (Falsificación de Firma por Imitación): ", "Contrato privado con firma realizada por un tercero. El subsistema de Deep Learning y el análisis de varianza angular macro detectan ataxia motora, activando la Segunda Ley de Solange Pellat."),
        ("Caso 4 (Abuso de Firma en Blanco): ", "Documento donde la firma fue estampada antes de la impresión del texto. El algoritmo de búsqueda A* rastrea la continuidad del trazo impreso sobre la firma, revelando la superposición indebida.")
    ]
    for c_title, c_desc in casos:
        add_body_p(c_desc, c_title, space_after=4)

    # -------------------------------------------------------------
    # 7. CONSIDERACIONES ÉTICAS Y CADENA DE CUSTODIA
    # -------------------------------------------------------------
    add_section_header("7. Consideraciones Éticas e IA Responsable")
    add_body_p(
        "La aplicación de Inteligencia Artificial en el ámbito jurídico exige garantías estrictas de explicabilidad y rigor probatorio:",
        None
    )

    eticas = [
        ("Transparencia Algorítmica (XAI): ", "Se descarta el uso de modelos de 'caja negra' aislados. Cada decisión emitida por el sistema cuenta con una justificación causal basada en reglas grafotécnicas explícitas."),
        ("Cadena de Custodia Digital Inmutable: ", "El sistema calcula el Hash Criptográfico SHA-256 de cada archivo en el instante de captura, garantizando ante cualquier juzgado que la evidencia no fue manipulada en memoria."),
        ("Mitigación de Falsos Positivos: ", "La arquitectura contempla la física del sensor (resolución óptica en DPI, trepidación y ruido de digitalización), diferenciando el ruido ambiental de verdaderas alteraciones dolosas.")
    ]
    for e_title, e_desc in eticas:
        add_body_p(e_desc, e_title, space_after=4)

    # -------------------------------------------------------------
    # 8. ENTREGABLES DEL PROYECTO
    # -------------------------------------------------------------
    add_section_header("8. Entregables e Impacto Esperado")
    entregables = [
        "Servicio Web RESTful en Python (FastAPI) con módulos desacoplados para visión, aprendizaje no supervisado, aprendizaje supervisado, redes neuronales y búsqueda informada.",
        "Dashboard Web Interactivo en React y TailwindCSS con soporte para cámara web en vivo, alternancia de dispositivos y visualización gráfica de matrices de confusión, curvas ROC y gráficos de dispersión PCA.",
        "Módulo de Exportación de Dictamen Pericial Judicial formal con firma digital criptográfica.",
        "Informe Técnico Final con análisis experimental comparativo de métricas de precisión, recall, F1-Score y Silhouette Score."
    ]
    for ent in entregables:
        p_ent = doc.add_paragraph(style='List Bullet')
        p_ent.paragraph_format.space_after = Pt(4)
        p_ent.paragraph_format.line_spacing = 1.15
        r_ent = p_ent.add_run(ent)
        r_ent.font.name = "Arial"
        r_ent.font.size = Pt(10)
        r_ent.font.color.rgb = DARK_GRAY

    # Guardar documento
    doc.save(output_path)
    print(f"Documento generado exitosamente en: {output_path}")

if __name__ == "__main__":
    create_proposal_docx(r"C:\Proyecto nuevo\Propuesta_Proyecto_DocuCSI.docx")
