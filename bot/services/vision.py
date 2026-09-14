"""Skrinshotdan matnni o'qish (OCR) — ko'ruvlar soni va akkaunt nomini aniqlash.

Standart dvigatel: RapidOCR (onnxruntime) — to'liq offline, API kalit kerak emas.
Kutubxona yo'q bo'lsa bot ishdan chiqmaydi: OCR shunchaki o'chiriladi va
foydalanuvchi kiritgan qiymat avvalgidek ishlayveradi.
"""
import asyncio
import io
import logging
from dataclasses import dataclass

from .utils import detect_handle, parse_views_from_text

log = logging.getLogger(__name__)

_engine = None
_load_attempted = False


def _get_engine():
    """RapidOCR'ni bir marta (lazy) yuklaydi. Yuklanmasa None qaytaradi."""
    global _engine, _load_attempted
    if _load_attempted:
        return _engine
    _load_attempted = True
    try:
        from rapidocr_onnxruntime import RapidOCR
        _engine = RapidOCR()
        log.info("OCR dvigatel (RapidOCR) yuklandi")
    except Exception as e:  # noqa: BLE001
        _engine = None
        log.warning("RapidOCR yuklanmadi — skrinshot tekshiruvi o'chirilgan: %s", e)
    return _engine


def _decode_image(data: bytes):
    import cv2
    import numpy as np
    arr = np.frombuffer(data, np.uint8)
    return cv2.imdecode(arr, cv2.IMREAD_COLOR)


def _run_ocr(data: bytes) -> list[tuple[str, float]]:
    """(matn, ishonch) juftliklari ro'yxatini qaytaradi."""
    engine = _get_engine()
    if engine is None:
        return []
    img = _decode_image(data)
    if img is None:
        return []
    try:
        result, _elapse = engine(img)
    except Exception as e:  # noqa: BLE001
        log.warning("OCR ishlamadi: %s", e)
        return []
    out: list[tuple[str, float]] = []
    for item in (result or []):
        try:
            text, score = item[1], float(item[2])
        except (IndexError, TypeError, ValueError):
            continue
        if text and str(text).strip():
            out.append((str(text).strip(), score))
    return out


@dataclass
class VisionResult:
    available: bool = False
    views: int | None = None          # skrinshotdan o'qilgan ko'ruvlar soni
    handle: str | None = None         # skrinshotdan o'qilgan akkaunt nomi
    confidence: float | None = None   # OCR ishonch darajasi (0..1)
    raw_text: str = ""                # tekshirish uchun xom matn


def _analyze_bytes(data: bytes, known_handle: str | None) -> VisionResult:
    lines = _run_ocr(data)
    if not lines:
        return VisionResult()
    text = "\n".join(ln for ln, _ in lines)
    views = parse_views_from_text(text)
    handle = detect_handle(text, known_handle)
    conf = max((s for _, s in lines), default=None)
    return VisionResult(available=True, views=views, handle=handle,
                        confidence=conf, raw_text=text)


async def analyze_screenshot(bot, file_id: str,
                             known_handle: str | None = None) -> VisionResult:
    """Telegram'dan skrinshotni yuklab, OCR bilan tahlil qiladi.

    Hech qachon xato otmaydi — muammo bo'lsa `available=False` qaytaradi.
    """
    buf = io.BytesIO()
    try:
        await bot.download(file_id, destination=buf)
    except Exception as e:  # noqa: BLE001
        log.warning("Skrinshot yuklab olinmadi (%s): %s", file_id, e)
        return VisionResult()
    data = buf.getvalue()
    if not data:
        return VisionResult()
    return await asyncio.to_thread(_analyze_bytes, data, known_handle)
