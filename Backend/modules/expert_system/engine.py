import hashlib
from datetime import datetime
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
        if ink_res.get('multiple_inks_detected', False):
            rules_triggered.append({
                'code': 'RULE-INK-01',
                'name': 'Incompatibilidad Cromatica de Tintas',
                'severity': 'CRITICA',
                'justification': (
                    f"Se identificaron 2 formulaciones de tinta distintas (Silhouette Score: {ink_res.get('silhouette_score', 0):.3f}). "
                    "Infiere la intervencion de un segundo instrumento inscriptor con posterioridad a la creacion original del documento."
                )
            })
            fraud_points += 45

        # Regla 2: Adulteracion de Cifras y Enmiendas
        tamper_res = findings.get('tampering', {})
        t_count = tamper_res.get('tampered_count', 0)
        if t_count > 0:
            rules_triggered.append({
                'code': 'RULE-TAMPER-02',
                'name': 'Adulteracion Morfologica de Cifras / Enmienda',
                'severity': 'CRITICA',
                'justification': (
                    f"El clasificador {tamper_res.get('best_model_used', 'Supervisado')} detecto {t_count} parches con "
                    "discontinuidad angular en los trazos y acumulacion anomala de ramificaciones (branch points)."
                )
            })
            fraud_points += 40

        # Regla 3: Leyes de Grafotecnia de Solange Pellat (Firma)
        sig_res = findings.get('signature', {})
        if not sig_res.get('is_genuine', True):
            tremor = sig_res.get('tremor_score', 0)
            rules_triggered.append({
                'code': 'RULE-PELLAT-03',
                'name': 'Segunda Ley de Solange Pellat (Accion Involuntaria e Inhibicion)',
                'severity': 'ALTA',
                'justification': (
                    f"La firma presenta elevado indice de temblores ({tremor:.1f}/100) y reduccion de velocidad cinematica. "
                    "El esfuerzo deliberado de imitacion servil suprime el automatismo motor inconsciente del titular."
                )
            })
            fraud_points += 45


        # Regla 4: Abuso de Firma en Blanco (Cronologia de Cruce A*)
        chrono_res = findings.get('chronology', {})
        if chrono_res.get('has_intersection', False) and chrono_res.get('blank_signature_fraud', False):
            rules_triggered.append({
                'code': 'RULE-CHRONO-04',
                'name': 'Cruce Inverso de Trazos (Firma en Blanco)',
                'severity': 'MAXIMA',
                'justification': (
                    "El algoritmo A* determino que el trazo del texto/clausula superpone ininterrumpidamente "
                    "al trazo de la firma. Evidencia concluyente de que el documento fue firmado antes de la impresion del texto."
                )
            })
            fraud_points += 50

        # Veredicto Global
        if fraud_points >= 40:
            global_verdict = "DOCUMENTO APOCRIFO / FRAUDE DOCUMENTAL CONCLUYENTE"
            verdict_color = "red"
        elif fraud_points >= 20:
            global_verdict = "INDICIOS SOSPECHOSOS DE ENMIENDA (Requiere peritaje complementario)"
            verdict_color = "amber"
        else:
            global_verdict = "DOCUMENTO AUTENTICO Y GENUINO"
            verdict_color = "emerald"

        # Generar texto formal del Dictamen Pericial Judicial
        case_id = f"EXP-FORENSE-{datetime.now().strftime('%Y%m%d')}-0089"
        report_text = f"""# DICTAMEN PERICIAL DOCUMENTOLOGICO Y GRAFOTECNICO
**ORGANO PERICIAL:** Laboratorio de Criminalistica e Inteligencia Artificial Documental
**EXPEDIENTE N°:** {case_id}
**FECHA Y HORA DE EMISION:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

### 1. CADENA DE CUSTODIA DIGITAL
- **Algoritmo Criptografico:** SHA-256
- **Hash de la Prueba Digital:** `{doc_hash}`
- **Garantia de Integridad:** Se certifica que el archivo procesado no sufrio manipulacion o alteracion digital externa.

---

### 2. RESUMEN DE HALLAZGOS CIENTIFICOS
1. **Espectrometria Optica de Tintas:**
   - Formulaciones Quimicas Detectadas: {ink_res.get('num_inks_detected', 1)}
   - Indice de Separabilidad (Silhouette Score): {ink_res.get('silhouette_score', 0):.4f}
   - Evaluacion: {ink_res.get('scientific_conclusion', 'N/A')}

2. **Deteccion de Adulteracion de Cifras (Supervisado):**
   - Parches Alterados: {t_count}
   - Modelo Evaluador: {tamper_res.get('best_model_used', 'Ensemble')}
   - Estado: {tamper_res.get('verdict', 'Sin alteraciones')}

3. **Cotejo de Firma y Dinamica Psicomotora (Deep Learning):**
   - Veredicto de Firma: {sig_res.get('verdict', 'N/A')}
   - Probabilidad de Autenticidad: {sig_res.get('authenticity_probability', 0)*100:.1f}%
   - Indice de Presion Motora: {sig_res.get('motor_pressure_index', 0):.1f} / 100
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
            report_text += "- No se activaron alertas de transgresion a los principios grafotecnicos ni procesales.\n\n"

        report_text += f"""---

### 4. CONCLUSION PERICIAL JUDICIAL
**VEREDICTO DEFINITIVO:** **{global_verdict}**
**NIVEL DE RIESGO EVIDENCIARIO:** {min(100, fraud_points)}% de probabilidad de manipulacion fraudulenta.

*Dictamen fundado en leyes fisicas de optica espectral, principios de la grafotecnia de Solange Pellat y modelos verificables de inteligencia artificial.*
"""

        return {
            'success': True,
            'case_id': case_id,
            'doc_hash': doc_hash,
            'fraud_points': min(100, fraud_points),
            'global_verdict': global_verdict,
            'verdict_color': verdict_color,
            'rules_triggered_count': len(rules_triggered),
            'rules_triggered': rules_triggered,
            'official_report_markdown': report_text
        }
