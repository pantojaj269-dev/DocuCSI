"""Casos geométricos independientes de los PNG de presentación.

Prueban regresiones y alcance de las conclusiones, no precisión forense real.
"""
from pathlib import Path
import unittest
import cv2
import numpy as np
import main
from modules.vision.processor import DocumentProcessor as Processor
from modules.inks.analyzer import InkAnalyzer
from modules.chronology.a_star import ChronologyAnalyzer
from modules.expert_system.engine import ForensicExpertSystem


def measure(image):
    mask, _ = Processor.extract_ink_mask(image)
    return mask


def line_scene(angle=0, crossing=True, reverse_order=False, scale=1):
    image = np.full((400, 800, 3), 250, np.uint8)
    xs = np.arange(410, 701)
    ys = 270 + 45*np.sin((xs-410)/38)
    if not crossing:
        ys -= 100
    stroke = np.column_stack((xs, ys)).astype(np.int32)
    a, b = (120, 270), (730, 270+int(610*np.tan(np.deg2rad(angle))))
    if reverse_order:
        cv2.line(image, a, b, (25,25,25), 5, cv2.LINE_AA)
    cv2.polylines(image, [stroke], False, (160,40,20), 4, cv2.LINE_AA)
    if not reverse_order:
        cv2.line(image, a, b, (25,25,25), 5, cv2.LINE_AA)
    if scale != 1:
        image = cv2.resize(image, None, fx=scale, fy=scale)
    return image


class VisualEvidenceTests(unittest.TestCase):
    def test_gray_print_and_blue_writing_are_not_two_colored_pens(self):
        for gray in [30, 80, 140, 185]:
            with self.subTest(gray=gray):
                image = np.full((300,600,3), 248, np.uint8)
                cv2.putText(image, 'FORMULARIO', (20,60), cv2.FONT_HERSHEY_SIMPLEX, 1, (gray,gray,gray), 2)
                cv2.putText(image, 'Datos a mano', (40,180), cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, 1.5, (140,35,20), 3)
                result = InkAnalyzer.analyze(image, measure(image))
                self.assertFalse(result['multiple_inks_detected'])

    def test_blue_pressure_variation_is_not_a_second_chemical_ink(self):
        image = np.full((300,600,3), 250, np.uint8)
        for y,color in [(80,(130,30,15)),(160,(210,110,90))]:
            cv2.putText(image, 'Misma tinta', (20,y), cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, 1.4, color, 3)
        result = InkAnalyzer.analyze(image, measure(image))
        self.assertFalse(result['multiple_inks_detected'])

    def test_red_and_blue_are_detected_as_distinct_colors(self):
        image = np.full((300,600,3), 250, np.uint8)
        for y,color in [(80,(140,35,20)),(180,(20,25,200))]:
            cv2.putText(image, 'Texto manuscrito', (20,y), cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, 1.2, color, 3)
        self.assertTrue(InkAnalyzer.analyze(image, measure(image))['multiple_inks_detected'])

    def test_gray_levels_do_not_prove_chemical_difference(self):
        image = np.full((300,600,3), 250, np.uint8)
        for y,gray in [(80,20),(180,120)]:
            cv2.putText(image, 'Texto', (20,y), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (gray,gray,gray), 3)
        self.assertFalse(InkAnalyzer.analyze(image, measure(image))['multiple_inks_detected'])

    def test_crossings_survive_small_slopes_scale_and_reversed_layers(self):
        for angle in [-4,0,4]:
            for scale in [.75,1,1.4]:
                for reverse in [False, True]:
                    with self.subTest(angle=angle,scale=scale,reverse=reverse):
                        image = line_scene(angle=angle,scale=scale,reverse_order=reverse)
                        result = ChronologyAnalyzer.analyze_intersection(image, measure(image))
                        self.assertTrue(result['has_intersection'])
                        self.assertIsNone(result['blank_signature_fraud'])
                        self.assertIsNone(result['is_signature_top'])
                        self.assertEqual(result['chronology_status'], 'inconclusive')

    def test_separated_signature_and_line_are_not_a_crossing(self):
        image = line_scene(crossing=False)
        result = ChronologyAnalyzer.analyze_intersection(image, measure(image))
        self.assertFalse(result['has_intersection'])
        self.assertEqual(result['nodes_explored_a_star'], 0)

    def test_line_alone_is_not_a_signature_crossing(self):
        image = np.full((400,800,3), 250, np.uint8)
        cv2.line(image, (80,270), (730,280), (20,20,20), 5)
        result = ChronologyAnalyzer.analyze_intersection(image, measure(image))
        self.assertFalse(result['has_intersection'])
        self.assertIsNone(result['horizontal_path_cost'])

    def test_unresolved_same_color_crossing_does_not_claim_a_sequence(self):
        image = line_scene()
        image[measure(image)>0] = (20,20,20)
        result = ChronologyAnalyzer.analyze_intersection(image, measure(image))
        self.assertIsNone(result['blank_signature_fraud'])
        self.assertIsNone(result['is_signature_top'])

    def test_signature_without_reference_never_claims_authorship(self):
        for scale in [.8,1,1.5]:
            image = np.full((400,800,3), 250, np.uint8)
            cv2.putText(image, 'M Flores', (400,310), cv2.FONT_HERSHEY_SCRIPT_COMPLEX, 1.5, (140,35,20), 2, cv2.LINE_AA)
            image = cv2.resize(image,None,fx=scale,fy=scale)
            result = main.signature_verifier.verify(image, measure(image))
            self.assertIsNone(result['is_genuine'])
            self.assertIsNone(result['authenticity_probability'])
            self.assertIsNone(result['motor_pressure_index'])
            self.assertFalse(result['anomaly_detected'])

    def test_missing_signature_is_inconclusive(self):
        image = np.full((400,800,3), 250, np.uint8)
        result = main.signature_verifier.verify(image, measure(image))
        self.assertEqual(result['morphology_status'], 'inconclusive')
        self.assertFalse(result['anomaly_detected'])

    def test_warm_low_saturation_paper_is_not_a_face(self):
        image = np.full((400,800,3), (220,230,239), np.uint8)
        cv2.putText(image, 'Documento escrito en papel', (40,180), cv2.FONT_HERSHEY_SIMPLEX, 1, (140,35,20), 3)
        valid, _, details = Processor.validate_document(image)
        self.assertTrue(valid, details)

    def test_color_difference_alone_is_not_a_fraud_verdict(self):
        report = ForensicExpertSystem.evaluate({'inks': {'multiple_inks_detected': True}})
        self.assertEqual(report['fraud_points'], 15)
        self.assertEqual(report['verdict_color'], 'amber')
        self.assertNotIn('MANIPULACION', report['global_verdict'])

    def test_absent_evidence_is_not_replaced_by_legacy_boolean(self):
        report = ForensicExpertSystem.evaluate({'signature': {'is_genuine': False}, 'chronology': {'blank_signature_fraud':True}})
        self.assertEqual(report['fraud_points'], 0)

    def test_presentation_photos_with_capture_perturbations(self):
        folder = Path(main.__file__).parents[1] / 'Cheques_para_presentacion/Estilo_lapicero'
        if not folder.exists():
            self.skipTest('Imágenes generadas de uso local; no son fixtures de producción')
        for path in sorted(folder.glob('*.png')):
            for scale,contrast in [(1,1),(.8,.9),(1.1,1.05)]:
                with self.subTest(file=path.name,scale=scale,contrast=contrast):
                    image = cv2.imread(str(path))
                    image = cv2.resize(image,None,fx=scale,fy=scale)
                    image = np.clip(image.astype(np.float32)*contrast,0,255).astype(np.uint8)
                    image = Processor.prepare_for_analysis(image)
                    image,_ = Processor.rectify_perspective(image)
                    mask = measure(image)
                    inks = InkAnalyzer.analyze(image,mask)
                    signature = main.signature_verifier.verify(image,mask)
                    chronology = ChronologyAnalyzer.analyze_intersection(image,mask)
                    signature = main.signature_verifier.account_for_overlap(signature, chronology, image.shape)
                    self.assertEqual(inks['multiple_inks_detected'],path.name.startswith('02'))
                    self.assertEqual(signature['anomaly_detected'],path.name.startswith('03'))
                    self.assertEqual(chronology['has_intersection'],path.name.startswith('04'))


if __name__ == '__main__':
    unittest.main()
