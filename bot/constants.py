"""Tizim konstantalari — statuslar, rollar, callback prefikslari."""


class Role:
    MODERATOR = "moderator"      # faqat guruhda review qiladi
    ADMIN = "admin"              # admin panel, rassilka, statistika
    SUPERADMIN = "superadmin"    # + adminlarni boshqarish, g'oliblar

    ADMIN_PANEL = (ADMIN, SUPERADMIN)
    REVIEWERS = (MODERATOR, ADMIN, SUPERADMIN)


class ExpoStatus:
    DRAFT = "draft"
    ACTIVE = "active"
    FINISHED = "finished"   # reyting muzlatilgan, final tekshiruv ketyapti
    CLOSED = "closed"       # g'oliblar e'lon qilingan


class SubStatus:
    PENDING = "pending"             # moderatsiyada
    APPROVED = "approved"           # reytingda
    REJECTED = "rejected"           # rad etilgan
    CHANGES = "changes_requested"   # qayta ishlash kerak


class ReportStatus:
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class BCTarget:
    ALL = "all"
    PARTICIPANTS = "participants"   # faol expo ishtirokchilari
    APPROVED = "approved"           # videolari tasdiqlanganlar
    PENDING = "pending"             # arizasi kutilayotganlar
    TOP10 = "top10"
    SINGLE = "single"


class CB:
    """callback_data prefikslari (<=64 bayt bo'lishi shart)."""
    LANG = "lang"          # lang:uz
    AGREE = "agr"          # agr:yes / agr:no
    REVIEW = "rev"         # rev:<sub_id>:ok|no|ch
    REASON = "rsn"         # rsn:<sub_id>:<mode=rej|ch>:<code>
    RESUB = "resub"        # resub:<sub_id>
    KEEPLINK = "keepl"     # keepl:<sub_id>
    FINALCHK = "finchk"    # finchk:<expo_id>
    ADMIN = "adm"          # adm:menu,...
    BC = "bc"              # bc:tg:<target> | bc:send:<id> | bc:cancel
    PRIZES_DONE = "prizes_done"


# Reply-keyboard "bekor qilish" tugmasining barcha til variantlari —
# FSM matn kiritadigan handlerlarda bu matnni o'tkazib yuborish uchun.
CANCEL_TEXTS = frozenset({"❌ Bekor qilish", "❌ Отмена"})
