import hashlib
from datetime import datetime, timezone
from uuid import uuid4
from typing import Dict, Any, List

class ForensicExpertSystem:
    """
    Sistema Experto Basado en Reglas y Motor de Inferencia Judicial:
    - Base de conocimiento con las Leyes de la Grafotecnia (Solange Pellat) y Protocolo Procesal Forense.
    - Motor de inferencia hacia adelante (Forward Chaining) con explicabilidad causal.
    - Cadena de custodia digital con Hash criptografico SHA-256.
    """

    @staticmethod
    def calculate_sha256(image_bytes: bytes) -> str:
        return hashlib.sha256(image_bytes).hexdigest()

    @classmethod
    def evaluate(cls, findings: Dict[str, Any], doc_bytes: bytes = b'') -> Dict[str, Any]:
        rules_triggered = []
        fraud_points = 0
        doc_hash = cls.calculate_sha256(doc_bytes) if doc_bytes else "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

        # Regla 1: Adulteracion Cromatica de Tintas
        ink_res = findings.get('inks', {})
        mixed_neutral = ink_res.get('mixed_colored_neutral', False)
        chromatic_multiple = ink_res.get('chromatic_multiple_detected', ink_res.get('multiple_inks_detected', False) and not mixed_neutral)
        if chromatic_multiple:
            rules_triggered.append({
                'code': 'RULE-INK-01',
                'name': 'Diferencia de color que requiere revisión contextual',
                'severity': 'OBSERVACION',
                'justification': (
                    f"Se identificaron grupos cromáticos separados (Silhouette: {ink_res.get('silhouette_score', 0):.3f}). "
                    "Puede haber varios colores legítimos. No determina composición, adulteración ni orden de escritura."
                )
            })
            fraud_points += 15

        if mixed_neutral:
            rules_triggered.append({
                'code': 'OBS-NEUTRAL-01',
                'name': 'Mezcla de trazos de color y negros/grises',
                'severity': 'CONTEXTO',
                'justification': (
                    'Hay evidencia visible de trazos neutros además del color. Puede corresponder a lápiz, '
                    'bolígrafo negro o impresión. No se elimina por asumir que es un formulario; '
                    'se requiere revisar el contexto y no se certifica legitimidad.'
                ),
            })

        # Regla 2: Adulteracion de Cifras y Enmiendas
        tamper_res = findings.get('tampering', {})
        t_count = tamper_res.get('tampered_count', 0)
        if t_count > 0:
            rules_triggered.append({
                'code': 'RULE-TAMPER-02',
                'name': 'Señal morfológica del clasificador ilustrativo',
                'severity': 'REVISION',
                'justification': (
                    f"El clasificador {tamper_res.get('best_model_used', 'Supervisado')} detecto {t_count} parches con "
                    "rasgos morfológicos atípicos según su entrenamiento sintético. No es una probabilidad calibrada ni acredita adulteración."
                )
            })
            fraud_points += 40

        # Regla 3: Leyes de Grafotecnia de Solange Pellat (Firma)
        sig_res = findings.get('signature', {})
        if sig_res.get('anomaly_detected', False):
            tremor = sig_res.get('tremor_score', 0)
            rules_triggered.append({
                'code': 'RULE-PELLAT-03',
                'name': 'Irregularidad morfológica del trazo: requiere cotejo',
                'severity': 'ALTA',
                'justification': (
                    f"Se observó rugosidad a varias escalas (índice {tremor:.1f}/100). "
                    "Se necesita referencia y evaluación de calidad; no acredita falsificación ni velocidad real."
                )
            })
            fraud_points += 45


        # Regla 4: Abuso de Firma en Blanco (Cronologia de Cruce A*)
        chrono_res = findings.get('chronology', {})
        if chrono_res.get('has_intersection', False) and chrono_res.get('requires_review', False):
            rules_triggered.append({
                'code': 'RULE-CHRONO-04',
                'name': 'Cruce visible de trazos: orden no concluyente',
                'severity': 'REVISION',
                'justification': (
                    "Se detectó una intersección entre línea y escritura de color. A* explora su conectividad. "
                    "Los costos no prueban la secuencia física de las tintas ni confirman firma en blanco."
                )
            })
            fraud_points += 25

        # Veredicto Global
        if fraud_points >= 40:
            global_verdict = "INDICIOS DE POSIBLE MANIPULACION DOCUMENTAL"
            verdict_color = "red"
        elif fraud_points >= 20:
            global_verdict = "OBSERVACIONES QUE REQUIEREN REVISION COMPLEMENTARIA"
            verdict_color = "amber"
        else:
            global_verdict = "SIN DIFERENCIA RESUELTA: LEGITIMIDAD NO DETERMINADA" if not rules_triggered else "MEZCLA O DIFERENCIAS VISUALES: REQUIERE CONTEXTO"
            verdict_color = "amber"

        limitations = [
            'Una fotografía no certifica legitimidad o fraude ni identifica con certeza grafito, tinta o impresión.',
            'Las diferencias no resueltas pueden quedar por debajo del contraste o resolución de esta captura.',
            'El clasificador de formas se entrenó con datos sintéticos; sus métricas no son validación de documentos reales.',
        ]
        quality = findings.get('quality', {})
        limitations.extend(quality.get('warnings', []))
        if not ink_res.get('success', False):
            limitations.append('El análisis de trazos no contó con evidencia suficiente.')
        if sig_res.get('morphology_status') == 'inconclusive':
            limitations.append('La región de posible firma no pudo evaluarse de forma concluyente.')
        if tamper_res.get('evidence_status') == 'not_evaluable':
            limitations.append('No se localizaron caracteres compatibles con el clasificador de formas.')

        # Generar texto formal del Dictamen Pericial Judicial
        issued_at = datetime.now(timezone.utc)
        case_id = f"EXP-FORENSE-{issued_at.strftime('%Y%m%d')}-{uuid4().hex[:8].upper()}"
        report_text = f"""# DICTAMEN PERICIAL DOCUMENTOLOGICO Y GRAFOTECNICO
**ALCANCE:** Prototipo academico con entrenamiento sintetico y heuristicas de imagen. No constituye un dictamen judicial ni acredita autenticidad, composicion quimica o secuencia fisica de trazos.
**ORGANO PERICIAL:** Laboratorio de Criminalistica e Inteligencia Artificial Documental
**EXPEDIENTE N°:** {case_id}
**FECHA Y HORA DE EMISION:** {issued_at.strftime('%Y-%m-%d %H:%M:%S UTC')}

---

### 1. CADENA DE CUSTODIA DIGITAL
- **Algoritmo Criptografico:** SHA-256
- **Hash de la Prueba Digital:** `{doc_hash}`
- **Identificacion del archivo recibido:** El hash corresponde a los bytes originales enviados, antes de rectificacion y redimensionamiento. Permite comparar integridad entre copias; no certifica su procedencia ni ausencia de alteraciones previas.

---

### 2. RESUMEN DE HALLAZGOS CIENTIFICOS
1. **Espectrometria Optica de Tintas:**
   - Grupos de Color Reportados: {ink_res.get('num_inks_detected', 1)}
   - Indice de Separabilidad (Silhouette Score): {ink_res.get('silhouette_score', 0):.4f}
   - Evaluacion: {ink_res.get('scientific_conclusion', 'N/A')}

2. **Deteccion de Adulteracion de Cifras (Supervisado):**
   - Parches Alterados: {t_count}
   - Modelo Evaluador: {tamper_res.get('best_model_used', 'Ensemble')}
   - Estado: {tamper_res.get('verdict', 'Sin alteraciones')}

3. **Morfología de Firma (heurística multiescala):**
   - Veredicto de Firma: {sig_res.get('verdict', 'N/A')}
   - Autenticidad: No estimable sin referencia y validación con datos reales.
   - Presión y velocidad físicas: No medibles con esta fotografía estática.
   - Indice de Temblores (Ataxia Grafica): {sig_res.get('tremor_score', 0):.1f} / 100

4. **Cronologia de Trazos Cruzados (Algoritmo A*):**
   - Trazo Superior Físico: {chrono_res.get('top_stroke', 'N/A')}
   - Veredicto de Secuencia: {chrono_res.get('chronology_verdict', 'N/A')}

---

### 3. REGLAS JURIDICO-FORENSES APLICADAS
"""
        if rules_triggered:
            for r in rules_triggered:
                report_text += f"- **[{r['code']}] {r['name']}** ({r['severity']}):\n  {r['justification']}\n\n"
        else:
            report_text += "- No se activaron los criterios del prototipo. Esto no acredita legitimidad ni ausencia de modificaciones.\n\n"

        report_text += '### LIMITES DE LA EVALUACION\n' + '\n'.join('- ' + item for item in limitations) + '\n\n'

        report_text += f"""---

### 4. CONCLUSION PERICIAL JUDICIAL
**RESULTADO ORIENTATIVO:** **{global_verdict}**
**PUNTUACION DE REGLAS:** {min(100, fraud_points)} / 100. No representa una probabilidad estadistica calibrada.

*Dictamen fundado en leyes fisicas de optica espectral, principios de la grafotecnia de Solange Pellat y modelos verificables de inteligencia artificial.*
"""

        return {
            'success': True,
            'case_id': case_id,
            'doc_hash': doc_hash,
            'fraud_points': min(100, fraud_points),
            'global_verdict': global_verdict,
            'verdict_color': verdict_color,
            'authenticity_determined': False,
            'limitations': limitations,
            'assessment_status': 'requires_context' if rules_triggered else 'limited_no_signal',
            'rules_triggered_count': len(rules_triggered),
            'rules_triggered': rules_triggered,
            'official_report_markdown': report_text
        }
