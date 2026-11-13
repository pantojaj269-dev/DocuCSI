"""Regresiones para mezcla azul + negro/gris, incluido lápiz tenue.

Estas geometrías controlan color, grosor y captura; no representan una
validación de identificación química de materiales reales.
"""
import base64
from pathlib import Path
import struct
import zlib
import unittest
from unittest.mock import patch
import cv2
import numpy as np
from fastapi.testclient import TestClient
import main
from modules.vision.processor import DocumentProcessor as Processor
from modules.inks.analyzer import InkAnalyzer


def material_scene(neutral_gray=150, thickness=1, paper=(250,250,250), shade=False):
    image = np.full((420,900,3), paper, np.uint8)
    cv2.putText(image, 'Escritura azul', (45,125), cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, 1.8, (140,35,20), 2, cv2.LINE_AA)
    if neutral_gray is not None:
        cv2.putText(image, 'Trazo neutro', (55,270), cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, 1.8, (neutral_gray,)*3, thickness, cv2.LINE_AA)
    if shade:
        lighting = np.linspace(.8,1,900,dtype=np.float32)[None,:,None]
        image = np.clip(image.astype(np.float32)*lighting,0,255).astype(np.uint8)
    return image


def analyze(image):
    mask, _ = Processor.extract_ink_mask(image)
    return InkAnalyzer.analyze(image,mask), mask


class MaterialInventoryTests(unittest.TestCase):
    def test_blue_plus_neutral_at_five_gray_levels_and_three_thicknesses(self):
        for gray in [25,100,180,210,230]:
            for thickness in [1,2,3]:
                with self.subTest(gray=gray,thickness=thickness):
                    result,mask = analyze(material_scene(gray,thickness))
                    self.assertGreater(np.count_nonzero(mask[180:330]), 100)
                    self.assertTrue(result['mixed_colored_neutral'])
                    self.assertGreater(result['neutral_pixel_count'],25)
                    self.assertTrue(result['requires_context'])
                    self.assertEqual(result['neutral_material_identity'],'undetermined')
                    self.assertFalse(result['different_materials_confirmed'])

    def test_warm_paper_and_gradual_shadows_preserve_neutral_marks(self):
        for paper in [(250,250,250),(220,230,240)]:
            for shade in [False,True]:
                with self.subTest(paper=paper,shade=shade):
                    # El lápiz tiene contraste positivo respecto de ambos soportes.
                    result,_ = analyze(material_scene(195,1,paper,shade))
                    self.assertTrue(result['mixed_colored_neutral'])

    def test_jpeg_and_reduced_photo_preserve_blue_plus_pale_gray(self):
        for quality in [70,90]:
            for scale in [.7,1]:
                with self.subTest(quality=quality,scale=scale):
                    image = cv2.resize(material_scene(210,1),None,fx=scale,fy=scale)
                    data = cv2.imencode('.jpg',image,[cv2.IMWRITE_JPEG_QUALITY,quality])[1]
                    image = cv2.imdecode(data,cv2.IMREAD_COLOR)
                    result,_ = analyze(image)
                    self.assertTrue(result['mixed_colored_neutral'])

    def test_blue_alone_does_not_count_its_antialias_halo_as_pencil(self):
        for thickness in [1,2,3]:
            image = material_scene(None)
            # Otra inscripción del mismo azul, con distinto grosor.
            cv2.putText(image,'Una sola tinta',(55,270),cv2.FONT_HERSHEY_SCRIPT_SIMPLEX,1.8,(140,35,20),thickness,cv2.LINE_AA)
            result,_ = analyze(image)
            self.assertFalse(result['mixed_colored_neutral'])
            self.assertFalse(result['chromatic_multiple_detected'])

    def test_gray_only_does_not_claim_pencil_identity_or_authenticity(self):
        image = np.full((420,900,3),250,np.uint8)
        cv2.putText(image,'Escritura gris',(55,210),cv2.FONT_HERSHEY_SCRIPT_SIMPLEX,2,(185,185,185),1,cv2.LINE_AA)
        result,_ = analyze(image)
        self.assertEqual(result['evidence_status'],'neutral_only_material_undetermined')
        self.assertEqual(result['neutral_material_identity'],'undetermined')
        self.assertFalse(result['different_materials_confirmed'])

    def test_plain_paper_texture_does_not_become_a_material(self):
        rng = np.random.default_rng(17)
        texture = rng.integers(-2,3,(420,900,1))
        image = np.clip(np.full((420,900,3),247)+texture,0,255).astype(np.uint8)
        mask,_ = Processor.extract_ink_mask(image)
        self.assertEqual(np.count_nonzero(mask),0)

    def test_perspective_does_not_crop_to_an_inner_amount_box(self):
        image = material_scene(195,1)
        cv2.rectangle(image,(410,100),(860,270),(50,50,50),2)
        corrected,changed = Processor.rectify_perspective(image)
        self.assertFalse(changed)
        self.assertEqual(corrected.shape,image.shape)
        self.assertTrue(analyze(corrected)[0]['mixed_colored_neutral'])

    def test_full_api_preserves_blue_plus_faint_gray_and_requests_review(self):
        client = TestClient(main.app)
        for gray in [100,210,230]:
            for rectify in [False,True]:
                with self.subTest(gray=gray,rectify=rectify):
                    encoded = cv2.imencode('.png',material_scene(gray,1))[1]
                    response = client.post('/api/analyze/full',json={
                        'image_base64':base64.b64encode(encoded).decode(),
                        'rectify_perspective':rectify,
                    })
                    self.assertEqual(response.status_code,200)
                    result = response.json()
                    self.assertTrue(result['success'])
                    self.assertEqual(result['analysis_version'],'1.2.0')
                    self.assertTrue(result['inks_analysis']['mixed_colored_neutral'])
                    self.assertFalse(result['judicial_report']['authenticity_determined'])
                    self.assertTrue(any(rule['code']=='OBS-NEUTRAL-01' for rule in result['judicial_report']['rules_triggered']))
                    self.assertNotEqual(result['judicial_report']['verdict_color'],'emerald')
                    self.assertIn('No acredita legitimidad',result['tampering_analysis']['verdict'])

    def test_no_character_regions_is_not_conformity(self):
        image = np.full((400,800,3),250,np.uint8)
        cv2.line(image,(50,200),(750,200),(140,35,20),3)
        result = main.tampering_detector.detect(image,Processor.extract_ink_mask(image)[0])
        self.assertEqual(result['evaluated_regions'],0)
        self.assertEqual(result['evidence_status'],'not_evaluable')
        self.assertIn('NO EVALUABLE',result['verdict'])

    def test_excessive_dimensions_are_rejected_before_bitmap_allocation(self):
        png = bytearray(cv2.imencode('.png',np.full((1,1,3),250,np.uint8))[1].tobytes())
        # Cambiar sólo IHDR y su CRC: no reservar un bitmap enorme en el test.
        png[16:24] = struct.pack('>II',5000,5000)
        png[29:33] = struct.pack('>I',zlib.crc32(png[12:29]) & 0xffffffff)
        with patch('modules.vision.processor.cv2.imdecode') as decode:
            with self.assertRaisesRegex(ValueError,'24 megapíxeles'):
                Processor.decode_image(bytes(png))
            decode.assert_not_called()

    def test_user_supplied_blue_and_pencil_photo_when_available(self):
        # La foto del usuario permanece local, fuera de Git y del despliegue.
        photo = Path(main.__file__).parents[1] / 'lapicero azul y lapiz negro.jpeg'
        if not photo.exists():
            self.skipTest('Foto del usuario disponible sólo en el entorno local')
        image = Processor.prepare_for_analysis(cv2.imread(str(photo)))
        image,_ = Processor.rectify_perspective(image)
        result,_ = analyze(image)
        self.assertTrue(result['mixed_colored_neutral'])
        self.assertTrue(result['neutral_marks_detected'])
        self.assertGreater(result['neutral_pixel_count'],25)
        self.assertFalse(result['different_materials_confirmed'])


if __name__ == '__main__':
    unittest.main()
