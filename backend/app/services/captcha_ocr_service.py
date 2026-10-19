import base64
import io
import re
import logging
from typing import Optional
from PIL import Image

logger = logging.getLogger(__name__)

# Intentar importar librerías de visión por computadora
try:
    import cv2
    import numpy as np
    import pytesseract
    OCR_LIBS_AVAILABLE = True
except ImportError:
    OCR_LIBS_AVAILABLE = False
    logger.warning("[OCR] pytesseract, cv2 o numpy no están instalados aún.")

# Intentar inicializar modelo neuronal ddddocr especializado en captchas
try:
    import ddddocr
    _ddddocr_engine = ddddocr.DdddOcr(show_ad=False)
    DDDDOCR_AVAILABLE = True
    logger.info("[OCR] Motor neuronal ddddocr cargado exitosamente.")
except Exception as e:
    _ddddocr_engine = None
    DDDDOCR_AVAILABLE = False
    logger.warning(f"[OCR] ddddocr no disponible, se usará Tesseract: {e}")


def resolve_ocr(base64_img: str) -> str:
    """
    Convierte una imagen Captcha en Base64 del MTC a texto limpio.
    
    Estrategia de Doble Motor:
    1. Motor Primario (Red Neuronal Profunda ONNX - ddddocr):
       Entrenado específicamente en captchas alfanuméricos con ruido de puntos,
       inclinación y texturas huecas. Resuelve con alta precisión caracteres
       críticos que confunden a Tesseract (ej: 8 vs S, 1 vs T, 9 vs 0).
    2. Motor Secundario (OpenCV + Tesseract fallback):
       Si ddddocr no está disponible o falla, aplica binarización Otsu y PSM 8.
    """
    if not base64_img or not isinstance(base64_img, str):
        raise ValueError("La imagen captcha en base64 no es válida o está vacía.")

    # 1. Limpiar prefijos de Data URI si existen
    clean_b64 = re.sub(r"^data:image/[a-zA-Z]+;base64,", "", base64_img.strip())
    # Corregir padding si falta
    missing_padding = len(clean_b64) % 4
    if missing_padding:
        clean_b64 += "=" * (4 - missing_padding)

    try:
        img_bytes = base64.b64decode(clean_b64)
    except Exception as e:
        logger.error(f"[OCR] Error al decodificar base64: {e}")
        raise ValueError(f"No se pudo decodificar la imagen Base64: {str(e)}")

    # 2. MOTOR PRIMARIO: Red Neuronal ddddocr
    if DDDDOCR_AVAILABLE and _ddddocr_engine is not None:
        try:
            pred_raw = _ddddocr_engine.classification(img_bytes)
            pred_clean = re.sub(r"[^A-Za-z0-9]", "", pred_raw).upper().strip()
            if len(pred_clean) == 6:
                logger.info(f"[OCR] Captcha resuelto por motor neuronal ddddocr: '{pred_clean}'")
                return pred_clean
            elif 5 <= len(pred_clean) <= 7:
                logger.info(f"[OCR] Captcha ddddocr con longitud {len(pred_clean)}: '{pred_clean}'")
                return pred_clean
        except Exception as dddd_err:
            logger.warning(f"[OCR] Error en motor neuronal ddddocr ({dddd_err}), pasando a fallback Tesseract...")

    # 3. MOTOR SECUNDARIO: OpenCV + Tesseract
    if not OCR_LIBS_AVAILABLE:
        raise RuntimeError("Ningún motor OCR disponible en el entorno.")

    try:
        # 2. Decodificar a imagen OpenCV
        np_arr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if img is None:
            # Intentar abrir con PIL y convertir a NumPy array
            pil_img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
            img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

        # 3. Escala de grises directa
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape

        # 4. Recorte de bordes perimetrales (elimina líneas negras/grises de borde)
        crop_top_bottom = max(1, int(h * 0.04))
        crop_left_right = max(2, int(w * 0.025))
        cropped = gray[crop_top_bottom:h - crop_top_bottom, crop_left_right:w - crop_left_right]

        # 5. Variantes de imagen para prueba
        # a) Cropped raw
        # b) Otsu Thresholding
        _, otsu = cv2.threshold(cropped, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        # c) Inverted Otsu
        otsu_inv = cv2.bitwise_not(otsu)
        # d) Resized x2
        ch, cw = cropped.shape
        resized_gray = cv2.resize(cropped, (cw * 2, ch * 2), interpolation=cv2.INTER_CUBIC)

        whitelist = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        
        candidates = []
        # Probar en orden de mayor efectividad
        test_images = [cropped, otsu, resized_gray, otsu_inv]
        test_psms = [8, 13, 7, 6]

        for target in test_images:
            for psm in test_psms:
                cfg = f"--oem 3 --psm {psm} -c tessedit_char_whitelist={whitelist}"
                try:
                    txt = pytesseract.image_to_string(target, config=cfg)
                    clean = re.sub(r"[^A-Z0-9]", "", txt.upper()).strip()
                    if len(clean) == 6:
                        # Candidato perfecto (los captchas del MTC son exactamente de 6 caracteres alfanuméricos)
                        logger.info(f"[OCR] Captcha resuelto óptimo: '{clean}' (PSM {psm})")
                        return clean
                    elif 5 <= len(clean) <= 7:
                        candidates.append(clean)
                except Exception:
                    pass

        if candidates:
            # Seleccionar el candidato con longitud 6 o más cercano a 6
            candidates.sort(key=lambda x: (abs(len(x) - 6), -len(x)))
            cleaned_text = candidates[0]
        else:
            # Fallback
            cfg_fallback = f"--oem 3 --psm 8 -c tessedit_char_whitelist={whitelist}"
            raw_out = pytesseract.image_to_string(cropped, config=cfg_fallback)
            cleaned_text = re.sub(r"[^A-Z0-9]", "", raw_out.upper()).strip()

        logger.info(f"[OCR] Captcha resuelto: '{cleaned_text}' (longitud: {len(cleaned_text)})")
        return cleaned_text

    except Exception as e:
        logger.error(f"[OCR] Error durante el procesamiento de la imagen: {e}")
        raise RuntimeError(f"Fallo al procesar OCR de captcha: {str(e)}")
