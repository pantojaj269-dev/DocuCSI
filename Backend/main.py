from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import base64
import os
import logging
import time
from pathlib import Path
from threading import BoundedSemaphore

# Evitar sobreasignar CPU y memoria en instancias pequeñas de Render.
os.environ.setdefault('OMP_NUM_THREADS', '1')
os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('MKL_NUM_THREADS', '1')
import cv2
import numpy as np
import torch

cv2.setNumThreads(1)
torch.set_num_threads(1)

from modules.vision.processor import DocumentProcessor
from modules.inks.analyzer import InkAnalyzer
from modules.tampering.detector import TamperingDetector
from modules.signatures.verifier import SignatureVerifier
from modules.chronology.a_star import ChronologyAnalyzer
from modules.expert_system.engine import ForensicExpertSystem

app = FastAPI(
    title="DocuCSI - Suite Inteligente de Peritaje Documental Forense",
    description="Plataforma Neuro-Simbolica de Investigacion Criminalistica de Documentos",
    version="1.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instanciar detectores
tampering_detector = TamperingDetector()
signature_verifier = SignatureVerifier()
analysis_slot = BoundedSemaphore(1)
logger = logging.getLogger('docucsi')

class Base64Payload(BaseModel):
    image_base64: str
    rectify_perspective: bool = True

@app.get("/api/health")
def health_check():
    return {"status": "online", "system": "DocuCSI Forensic Suite", "version": "1.1.0"}

@app.get("/api/samples")
def get_sample_documents():
    samples_dir = Path(__file__).resolve().parent / 'data' / 'samples'
    if not os.path.exists(samples_dir):
        return {"samples": []}

    results = []
    metadata = {
        "check_clean.png": {"title": "Cheque Legitimo", "description": "Documento bancario con tinta homogenea y firma genuina."},
        "check_altered.png": {"title": "Cheque Adulterado ($100 -> $1000)", "description": "Enmienda con adicion de un cero y clausula en tinta diferente."},
        "forged_contract.png": {"title": "Contrato con Firma Falsificada", "description": "Firma con titubeos y temblores motores (Pellat Ley 2)."},
        "blank_signature.png": {"title": "Abuso de Firma en Blanco", "description": "Texto del pagare redactado fisicamente encima de una firma previa."}
    }

    for fname in sorted(os.listdir(samples_dir)):
        if fname.endswith(".png"):
            fpath = os.path.join(samples_dir, fname)
            img = cv2.imread(fpath)
            if img is not None:
                _, buf = cv2.imencode(".png", img)
                b64_str = "data:image/png;base64," + base64.b64encode(buf).decode("utf-8")
                info = metadata.get(fname, {"title": fname, "description": "Muestra forense"})
                results.append({
                    "id": fname,
                    "title": info["title"],
                    "description": info["description"],
                    "image_base64": b64_str
                })
    return {"samples": results}

@app.get("/api/benchmark/models")
def get_benchmark_models():
    return {
        "status": "success",
        "models_evaluated": tampering_detector.benchmark_results,
        "best_model": tampering_detector.best_model_name,
        "deep_learning_mlp_loss": signature_verifier.loss_history
    }

@app.post("/api/analyze/full")
def analyze_full_document(payload: Base64Payload):
    if not analysis_slot.acquire(blocking=False):
        raise HTTPException(status_code=503, detail='El servidor está procesando otro peritaje. Espera unos segundos y vuelve a intentar.', headers={'Retry-After': '5'})
    started = time.perf_counter()
    timings = {}

    def record_stage(name):
        now = time.perf_counter()
        timings[name] = round(now - started - sum(timings.values()), 3)

    try:
        original_bytes = DocumentProcessor.decode_base64_bytes(payload.image_base64)
        image = DocumentProcessor.prepare_for_analysis(DocumentProcessor.decode_image(original_bytes))
        record_stage('decode')
        
        # 0. Validador de Entrada Pericial (Guardia de Percepción)
        is_valid, val_msg, val_details = DocumentProcessor.validate_document(image)
        if not is_valid:
            return {
                "success": False,
                "is_document": False,
                "error_title": "ADVERTENCIA DE PERCEPCION FORENSE",
                "message": val_msg,
                "validation_details": val_details
            }

        # 1. Rectificacion de perspectiva
        rectified = image
        rectified_status = False
        if payload.rectify_perspective:
            rectified, rectified_status = DocumentProcessor.rectify_perspective(image)

        # 2. Extraccion de mascara de tinta y esqueleto
        ink_mask, gray = DocumentProcessor.extract_ink_mask(rectified)
        record_stage('preprocessing')

        # 3. Analisis No Supervisado de Tintas (K-Means, DBSCAN, PCA)
        inks_res = InkAnalyzer.analyze(rectified, ink_mask)
        record_stage('inks')

        # 4. Analisis Supervisado de Adulteracion de Cifras
        tampering_res = tampering_detector.detect(rectified, ink_mask)
        record_stage('tampering')

        # 5. Verificacion de Firma y Presion con Deep Learning (PyTorch)
        signature_res = signature_verifier.verify(rectified, ink_mask)
        record_stage('signature')

        # 6. Analisis de Cronologia de Cruce con Algoritmo A*
        chronology_res = ChronologyAnalyzer.analyze_intersection(rectified, ink_mask)
        signature_res = signature_verifier.account_for_overlap(signature_res, chronology_res, rectified.shape)
        record_stage('chronology')

        # 7. Evaluacion del Sistema Experto y Dictamen Judicial
        findings = {
            'inks': inks_res,
            'tampering': tampering_res,
            'signature': signature_res,
            'chronology': chronology_res
        }
        judicial_report = ForensicExpertSystem.evaluate(findings, original_bytes)

        # Codificar imagenes resultantes
        _, rect_buf = cv2.imencode(".png", rectified)
        _, mask_buf = cv2.imencode(".png", ink_mask)
        record_stage('report_and_encoding')

        return {
            "success": True,
            "processing_seconds": round(time.perf_counter() - started, 3),
            "stage_timings_seconds": timings,
            "analysis_dimensions": {"width": int(image.shape[1]), "height": int(image.shape[0])},
            "rectified_perspective": rectified_status,
            "rectified_image_b64": "data:image/png;base64," + base64.b64encode(rect_buf).decode("utf-8"),
            "ink_mask_b64": "data:image/png;base64," + base64.b64encode(mask_buf).decode("utf-8"),
            "inks_analysis": inks_res,
            "tampering_analysis": tampering_res,
            "signature_analysis": signature_res,
            "chronology_analysis": chronology_res,
            "judicial_report": judicial_report
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.exception('Error en análisis forense')
        raise HTTPException(status_code=500, detail='No se pudo completar el análisis. Intenta con otra imagen.') from e
    finally:
        analysis_slot.release()

@app.post("/api/signatures/compare_dual")
def compare_dual_signatures_endpoint(payload: Base64Payload):
    """
    Cotejo Grafotecnico Comparativo Directo:
    Analiza una misma hoja con dos firmas (Izquierda: Patron Original, Derecha: Cuestionada / Imitacion).
    """
    if not analysis_slot.acquire(blocking=False):
        raise HTTPException(status_code=503, detail='El servidor está procesando otro peritaje. Espera unos segundos y vuelve a intentar.', headers={'Retry-After': '5'})
    try:
        image = DocumentProcessor.prepare_for_analysis(DocumentProcessor.decode_base64(payload.image_base64))
        is_valid, msg, _ = DocumentProcessor.validate_document(image)
        if not is_valid:
            return {
                "success": False,
                "error_type": "VALIDATION_FAILED",
                "message": msg
            }

        ink_mask, _ = DocumentProcessor.extract_ink_mask(image)
        comparison_res = signature_verifier.compare_dual_signatures(image, ink_mask)
        return comparison_res
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.exception('Error en cotejo dual')
        raise HTTPException(status_code=500, detail='No se pudo completar el cotejo de firmas.') from e
    finally:
        analysis_slot.release()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

