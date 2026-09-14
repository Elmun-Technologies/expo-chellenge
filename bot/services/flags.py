"""Anti-fraud: prosmotr yangilanishidagi shubhali belgilarni aniqlaydi."""
from datetime import datetime

FLAG_JUMP = "SUSPECT_JUMP"          # qisqa vaqtda keskin sakrash
FLAG_NEGATIVE = "NEGATIVE_DELTA"    # kamaygan — montaj yoki eski skrinshot
FLAG_ZERO_TIME = "ZERO_TIME"        # avvalgi tasdiq vaqti yo'q (g'ayrioddiy)
FLAG_OCR_MISMATCH = "OCR_VIEW_MISMATCH"    # kiritilgan son skrinshotdagidan farq qiladi
FLAG_ACCOUNT_MISMATCH = "ACCOUNT_MISMATCH"  # skrinshotdagi akkaunt registrdagidan farq qiladi


def ocr_flags(typed_views: int | None, ocr_views: int | None,
              registered_handle: str | None, detected_handle: str | None,
              pct_threshold: int = 5) -> list[str]:
    """OCR natijasiga ko'ra shubhali holatlarni belgilaydi.

    - Kiritilgan son skrinshotdan o'qilgan sondan `pct_threshold`% dan ko'proq
      farq qilsa → OCR_VIEW_MISMATCH.
    - Skrinshotdagi akkaunt registrdagi akkauntdan farq qilsa → ACCOUNT_MISMATCH.
    """
    flags: list[str] = []
    if ocr_views is not None and typed_views is not None and typed_views > 0:
        diff_pct = abs(ocr_views - typed_views) / typed_views * 100
        if diff_pct > pct_threshold:
            flags.append(FLAG_OCR_MISMATCH)
    if detected_handle and registered_handle and \
            detected_handle.lower() != registered_handle.lower():
        flags.append(FLAG_ACCOUNT_MISMATCH)
    return flags


def compute_flags(prev_views: int | None, new_views: int,
                  prev_at: datetime | None, now: datetime,
                  pct_threshold: int = 30, abs_threshold: int = 5000) -> list[str]:
    flags: list[str] = []
    if prev_views is None:
        return flags

    delta = new_views - prev_views
    if delta < 0:
        flags.append(FLAG_NEGATIVE)
        return flags  # keyingi tekshiruvlarga hojat yo'q

    if prev_at is None:
        # Birinchi tasdiq vaqti yo'q — o'zi shubhali holat
        if delta >= abs_threshold:
            flags.append(FLAG_ZERO_TIME)
        return flags

    seconds = max((now - prev_at).total_seconds(), 1)
    per_hour = delta * 3600.0 / seconds
    pct = (delta / prev_views * 100) if prev_views > 0 else (100.0 if delta > 0 else 0.0)

    if seconds <= 3600 and (pct >= pct_threshold or delta >= abs_threshold):
        flags.append(FLAG_JUMP)
    elif per_hour >= abs_threshold and pct >= pct_threshold:
        flags.append(FLAG_JUMP)

    return flags
