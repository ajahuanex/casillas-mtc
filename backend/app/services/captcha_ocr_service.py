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


def clean_captcha_chars(raw: str) -> str:
    """
    Normaliza caracteres predichos por el OCR para el formato estricto del MTC:
    - Los captchas del MTC son letras MAYÚSCULAS (A-Z) y dígitos (0-9).
    - En la tipografía del MTC, la letra 'I' mayúscula es un trazo vertical simple sin serifa.
      ddddocr la predice frecuentemente como 'l' (ele minúscula) o 'i' minúscula.
      Por tanto, 'l' e 'i' se mapean a 'I' mayúscula.
    - La letra 'L' mayúscula real (con base horizontal inferior) es predicha como 'L' mayúscula y se preserva.
    - El resto de caracteres se convierte a mayúscula y se eliminan espacios o símbolos extraños.
    """
    cleaned = []
    for c in raw:
        if c in ('l', 'i'):
            cleaned.append('I')
        else:
            cleaned.append(c.upper())
    return re.sub(r"[^A-Z0-9]", "", "".join(cleaned)).strip()


def resolve_ocr(base64_img: str, strict_6_chars: bool = True) -> str:
    """
    Convierte una imagen Captcha en Base64 del MTC a texto limpio.
    
    Estrategia de Doble Motor:
    1. Motor Primario (Red Neuronal Profunda ONNX - ddddocr):
       Especializado en captchas alfanuméricos con ruido de fondo y distorsión.
       Mapea 'l'/'i' -> 'I' y conserva 'L' -> 'L'.
    2. Motor Secundario (OpenCV + Tesseract fallback):
       Si ddddocr no está disponible o no produce 6 caracteres, aplica OpenCV + Tesseract.

    Si strict_6_chars es True, descarta cualquier predicción que no tenga
    exactamente 6 caracteres para evitar fallos de autenticación en el MTC.
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
            pred_clean = clean_captcha_chars(pred_raw)
            if len(pred_clean) == 6:
                logger.info(f"[OCR] Captcha resuelto por motor neuronal ddddocr: '{pred_clean}' (raw: '{pred_raw}')")
                return pred_clean
            else:
                logger.warning(f"[OCR] Captcha ddddocr con longitud no óptima ({len(pred_clean)} != 6): '{pred_clean}' (raw: '{pred_raw}')")
                if not strict_6_chars and 4 <= len(pred_clean) <= 8:
                    return pred_clean
        except Exception as dddd_err:
            logger.warning(f"[OCR] Error en motor neuronal ddddocr ({dddd_err}), pasando a fallback Tesseract...")

    # 3. MOTOR SECUNDARIO: OpenCV + Tesseract
    if not OCR_LIBS_AVAILABLE:
        if strict_6_chars:
            raise ValueError("El motor neuronal no produjo un captcha de 6 caracteres y no hay motor Tesseract secundario.")
        raise RuntimeError("Ningún motor OCR disponible en el entorno.")

    try:
        # Decodificar a imagen OpenCV
        np_arr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if img is None:
            pil_img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
            img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

        # Escala de grises directa
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape

        # Recorte de bordes perimetrales
        crop_top_bottom = max(1, int(h * 0.04))
        crop_left_right = max(2, int(w * 0.025))
        cropped = gray[crop_top_bottom:h - crop_top_bottom, crop_left_right:w - crop_left_right]

        # Variantes de preprocesamiento
        _, otsu = cv2.threshold(cropped, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        otsu_inv = cv2.bitwise_not(otsu)
        ch, cw = cropped.shape
        resized_gray = cv2.resize(cropped, (cw * 2, ch * 2), interpolation=cv2.INTER_CUBIC)

        whitelist = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
        candidates = []
        test_images = [cropped, otsu, resized_gray, otsu_inv]
        test_psms = [8, 13, 7, 6]

        for target in test_images:
            for psm in test_psms:
                cfg = f"--oem 3 --psm {psm} -c tessedit_char_whitelist={whitelist}"
                try:
                    txt = pytesseract.image_to_string(target, config=cfg)
                    clean = clean_captcha_chars(txt)
                    if len(clean) == 6:
                        logger.info(f"[OCR] Captcha resuelto por Tesseract: '{clean}' (PSM {psm})")
                        return clean
                    elif 5 <= len(clean) <= 7:
                        candidates.append(clean)
                except Exception:
                    pass

        if candidates:
            candidates.sort(key=lambda x: (abs(len(x) - 6), -len(x)))
            best = candidates[0]
            if strict_6_chars and len(best) != 6:
                raise ValueError(f"Tesseract produjo longitud {len(best)} ('{best}'), se requiere exactamente 6 caracteres.")
            return best

        if strict_6_chars:
            raise ValueError("No se pudo obtener un captcha de 6 caracteres con certeza.")

        cfg_fallback = f"--oem 3 --psm 8 -c tessedit_char_whitelist={whitelist}"
        raw_out = pytesseract.image_to_string(cropped, config=cfg_fallback)
        return clean_captcha_chars(raw_out)

    except Exception as e:
        logger.error(f"[OCR] Error durante el procesamiento de la imagen: {e}")
        raise ValueError(f"Fallo al procesar OCR de captcha: {str(e)}")

