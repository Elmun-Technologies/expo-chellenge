"""Formatlash va parslash utilitalari (aiogram'dan mustaqil — test uchun)."""
import re
from datetime import datetime, timedelta

# Baza UTC'da saqlanadi; foydalanuvchi Toshkent vaqtida (UTC+5) ko'radi/kiritadi
TASHKENT = timedelta(hours=5)


def tash_to_utc(dt: datetime) -> datetime:
    """Toshkent naive vaqtni UTC naive'ga o'tkazish."""
    return dt - TASHKENT


def utc_to_tash(dt: datetime | None) -> datetime | None:
    return dt + TASHKENT if dt is not None else None


REELS_LINK = re.compile(
    r"^https?://(www\.)?instagram\.com/(reel|reels|p)/[A-Za-z0-9_-]{5,20}/?(\?.*)?$",
    re.IGNORECASE,
)
INSTA_HANDLE = re.compile(r"^[A-Za-z0-9._]{1,30}$")
PHONE = re.compile(r"^\+?\d{9,15}$")

DATE_FORMATS = ("%d.%m.%Y %H:%M", "%d.%m.%Y", "%Y-%m-%d %H:%M", "%Y-%m-%d")


def is_reels_link(text: str) -> bool:
    return bool(REELS_LINK.match(text.strip()))


def normalize_insta(text: str) -> str | None:
    """'@User_Name' -> 'user_name' (validatsiya bilan)."""
    h = text.strip().lstrip("@").lower()
    return h if INSTA_HANDLE.match(h) else None


def is_valid_phone(text: str) -> bool:
    return bool(PHONE.match(text.strip()))


# ---------------- son (ko'ruvlar) parslash ----------------

# Ko'paytuvchi qo'shimchalar: "12,5K", "1,2M", "12,5 ming", "1,2 млн", "12.5K"
_K_SUFFIX = re.compile(
    r"\b(?:k|к|минг|ming|minglab|thousand|тыс)[а-яё]*\b", re.IGNORECASE)
_M_SUFFIX = re.compile(
    r"\b(?:m|млн|mln|million|milliard|mlrd)\b", re.IGNORECASE)
# Son ifodasi: "12 500" / "12,500" / "12.500" / "12,5" / "12.5" / "12500"
_NUM_RE = re.compile(r"\d{1,3}(?:[ .,]\d{3})+|\d+(?:[.,]\d+)?")

# Ko'ruvlar bilan yonma-yon keladigan so'zlar (OCR matni uchun)
_VIEW_LABEL = re.compile(
    r"просмотр[а-яё]*|views?|ko['‘’`]?rish(?:lar)?|korish(?:lar)?|к[ўу]риш(?:лар)?",
    re.IGNORECASE,
)


def _suffix_multiplier(text: str) -> int:
    if _M_SUFFIX.search(text):
        return 1_000_000
    if _K_SUFFIX.search(text):
        return 1_000
    # token oxiriga yopishgan harf: "12.5K" (biz uni "12.5 K" qilib beramiz)
    if re.search(r"\d\s*[mM](?![a-zA-Zа-яё])", text):
        return 1_000_000
    if re.search(r"\d\s*[kK](?![a-zA-Zа-яё])", text):
        return 1_000
    return 1


def _to_float(raw: str) -> float | None:
    """'12 500' | '12,500' | '12.500' | '12,5' | '12.5' -> float."""
    raw = raw.strip()
    if not raw:
        return None
    if "," in raw and "." in raw:
        if raw.rfind(",") > raw.rfind("."):
            raw = raw.replace(".", "").replace(",", ".")
        else:
            raw = raw.replace(",", "")
    elif "," in raw:
        parts = raw.split(",")
        if len(parts) > 2 or len(parts[1]) == 3:
            raw = raw.replace(",", "")
        else:
            raw = raw.replace(",", ".")
    elif "." in raw:
        parts = raw.split(".")
        if len(parts) > 2 or len(parts[1]) == 3:
            raw = raw.replace(".", "")
    raw = raw.replace(" ", "")
    try:
        return float(raw)
    except ValueError:
        return None


def _iter_numbers(text: str):
    """Matndan barcha sonlarni (raw, value, start) sifatida chiqaradi."""
    for m in _NUM_RE.finditer(text):
        raw = m.group(0)
        tail = text[m.end():m.end() + 10]
        mult = _suffix_multiplier(raw + " " + tail)
        v = _to_float(raw)
        if v is None:
            continue
        v *= mult
        if 0 < v < 1e13:
            yield raw, v, m.start()


def _best_number(nums) -> int | None:
    if not nums:
        return None
    # eng ko'p raqamli sonni tanlaymiz; teng bo'lsa kattasini
    nums.sort(key=lambda x: (sum(c.isdigit() for c in x[0]), x[1]), reverse=True)
    return int(round(nums[0][1]))


def parse_views(text: str) -> int | None:
    """Foydalanuvchi yozgan sonni o'qiydi:
    '12 500' / '12,500' / '12.5K' / '1,2M' / '12,5 ming' -> 12500 va h.k."""
    if not text:
        return None
    return _best_number(list(_iter_numbers(text)))


def parse_views_from_text(text: str) -> int | None:
    """OCR matnidan ko'ruvlar sonini aniqlaydi.

    Afzallik tartibi:
    1) «views/просмотров/ko'rishlar» so'zi yonidagi son;
    2) faqat sondan iborat satr (katta raqam odatda shunday keladi);
    3) eng katta son.
    """
    if not text:
        return None
    # 1) label yonidagi son
    for lm in _VIEW_LABEL.finditer(text):
        lo = max(0, lm.start() - 25)
        hi = min(len(text), lm.end() + 25)
        for _, v, _pos in _iter_numbers(text[lo:hi]):
            return int(round(v))
    # 2) faqat sondan iborat satrlar
    for line in text.splitlines():
        if _is_pure_number_line(line):
            nums = list(_iter_numbers(line))
            if nums:
                return int(round(max(v for _, v, _ in nums)))
    # 3) eng katta son
    nums = list(_iter_numbers(text))
    if not nums:
        return None
    return int(round(max(v for _, v, _ in nums)))


_HANDLE_RE = re.compile(r"@([A-Za-z0-9._]{1,30})")


def _is_pure_number_line(line: str) -> bool:
    """Satr faqat sondan (K/M/минг/млн bilan) iboratmi?"""
    s = line.strip()
    if not s:
        return False
    s = re.sub(r"(?:минг|ming|minglab|млн|mln|million|thousand|тыс)",
               " ", s, flags=re.IGNORECASE)
    s = re.sub(r"[0-9.,\s]", "", s)
    s = re.sub(r"[kKmM]", "", s)
    return s.strip() == ""


def _handle_candidates(text: str):
    """Matndagi har bir '@' dan keyingi nomzodlarni chiqaradi.

    OCR ko'pincha '_' (tagchiziq)ni bo'shliq deb o'qiydi (`alisher_nur` →
    `alisher nur`), shuning uchun birinchi so'z bilan birga dastlabki ikki
    so'zning qo'shilganini ham nomzod qilib beramiz.
    """
    for line in text.splitlines():
        for m in re.finditer(r"@", line):
            words = line[m.end():].split()
            if not words:
                continue
            yield words[0].lower()
            if len(words) >= 2:
                yield (words[0] + words[1]).lower()


def detect_handle(text: str, known_handle: str | None = None) -> str | None:
    """Matndan Instagram akkaunt nomini topadi (registrdagi nom afzal).

    Taqqoslash tagchiziq/bo'shliq farqiga chidamli — OCR xatosi bo'lsa ham
    registrdagi to'g'ri nom qaytariladi.
    """
    if not text:
        return None
    known = known_handle.lower() if known_handle else None
    known_compact = re.sub(r"[^a-z0-9]", "", known) if known else None

    if known:
        for cand in _handle_candidates(text):
            cand = cand.strip(".,;:")
            if cand == known:
                return known
            if known_compact and \
                    re.sub(r"[^a-z0-9]", "", cand) == known_compact:
                return known
        # @ belgisisiz yozilgan registrdagi nom
        if re.search(rf"(?<![@\w]){re.escape(known)}(?![\w])", text, re.IGNORECASE):
            return known

    # moslik topilmasa — matndagi birinchi @handle
    m = _HANDLE_RE.search(text)
    if m:
        return m.group(1).lower()
    return None


def parse_date(text: str) -> datetime | None:
    text = text.strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    return None


def fmt_int(n: int) -> str:
    return f"{n:,}".replace(",", " ")


def fmt_dt(dt: datetime | None) -> str:
    """Toshkent vaqtida ko'rsatish."""
    t = utc_to_tash(dt)
    return t.strftime("%d.%m.%Y %H:%M") if t else "—"


def mask_handle(handle: str | None) -> str:
    """Maxfiylik: '@alisher_nur' -> '@alis***'"""
    if not handle:
        return "—"
    h = handle.lstrip("@")
    visible = h[:4] if len(h) > 4 else h
    return f"@{visible}***"
