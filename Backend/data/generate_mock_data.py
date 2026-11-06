import cv2
import numpy as np
import os
import base64

def create_sample_check_clean():
    # Cheque bancario autentico (tinta azul uniforme, trazo fluido)
    img = np.full((400, 800, 3), 250, dtype=np.uint8)
    cv2.rectangle(img, (20, 20), (780, 380), (190, 190, 190), 2)
    ink_color = (140, 35, 20) # Tinta azul uniforme en todo el documento
    
    cv2.putText(img, "BANCO NACIONAL - CHEQUE DE GERENCIA", (40, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.75, ink_color, 2)
    cv2.putText(img, "PAGUESE A LA ORDEN DE: Juan Perez Alarcon", (40, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.55, ink_color, 1)
    cv2.putText(img, "LA SUMA DE: Cien con 00/100 Dolares", (40, 185), cv2.FONT_HERSHEY_SIMPLEX, 0.55, ink_color, 1)
    
    # Monto en caja
    cv2.rectangle(img, (580, 110), (750, 160), (140, 140, 140), 2)
    cv2.putText(img, "$ 100.00", (600, 145), cv2.FONT_HERSHEY_SIMPLEX, 0.85, ink_color, 2)

    # Firma genuina fluida y rapida
    pts = np.array([[520, 320], [550, 280], [580, 330], [620, 270], [660, 310], [710, 290]], np.int32)
    cv2.polylines(img, [pts], False, ink_color, 3, cv2.LINE_AA)
    cv2.putText(img, "FIRMA AUTORIZADA", (560, 355), cv2.FONT_HERSHEY_SIMPLEX, 0.45, ink_color, 1)
    return img

def create_sample_check_altered():
    # Cheque con enmienda fraudulenta (se anadio un cero con otro boligrafo)
    img = create_sample_check_clean()
    # Adulteracion: anadir un cero "$ 1000.00" con tinta diferente (rojo/negro)
    cv2.putText(img, "0", (700, 145), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (20, 20, 215), 3) # Tinta 2 claramente diferente
    # Adicion de clausula falsa con Tinta 2
    cv2.putText(img, "CLAUSULA ADICIONAL: Pago de rescate", (40, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (20, 20, 215), 2)
    return img

def create_sample_forged():
    # Documento con firma falsificada temblorosa
    img = np.full((400, 800, 3), 250, dtype=np.uint8)
    cv2.rectangle(img, (20, 20), (780, 380), (180, 180, 180), 2)
    cv2.putText(img, "CONTRATO PRIVADO DE COMPRAVENTA", (40, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (40, 40, 40), 2)
    cv2.putText(img, "POR EL PRESENTE DOCUMENTO SE CEDE EL TOTAL DEL INMUEBLE", (40, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (30, 30, 30), 1)
    
    # Firma con titubeos y temblores marcados (Ataxia por calco lento)
    pts = []
    np.random.seed(42)
    for x in range(500, 720, 4):
        jitter = np.random.randint(-12, 13) if (x % 8 == 0) else int(15 * np.sin(x * 0.25))
        y = 300 + int(20 * np.sin(x * 0.05)) + jitter
        pts.append([x, y])
    pts = np.array(pts, np.int32)
    cv2.polylines(img, [pts], False, (50, 40, 160), 2, cv2.LINE_AA)
    cv2.putText(img, "FIRMA DEL CEDENTE", (550, 355), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (100, 100, 100), 1)
    return img

def create_sample_blank_signature():
    # Documento de firma en blanco: linea de texto cruza por encima de la firma
    img = np.full((400, 800, 3), 250, dtype=np.uint8)
    cv2.putText(img, "PAGARE A LA VISTA", (40, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (40, 40, 40), 2)
    
    # 1. Firma dibujada primero (subyacente)
    pts = np.array([[380, 260], [420, 180], [470, 280], [530, 170], [600, 250]], np.int32)
    cv2.polylines(img, [pts], False, (140, 40, 20), 3, cv2.LINE_AA)

    # 2. Linea de texto o sello impresa DESPUES encima de la firma
    cv2.line(img, (200, 230), (700, 230), (10, 10, 10), 4, cv2.LINE_AA)
    cv2.putText(img, "DEBO Y PAGARE INCONDICIONALMENTE LA SUMA DE $50,000 USD", (40, 220), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (10, 10, 10), 1)
    return img


os.makedirs('data/samples', exist_ok=True)
cv2.imwrite('data/samples/check_clean.png', create_sample_check_clean())
cv2.imwrite('data/samples/check_altered.png', create_sample_check_altered())
cv2.imwrite('data/samples/forged_contract.png', create_sample_forged())
cv2.imwrite('data/samples/blank_signature.png', create_sample_blank_signature())
print("Mock forensic samples generated successfully in data/samples/")
