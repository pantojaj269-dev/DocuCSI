import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def create_archive_docx(output_path):
    doc = docx.Document()
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    NAVY = RGBColor(28, 25, 23)       # #1C1917 (Espresso/Charcoal)
    BRONZE = RGBColor(139, 94, 60)    # #8B5E3C (Bronce/Sepia)
    DARK_GRAY = RGBColor(68, 64, 60)  # #44403C

    # Encabezado
    p_pre = doc.add_paragraph()
    p_pre.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_pre = p_pre.add_run("MEMORIA TÉCNICA, BITÁCORA Y GUÍA DE SUSTENTACIÓN")
    r_pre.font.name = "Arial"
    r_pre.font.size = Pt(10)
    r_pre.font.bold = True
    r_pre.font.color.rgb = BRONZE

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(4)
    p_title.paragraph_format.space_after = Pt(6)
    r_title = p_title.add_run("DocuCSI: Bitácora Completa de Desarrollo, Preguntas del Jurado y Guía de Demostración")
    r_title.font.name = "Arial"
    r_title.font.size = Pt(17)
    r_title.font.bold = True
    r_title.font.color.rgb = NAVY

    p_line = doc.add_paragraph()
    p_line.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_line.paragraph_format.space_after = Pt(16)
    p_line.add_run("―" * 55).font.color.rgb = BRONZE

    def add_h(title):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(5)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(title)
        r.font.name = "Arial"
        r.font.size = Pt(12.5)
        r.font.bold = True
        r.font.color.rgb = NAVY
        return p

    def add_p(text, bold_prefix=None, space_after=5):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = 1.15
        if bold_prefix:
            r1 = p.add_run(bold_prefix)
            r1.font.name = "Arial"
            r1.font.size = Pt(10)
            r1.font.bold = True
            r1.font.color.rgb = NAVY
        r2 = p.add_run(text)
        r2.font.name = "Arial"
        r2.font.size = Pt(10)
        r2.font.color.rgb = DARK_GRAY
        return p

    # 1. HISTORIA Y EVOLUCIÓN DEL PROYECTO
    add_h("1. Evolución del Proyecto: De la Idea a la Suite Forense Completa")
    add_p("El proyecto comenzó con el interés de aplicar Inteligencia Artificial a la Criminalística y las Ciencias Forenses de manera viable para un estudiante universitario. Se descartaron opciones como balística o manchas de sangre por la dificultad de obtener muestras biológicas, y se seleccionó la Documentoscopía Forense y Peritaje de Firmas.", "1.1. Origen de la Propuesta: ")
    add_p("Para no limitarse a un simple clasificador de firmas, el proyecto evolucionó hacia un Agente Inteligente Multitarea (DocuCSI) que abarca todos los módulos del sílabo: Espectrometría no supervisada de tintas, detección supervisada de cifras alteradas, aprendizaje profundo en dinámica de firmas, búsqueda informada (A*) para cronología de trazos, y un sistema experto basado en reglas con cadena de custodia SHA-256.", "1.2. Alcance Integral: ")

    # 2. CONCEPTOS TÉCNICOS EXPLICADOS
    add_h("2. Conceptos Clave de Machine Learning y Criminalística (Para Estudiar)")
    
    concepts = [
        ("K-Means, PCA y Silhouette Score (Espectrometría de Tintas): ", 
         "K-Means (k=2) agrupa los píxeles de tinta en los espacios cromáticos HSV y CIELAB. PCA reduce las 9 dimensiones a 2D para graficar los clústeres. Silhouette Score mide matemáticamente qué tan separados están los pigmentos. Si dos bolígrafos son de marcas distintas (incluso si ambos son azules), su firma espectral Delta Hue difiere en más de 13°."),
        
        ("Gradient Boosting y Branch Points (Detección de Enmiendas): ", 
         "Al binarizar y adelgazar un número a su esqueleto morfológico, los cruces de líneas se llaman branch points (ramificaciones). Si alguien adultera un '100' convirtiéndolo en '1000' o repasa un trazo, genera un exceso anormal de uniones y cambios bruscos de ángulo que el modelo Gradient Boosting clasifica como alteración."),
         
        ("Segunda Ley de Solange Pellat y Red Neuronal PyTorch MLP (Firmas): ", 
         "Establece que cuando una persona firma, lo hace con automatismo motor espontáneo (rápido y fluido). Cuando alguien intenta imitar una firma ajena, dibuja con lentitud y miedo a fallar, produciendo micro-temblores (ataxia gráfica) y pérdida de velocidad. La red neuronal MLP en PyTorch detecta esta inhibición motora."),
         
        ("Algoritmo A* y el Fraude de Firma en Blanco (Cronología de Trazos): ", 
         "En el delito donde un estafador imprime texto sobre una hoja previamente firmada, la línea del texto pasa físicamente por encima del trazo de la firma. El algoritmo A* viaja por el cruce buscando la ruta de menor costo de gradiente; el trazo continuo que no sufre interrupción es el que se escribió después."),

        ("Modo Cotejo Grafotécnico Dual (Firma vs. Firma en la Misma Hoja): ",
         "Permite colocar en una sola hoja la firma original (indubitada) a la izquierda y la imitación (dubitada) a la derecha. El sistema segmenta ambas mitades, calcula la similitud morfológica y contrasta la velocidad y temblores, emitiendo un veredicto comparativo.")
    ]
    for c_title, c_desc in concepts:
        add_p(c_desc, c_title, space_after=4)

    # 3. LECCIÓN EXPERIMENTAL: CÁMARA WEB VS. FOTO DE CELULAR
    add_h("3. La Lección de Percepción: Cámara Web vs. Foto de Celular")
    add_p("Durante las pruebas en vivo, se observó que una foto de celular activaba 2 reglas mientras que la cámara web de la laptop activaba 4 reglas en el mismo documento.", "3.1. Hallazgo Experimental: ")
    add_p("Esto se debe a la resolución óptica y la física del sensor (Signal-to-Noise Ratio): la cámara del celular (12-48 MP) entrega bordes nítidos y sin movimiento. La cámara de la laptop (0.9 MP a 720p) genera escalonamiento digital (píxeles en sierra) y desenfoque; los modelos matemáticos interpretan ese serrucho de píxeles como temblores de mano (ataxia). En criminalística real (Norma ISO/IEC 17025), se exige un escaneo mínimo de resolución para evitar falsos positivos por ruido del sensor.", "3.2. Justificación de Ingeniería: ")

    # 4. GUÍA PARA LA DEMOSTRACIÓN EN VIVO
    add_h("4. Guía Rápida para la Demostración ante el Profesor")
    add_p("1. Abre la web en http://localhost:5173 (con la nueva paleta beige minimalista).")
    add_p("2. Demostración Rápida (Plan A): Haz clic en los botones superiores ('Cheque Legítimo', 'Cheque Adulterado', 'Firma Falsificada', 'Firma en Blanco'). En 1 segundo cada caso se procesará con resultados perfectos.")
    add_p("3. Demostración en Vivo de Tintas (Plan B): Muestra la foto de tu cuaderno donde escribiste con 1 lapicero (homogéneo) vs. con 2 lapiceros de diferente marca (alerta de 2 tintas).")
    add_p("4. Demostración del Cotejo Dual de Firmas (Plan C): Ve a la pestaña 4, activa 'Modo Cotejo Dual', sube la hoja con tu firma y la imitación de tu amigo, y muestra la comparativa lado a lado con las cajas verde y roja.")

    # 5. PREGUNTAS CLAVE DEL PROFESOR Y CÓMO RESPONDERLAS
    add_h("5. Preguntas Difíciles del Jurado / Profesor y Respuestas de Alto Nivel")

    qa = [
        ("Pregunta 1: ¿Por qué usaron K-Means y no solo una comparación de color RGB?",
         "Respuesta: 'Profesor, el espacio RGB es dependiente de la iluminación y las sombras. Usamos el espacio LAB y HSV porque separan la luminancia de la crominancia. Con K-Means y PCA analizamos la firma espectral química (Delta Hue), permitiendo distinguir dos marcas de bolígrafos aunque al ojo humano ambas se vean azules.'"),

        ("Pregunta 2: ¿Por qué usaron A* para el cruce y no una simple red convolucional?",
         "Respuesta: 'A* aporta explicabilidad causal física. En un juicio, una red neuronal opaca puede ser desestimada como caja negra. A* modela la densidad de tinta como un grafo de costos y demuestra formalmente qué trazo tiene continuidad ininterrumpida.'"),

        ("Pregunta 3: ¿Cómo garantizan que la evidencia no fue manipulada en el software?",
         "Respuesta: 'Implementamos Cadena de Custodia Digital mediante Hashing Criptográfico SHA-256. En el milisegundo exacto en que la cámara o el archivo entran a la memoria, se genera su huella digital criptográfica inmutable, la cual queda sellada en el acta judicial.'")
    ]
    for q, a in qa:
        add_p(q, None, space_after=2)
        add_p(a, None, space_after=6)

    doc.save(output_path)
    print(f"Archivo guardado exitosamente en: {output_path}")

if __name__ == "__main__":
    create_archive_docx(r"C:\Proyecto nuevo\Memoria_Completa_y_Guia_Sustentacion.docx")
