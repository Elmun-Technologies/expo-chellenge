"""Anti-fraud: prosmotr yangilanishidagi shubhali belgilarni aniqlaydi."""
from datetime import datetime

FLAG_JUMP = "SUSPECT_JUMP"          # qisqa vaqtda keskin sakrash
FLAG_NEGATIVE = "NEGATIVE_DELTA"    # kamaygan — montaj yoki eski skrinshot
FLAG_ZERO_TIME = "ZERO_TIME"        # avvalgi tasdiq vaqti yo'q (g'ayrioddiy)


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
