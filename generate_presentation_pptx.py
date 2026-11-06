import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

def create_presentation_with_images():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # Color Palette
    BG_LIGHT = RGBColor(248, 246, 240)      # Lab Cream
    DARK_NAVY = RGBColor(30, 41, 59)        # Slate Navy
    ACCENT_RED = RGBColor(185, 28, 28)      # Crimson Forensics
    ACCENT_BLUE = RGBColor(2, 132, 199)     # Deep Tech Blue
    CARD_BG = RGBColor(255, 255, 255)       # Pure White
    TEXT_MAIN = RGBColor(51, 65, 85)        # Slate Dark
    BORDER_COLOR = RGBColor(226, 232, 240)  # Subtle Border
    EMERALD = RGBColor(5, 150, 105)

    blank_layout = prs.slide_layouts[6]

    def set_slide_bg(slide, color=BG_LIGHT):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
        bg.fill.solid()
        bg.fill.fore_color.rgb = color
        bg.line.fill.background()
        return bg

    def add_header(slide, category, title):
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.3))
        tf_cat = cat_box.text_frame
        tf_cat.word_wrap = True
        tf_cat.margin_left = tf_cat.margin_right = tf_cat.margin_top = tf_cat.margin_bottom = 0
        p_cat = tf_cat.paragraphs[0]
        p_cat.text = category.upper()
        p_cat.font.name = "Arial"
        p_cat.font.size = Pt(11)
        p_cat.font.bold = True
        p_cat.font.color.rgb = ACCENT_RED

        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(11.7), Inches(0.6))
        tf_title = title_box.text_frame
        tf_title.word_wrap = True
        tf_title.margin_left = tf_title.margin_right = tf_title.margin_top = tf_title.margin_bottom = 0
        p_title = tf_title.paragraphs[0]
        p_title.text = title
        p_title.font.name = "Arial"
        p_title.font.size = Pt(24)
        p_title.font.bold = True
        p_title.font.color.rgb = DARK_NAVY

    def add_notes(slide, notes_text):
        notes_slide = slide.notes_slide
        text_frame = notes_slide.notes_text_frame
        text_frame.text = notes_text

    def add_card(slide, left, top, width, height, title, items, badge="", badge_color=ACCENT_BLUE):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = BORDER_COLOR
        card.line.width = Pt(1.5)

        tb = slide.shapes.add_textbox(left + Inches(0.25), top + Inches(0.2), width - Inches(0.5), height - Inches(0.4))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0

        p0 = tf.paragraphs[0]
        if badge:
            p0.text = f"[{badge}] {title}"
        else:
            p0.text = title
        p0.font.name = "Arial"
        p0.font.size = Pt(15)
        p0.font.bold = True
        p0.font.color.rgb = DARK_NAVY
        p0.space_after = Pt(10)

        for item in items:
            p = tf.add_paragraph()
            p.text = f"• {item}"
            p.font.name = "Arial"
            p.font.size = Pt(12)
            p.font.color.rgb = TEXT_MAIN
            p.space_after = Pt(6)

    # =============================================================
    # DIAPOSITIVA 1: PORTADA & PROPÓSITO
    # =============================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s1, DARK_NAVY)

    bar = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(0.12))
    bar.fill.solid()
    bar.fill.fore_color.rgb = ACCENT_RED
    bar.line.fill.background()

    t_box = s1.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(11.3), Inches(3.8))
    tf1 = t_box.text_frame
    tf1.word_wrap = True

    p = tf1.paragraphs[0]
    p.text = "PROYECTO DE INTELIGENCIA ARTIFICIAL"
    p.font.name = "Arial"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE
    p.space_after = Pt(14)

    p = tf1.add_paragraph()
    p.text = "DocuCSI: Suite de Peritaje Documental Forense"
    p.font.name = "Arial"
    p.font.size = Pt(36)
    p.font.bold = True
    p.font.color.rgb = RGBColor(255, 255, 255)
    p.space_after = Pt(18)

    p = tf1.add_paragraph()
    p.text = "Sistema automatizado para la detección de fraude, enmiendas en cheques, falsificación de firmas y manipulación de documentos mediante Visión Artificial y Machine Learning."
    p.font.name = "Arial"
    p.font.size = Pt(15)
    p.font.color.rgb = RGBColor(203, 213, 225)
    p.space_after = Pt(24)

    p = tf1.add_paragraph()
    p.text = "Stack: Python (FastAPI + PyTorch) | React 19 + Vite | OpenCV | Scikit-Learn | SHA-256"
    p.font.name = "Arial"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = ACCENT_RED

    add_notes(s1,
        "GUION BREVE (Diapositiva 1):\n"
        "\"Buenas tardes. DocuCSI es una plataforma que automatiza el peritaje criminalístico de documentos. Su objetivo es determinar de forma matemática y objetiva si un cheque, contrato o pagaré fue alterado, analizando tintas, cifras y firmas en menos de 2 segundos.\""
    )

    # =============================================================
    # DIAPOSITIVA 2: ALCANCE DEL SISTEMA (CON MUESTRA FORENSE REAL)
    # =============================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s2)
    add_header(s2, "Alcance del Proyecto", "¿Qué analiza y qué problemas resuelve el sistema?")

    add_card(s2, Inches(0.8), Inches(1.5), Inches(6.2), Inches(5.4),
        "4 Tipos de Fraude Detectados", [
        "1. Espectrometría de Tintas (No Supervisado): Identifica si se usaron bolígrafos de diferente fórmula química para adulterar textos (K-Means y PCA en espacio HSV/LAB).",
        "2. Cifras Numéricas Adulteradas (Supervisado): Detecta enmiendas o ceros agregados en casillas de montos bancarios mediante Gradient Boosting y Random Forest.",
        "3. Biomecánica de Firmas (Deep Learning): Detecta inhibición motora, lentitud y micro-temblores involuntarios por imitación servil (Segunda Ley de Solange Pellat).",
        "4. Cronología de Trazos Cruzados (Búsqueda A*): Resuelve qué trazo está físicamente superpuesto al otro, revelando el delito de 'Firma en Blanco'.",
        "Resultado: Dictamen pericial formal con porcentaje de sospecha y Hash SHA-256."
    ], badge="FUNCIONALIDADES")

    # Image Card on the Right
    sample_path = "C:/Proyecto nuevo/Backend/data/samples/check_altered.png"
    if os.path.exists(sample_path):
        card_img = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.3), Inches(1.5), Inches(5.2), Inches(5.4))
        card_img.fill.solid()
        card_img.fill.fore_color.rgb = CARD_BG
        card_img.line.color.rgb = BORDER_COLOR
        card_img.line.width = Pt(1.5)

        # Title for Image
        tb_img = s2.shapes.add_textbox(Inches(7.5), Inches(1.7), Inches(4.8), Inches(0.5))
        p_img = tb_img.text_frame.paragraphs[0]
        p_img.text = "EVIDENCIA FORENSE: CHEQUE ADULTERADO"
        p_img.font.name = "Arial"
        p_img.font.size = Pt(12)
        p_img.font.bold = True
        p_img.font.color.rgb = ACCENT_RED

        s2.shapes.add_picture(sample_path, Inches(7.5), Inches(2.3), width=Inches(4.8))

        tb_desc = s2.shapes.add_textbox(Inches(7.5), Inches(5.8), Inches(4.8), Inches(0.9))
        p_desc = tb_desc.text_frame.paragraphs[0]
        p_desc.text = "Muestra real analizada: Se modificó la cifra de $100 a $1000 con un bolígrafo secundario. El sistema aísla la segunda tinta y la alteración morfológica."
        p_desc.font.name = "Arial"
        p_desc.font.size = Pt(10)
        p_desc.font.color.rgb = TEXT_MAIN

    add_notes(s2,
        "GUION BREVE (Diapositiva 2):\n"
        "\"El alcance del sistema cubre cuatro tipos de fraude: espectrometría para detectar bolígrafos diferentes, clasificación de cifras alteradas en cheques como vemos en la imagen de la derecha donde un 100 fue convertido en 1000, análisis biomecánico de firmas falsificadas con PyTorch, y resolución cronológica de trazos superpuestos con el algoritmo A*.\""
    )

    # =============================================================
    # DIAPOSITIVA 3: ARQUITECTURA DEL SISTEMA (CON DIAGRAMA)
    # =============================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s3)
    add_header(s3, "Arquitectura de Software", "Flujo Cliente-Servidor y Pipeline Analítico")

    # Top summary card
    add_card(s3, Inches(0.8), Inches(1.5), Inches(11.7), Inches(1.6),
        "Estructura Desacoplada en 3 Capas", [
        "Capa de Presentación: Frontend en React 19 con captura WebRTC y envío en Base64.",
        "Capa de Servicios: API REST asíncrona en FastAPI con sellado de integridad SHA-256.",
        "Capa Analítica: Pipeline secuencial de Visión, Machine Learning, Deep Learning y Búsqueda Heurística A*."
    ], badge="PATRÓN ARQUITECTÓNICO")

    # Architecture Diagram Image
    diag_path = "C:/Proyecto nuevo/presentation_assets/architecture_diagram.png"
    if os.path.exists(diag_path):
        s3.shapes.add_picture(diag_path, Inches(0.8), Inches(3.3), width=Inches(11.7))

    add_notes(s3,
        "GUION BREVE (Diapositiva 3):\n"
        "\"La arquitectura es cliente-servidor desacoplada. El frontend en React captura el documento y lo transmite en Base64 al backend en FastAPI. El servidor sella la imagen con un Hash SHA-256 inmutable y la procesa a través de nuestro pipeline de visión, machine learning y deep learning, devolviendo el dictamen judicial al instante.\""
    )

    # =============================================================
    # DIAPOSITIVA 4: LENGUAJES Y ENTORNO DE EJECUCIÓN (CON DIAGRAMA)
    # =============================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s4)
    add_header(s4, "Ingeniería del Sistema", "¿En qué lenguaje se hizo y en dónde se ejecuta?")

    add_card(s4, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.4),
        "Lenguajes de Programación", [
        "Python 3.12+ (Backend & Modelos IA):",
        "  - Empleado para todo el procesamiento matricial, tensores, visión artificial y clasificadores.",
        "  - Soporte maduro para librerías científicas (PyTorch, Scikit-Learn, OpenCV).",
        "JavaScript / TypeScript ES6+ (Frontend):",
        "  - Interfaz web interactiva en el navegador.",
        "  - Manejo de streaming de video en vivo (WebRTC) y renderizado gráfico en Canvas.",
        "Requisitos de Hardware:",
        "  - Laptop o PC estándar, 4 GB de RAM y cámara web integrada (720p o superior)."
    ], badge="LENGUAJES")

    # Deployment Diagram Image on the Right
    dep_path = "C:/Proyecto nuevo/presentation_assets/deployment_diagram.png"
    if os.path.exists(dep_path):
        s4.shapes.add_picture(dep_path, Inches(6.7), Inches(1.5), width=Inches(5.8))

    add_notes(s4,
        "GUION BREVE (Diapositiva 4):\n"
        "\"Respecto a los lenguajes: usamos Python 3.12 en el backend por su potencia en tensores e IA, y JavaScript con React en el frontend. Como se observa a la derecha, el sistema corre de forma local sin internet en una laptop pericial con un script .bat, o en la nube mediante contenedores Docker para juzgados.\""
    )

    # =============================================================
    # DIAPOSITIVA 5: LIBRERÍAS Y FRAMEWORKS (CON GRAPHIC STACK)
    # =============================================================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s5)
    add_header(s5, "Stack Tecnológico", "Librerías y Frameworks Utilizados")

    add_card(s5, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.4),
        "Resumen de Librerías Principales", [
        "FastAPI & Uvicorn: API REST asíncrona de ultrabaja latencia y tipado estricto con Pydantic.",
        "OpenCV: Homografía de perspectiva, binarización Otsu y esqueletización Zhang-Suen a 1 píxel.",
        "PyTorch (torch): Red Neuronal Densa (MLP) con regularización Dropout para biomecánica de firmas.",
        "Scikit-Learn: K-Means / PCA (tintas) y Gradient Boosting / Random Forest (cifras adulteradas).",
        "React 19 & Vite: Frontend SPA reactivo de carga y renderizado instantáneo.",
        "Tailwind CSS 4: Estilos utilitarios y diseño ergonómico de laboratorio forense."
    ], badge="LIBRERÍAS")

    # Tech Stack Graphic on the Right
    tech_path = "C:/Proyecto nuevo/presentation_assets/tech_stack.png"
    if os.path.exists(tech_path):
        s5.shapes.add_picture(tech_path, Inches(6.7), Inches(1.5), width=Inches(5.8))

    add_notes(s5,
        "GUION BREVE (Diapositiva 5):\n"
        "\"En cuanto a librerías: en el backend empleamos FastAPI para la API, OpenCV para la visión, PyTorch para la red neuronal profunda de firmas, y Scikit-Learn para las tintas y enmiendas. En el frontend usamos React 19, Tailwind CSS y WebRTC para la cámara en vivo. Con este stack logramos una herramienta rápida, ligera y precisa.\""
    )

    # =============================================================
    # DIAPOSITIVA 6: CONCLUSIONES & CIERRE (NUEVA DIAPOSITIVA)
    # =============================================================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s6)
    add_header(s6, "Conclusiones & Cierre", "Impacto, Viabilidad Técnica y Validez Jurídica")

    add_card(s6, Inches(0.8), Inches(1.5), Inches(6.8), Inches(5.4),
        "Conclusiones del Proyecto", [
        "1. Automatización Objetiva y Rápida: Se sustituye la apreciación subjetiva de la lupa por métricas matemáticas cuantitativas en menos de 2 segundos.",
        "2. Paradigma Neuro-Simbólico Explicable: La unión de Redes Neuronales (percepción motora) con Sistemas Expertos (Leyes de Pellat) elimina el problema de la 'caja negra' en tribunales.",
        "3. Solución Integral al Delito de Firma en Blanco: El algoritmo A* resuelve formalmente la cronología de superposición de trazos con rigor matemático.",
        "4. Alta Disponibilidad y Despliegue Flexible: Funciona de forma autónoma offline en estaciones periciales o centralizado en la nube mediante Docker.",
        "5. Garantía de Integridad: Preservación de la evidencia digital bajo normas forenses mediante sellado criptográfico SHA-256."
    ], badge="CONCLUSIONES", badge_color=EMERALD)

    # Seal Image on the Right
    seal_path = "C:/Proyecto nuevo/presentation_assets/conclusion_seal.png"
    if os.path.exists(seal_path):
        s6.shapes.add_picture(seal_path, Inches(7.9), Inches(1.8), width=Inches(4.6))

    add_notes(s6,
        "GUION BREVE (Diapositiva 6):\n"
        "\"Para concluir: DocuCSI demuestra cómo la Inteligencia Artificial puede transformar la criminalística documental. Al combinar redes neuronales con sistemas expertos explicables y cadena de custodia SHA-256, garantizamos no solo precisión técnica, sino plena validez probatoria en tribunales. Muchas gracias por su atención.\""
    )

    output_path = "C:/Proyecto nuevo/Presentacion_DocuCSI_Final.pptx"
    prs.save(output_path)
    print(f"Presentation saved successfully to: {output_path}")

    # Also attempt to overwrite Breve if not locked
    try:
        prs.save("C:/Proyecto nuevo/Presentacion_DocuCSI_Breve.pptx")
        print("Also updated Presentacion_DocuCSI_Breve.pptx")
    except Exception as e:
        print(f"Note on Breve: {e}")

if __name__ == "__main__":
    create_presentation_with_images()
