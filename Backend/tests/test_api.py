"""Regresiones del flujo de presentación. Ejecutar desde Backend:
python -m unittest discover -s tests -v
"""
import asyncio
import base64
import hashlib
import json
from pathlib import Path
import threading
import unittest
from unittest.mock import patch

import cv2
import httpx
import numpy as np
from fastapi.testclient import TestClient

import main
from modules.vision.processor import DocumentProcessor

SAMPLES = Path(main.__file__).parent / 'data' / 'samples'


def payload(raw):
    return {'image_base64': base64.b64encode(raw).decode('ascii')}


def encode(image):
    return cv2.imencode('.png', image)[1].tobytes()


class ApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(main.app)

    def test_samples_and_benchmarks(self):
        samples = self.client.get('/api/samples').json()['samples']
        self.assertEqual(len(samples), 4)
        self.assertEqual(len(self.client.get('/api/benchmark/models').json()['models_evaluated']), 6)
        self.assertEqual(self.client.get('/api/health').status_code, 200)

    def test_all_demo_documents_and_original_hash(self):
        for sample in SAMPLES.glob('*.png'):
            with self.subTest(sample=sample.name):
                raw = sample.read_bytes()
                response = self.client.post('/api/analyze/full', json=payload(raw))
                self.assertEqual(response.status_code, 200)
                result = response.json()
                self.assertTrue(result['success'])
                self.assertEqual(result['judicial_report']['doc_hash'], hashlib.sha256(raw).hexdigest())
                self.assertGreater(result['processing_seconds'], 0)
                self.assertIn('chronology', result['stage_timings_seconds'])
                self.assertEqual(result['judicial_report']['fraud_points'] == 0, sample.name == 'check_clean.png')
                # Rechaza NaN / Infinity que romperían la serialización JSON del servidor.
                json.dumps(result, allow_nan=False)

    def test_invalid_images_are_client_errors_and_release_slot(self):
        for path in ['/api/analyze/full', '/api/signatures/compare_dual']:
            for value in ['not-base64!', '', base64.b64encode(b'not an image').decode()]:
                with self.subTest(path=path, value=value):
                    self.assertEqual(self.client.post(path, json={'image_base64': value}).status_code, 400)
        self.assertTrue(main.analysis_slot.acquire(blocking=False))
        main.analysis_slot.release()

    def test_blank_document_rejected(self):
        raw = encode(np.full((300, 400, 3), 255, dtype=np.uint8))
        for path in ['/api/analyze/full', '/api/signatures/compare_dual']:
            result = self.client.post(path, json=payload(raw)).json()
            self.assertFalse(result['success'])
            self.assertIn('message', result)

    def test_too_small_and_oversize_payload(self):
        raw = encode(np.full((10, 10, 3), 255, dtype=np.uint8))
        self.assertEqual(self.client.post('/api/analyze/full', json=payload(raw)).status_code, 400)
        with self.assertRaises(ValueError):
            DocumentProcessor.decode_base64_bytes('a' * 22_000_001)

    def test_large_photo_bounded_resolution(self):
        image = np.full((3000, 4000, 3), 255, dtype=np.uint8)
        resized = DocumentProcessor.prepare_for_analysis(image)
        self.assertEqual(resized.shape, (1200, 1600, 3))

    def test_repeated_analysis_is_stable(self):
        request = payload((SAMPLES / 'check_altered.png').read_bytes())
        first = self.client.post('/api/analyze/full', json=request).json()
        second = self.client.post('/api/analyze/full', json=request).json()
        self.assertEqual(first['inks_analysis'], second['inks_analysis'])
        self.assertEqual(first['judicial_report']['fraud_points'], second['judicial_report']['fraud_points'])
        self.assertNotEqual(first['judicial_report']['case_id'], second['judicial_report']['case_id'])

    def test_dual_signatures_success_and_insufficient_material(self):
        image = np.full((400, 800, 3), 255, dtype=np.uint8)
        cv2.putText(image, 'Firma', (40, 240), cv2.FONT_HERSHEY_SCRIPT_COMPLEX, 2, (80, 30, 20), 3)
        cv2.putText(image, 'Firma', (440, 240), cv2.FONT_HERSHEY_SCRIPT_COMPLEX, 2, (80, 30, 20), 3)
        result = self.client.post('/api/signatures/compare_dual', json=payload(encode(image))).json()
        self.assertTrue(result['success'])
        self.assertFalse(result['is_forgery'])
        image[:, 400:] = 255
        result = self.client.post('/api/signatures/compare_dual', json=payload(encode(image))).json()
        self.assertFalse(result['success'])
        self.assertIn('message', result)


class ConcurrencyTests(unittest.IsolatedAsyncioTestCase):
    async def test_health_remains_available_and_second_analysis_rejected(self):
        entered = threading.Event()
        release = threading.Event()
        original = main.InkAnalyzer.analyze

        def slow_analysis(*args, **kwargs):
            entered.set()
            if not release.wait(timeout=5):
                raise RuntimeError('Test did not release analysis')
            return original(*args, **kwargs)

        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=main.app), base_url='http://test') as client:
            with patch.object(main.InkAnalyzer, 'analyze', side_effect=slow_analysis):
                request = payload((SAMPLES / 'check_clean.png').read_bytes())
                pending = asyncio.create_task(client.post('/api/analyze/full', json=request))
                try:
                    self.assertTrue(await asyncio.to_thread(entered.wait, 2))
                    health = await asyncio.wait_for(client.get('/api/health'), timeout=1)
                    self.assertEqual(health.status_code, 200)
                    for path in ['/api/analyze/full', '/api/signatures/compare_dual']:
                        busy = await asyncio.wait_for(client.post(path, json=request), timeout=1)
                        self.assertEqual(busy.status_code, 503)
                        self.assertEqual(busy.headers['retry-after'], '5')
                finally:
                    release.set()
                    result = await pending
                self.assertEqual(result.status_code, 200)


if __name__ == '__main__':
    unittest.main()
