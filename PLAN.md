# Expo Challenge Bot — Reja va Arxitektura

> Maqsad: har bir Expo doirasida o'tkaziladigan video challenge uchun
> ishtirokchilarni qabul qilish, videolarini moderatsiyadan o'tkazish,
> prosmorlarni skrinshot asosida tasdiqlash, reyting yuritish va
> g'olibni HAQONIY aniqlash uchun Telegram bot.

---

## 1. Umumiy maqsad

- Tashkilotchilar yil davomida turli tematikadagi Expo lari o'tkazadi.
- Har bir Expo doirasida video challenge bo'ladi: ishtirokchilar o'z
  Instagram Reels videolarini joylashadi.
- **Eng ko'p tasdiqlangan prosmotr yig'gan video** iPhone va boshqa
  sovg'alarni oladi (g'olib = prosmotr bo'yicha, random yo'q).
- Bot qatnashmoqchi bo'lganlarni **filter** qiladi va moderate guruhiga
  yuboradi; maxsus jamoa ko'rib chiqadi.
- Bot orqali har bir foydalanuvchiga alohida va umumiy **rassilka**
  qilish mumkin.
- To'liq **statistika va analitika** admin panelda.

---

## 2. Rollar

| Rol | Kim | Imkoniyatlar |
|---|---|---|
| Foydalanuvchi | Ishtirokchi | Ro'yxatdan o'tish, video yuborish, prosmotr yangilash, reyting ko'rish |
| Moderator | Maxsus jamoa — **hay'at (review) guruhining har bir a'zosi** | Video+havolani tasdiqlash / rad etish, sabab yozish |
| Admin | Tashkilotchi jamoa | Expo yaratish, rassilka, statistika, challenge yakunlash |
| Superadmin | Texnik mas'ul | Adminlarni boshqarish, g'olibni e'lon qilish, tizim sozlamalari |

**Muhim:** Moderatorlar faqat guruhda ishlaydi (aloqa botda alohida
admin-panel ochish shart emas), Adminlar esa botdagi yashirin admin
buyruqlari orqali ishlaydi.

**Hay'at guruhi — avtomatik huquq:** review guruhiga kim a'zo bo'lsa,
o'shaning barchasi arizalarni tasdiqlashi/rad etishi mumkin — har bir
kishini alohida `/addadmin` qilish shart emas. Bot har tekshiruvda
Telegram'dan a'zolikni so'raydi (`getChatMember`, 60 sekundlik kesh
bilan); guruhdan chiqqan/chiqarilgan odam huquqni darhol yo'qotadi.
Bot guruhda admin bo'lishi kerak.

---

## 3. Foydalanuvchi oqimi (User Flow)

### 3.1 Ro'yxatdan o'tish
1. `/start` → til tanlash (o'zbek/rus).
2. To'liq ism-soat → telefon raqam (kontakt tugmasi orqali) →
   Instagram akkaunt nomi (`@nickname`).
3. Challenge qoidalari ekrani → **"Qabul qilaman"** tugmasi.
4. Tasdiqlangach → asosiy menyu.

### 3.2 Asosiy menyu
- 🎥 Video yuborish
- 📊 Mening o'rning
- 🏆 Reyting (Top-10)
- 📈 Mening statistikam
- ℹ️ Qoidalar

### 3.3 Video yuborish (Challenge'ga qo'shilish)
1. Foydalanuvchi Instagram **Reels havolasini** yuboradi.
   - Bot tekshiradi: `instagram.com/reel/...` formatidagi havola birorta
     boshqa ishtirokchida band emasmi (bir videoni ikki kishi yubora
     olmaydi).
2. Bot so'raydi: shu havoladagi **prosmorrlar soni skrinshot** i
   (ko'ruvlar soni va akkaunt nomi ko'ringan holda).
3. Bot so'raydi: bu video **o'z akkauntingizda** ekanini tasdiqlaysizmi?
4. Ma'lumotlar to'liq bo'lsa → status `KUTILMOQDA` → chiqarish guruhiga
   yuboriladi.
5. Moderator tekshiradi:
   - ✅ Tasdiqlasa → status `QABUL QILINDI`, foydalanuvchiga xabar
     boradi, reytingga kiradi.
   - ❌ Rad etsa → sabab tanlanadi (tugmalar orqali) → foydalanuvchiga
     sabab yozilgan xabar yuboriladi, **qayta yuborish** imkoni beriladi.

### 3.4 Prosmortlarni yangilash (challenge davomida)
- Prosmotrlar o'sgani sari foydalanuvchi "🔄 Yangilash" orqali yangi
  skrinshot yuboradi → yana moderatsiyadan o'tadi.
- Eski qiymatlar o'chirilmaydi — **tarix jadvalida** saqlanadi
  (anti-fraud uchun).
- Taxminiy o'sishdan keskin katta farq bo'lsa (soatiga +N%), tizim
  moderatorga avtomatik **belgi (flag)** qo'yadi.

---

## 4. Video holatlari mashinasi (Lifecycle)

```
[Foydalanuvchi yubordi]
        │
        ▼
   KUTILMOQDA ────────────────► review guruhiga tushadi
        │
        ├─ ✅ ──► TASDIQLANGAN ──► reytingda ko'rinadi
        │
        ├─ ❌ ──► RAD ETILGAN ──► foydalanuvchiga sabab + qayta
        │                         yuborish tugmasi
        └─ ✏️ ──► QAYTA ISHLASH KERAK ──► sabab yoziladi
                  (masalan: skrinshot xira, akkaunt nomi ko'rinmayapti)

[Challenge yakunda]
        │
        ▼
  FINAL TEKSHIRUV (faqat TOP-10) ──► yangi skrinshot / ekran yozuvi
        │                              24 soat ichida yuborish shart
        ▼
  YAKUNIY TASDIQ ──► g'olib e'lon qilinadi
```

---

## 5. Anti-fraud (Haqoniylik) qoidalari

Challenge "haqoniy" bo'lishi uchun ko'p qatlamli himoya:

1. **Havola unikalligi** — bir video faqat bir ishtirokchidda.
2. **Instagram nomi mosligi** — ro'yxatdagi akkaunt bilan skrinshotdagi
   akkaunt nomi moderator tomonidan solishtiriladi.
3. **Prosmotr tarixi** — har bir tasdiqlangan skrinshot DB'da
   saqlanadi; keskin sakrashlarga avtomatik flag:
   - 1 soatda o'sish > 30% va > 5000 ko'rish → `SUSPECT_JUMP`
   - Prosmotr oldingi tasdiqlangan qiymatdan *kamaygan* bo'lsa
     → avtomatik rad etish (skrinshot eski yoki montaj).
4. **Superedit-an'anavi belgilar** — skrinshot juda kichik o'lcham,
   notikolar kesilgan bo'lsa moderatorga maxsus ogohlantirish yozuvi.
5. **Final tekshiruv** — yakundan keyin TOP-10 o'rniga kirganlar
   **24 soat ichida** ekran yozuvini (Reels sahifasidan views ko'rsatib)
   yuborishi shart. Yubormagan → diskvalifikatsiya.
6. **Audit log** — moderator/adminlarning BARCHA harakatlari
   (tasdiqladi, rad etdi, rassilka qildi...) `audit_log` jadvaliga
   yoziladi. Shubhali vaziyatda hammasini qayta ko'rib chiqish mumkin.
7. **Challenge vaqti** — `end_at` dan keyin yangi video va yangi
   skrinshot qabul qilinmaydi.

---

## 6. Reyting (Leaderboard)

- **Top-10**: 1️⃣-🔟 o'rin, ism + Instagram + tasdiqlangan prosmotr.
- **Mening o'rnim**:
  ```
  Sizning o'rningiz: #47
  Sizning prosmotringiz: 12 500
  ─ Jami ishtirokchi: 234 ─
  👆 #46 · @oldindagi_user — 13 100
  🫵 #47 · SIZ — 12 500
  👇 #48 · @orqadagi_user — 12 300
  ```
- Foydalanuvchi shundoq qayerda turganini va kimdan qancha ortda
  ekanligini biladi.
- Maxfiylik: faqat TOP-10 to'liq ko'rinadi, qolganlar o'z o'rni va
  yaqin qo'shnilarni ko'radi (nomlar qisman yashiriladi: `@ali***ov`).

---

## 7. G'olibni aniqlash

Tanlangan logika: **faqat prosmotr bo'yicha**.

1. Admin "⏳ Challenge'ni yakunlash" tugmasini bosadi.
2. Reyting muzlatiladi, yangi yuborishlar yopiladi.
3. TOP-10 ga **final tekshiruv** so'rovi ketadi (24 soat).
4. Admin final natijalarni kiritadi/tasdiqlaydi.
5. Bot chempionatlarni e'lon qiladi:
   - ishtirokchilarga yakkaxon xabar,
   - asosiy guruh/kanalda e'lon (post),
   - g'oliblarga alohida tabrik + keyingi qadamlar (elon qilish,
     mukofot topshirish uchun kontakti).

> [!NOTE]
> **Amalga oshirildi** ✅ — asosiy g'olib prosmotr bo'yicha + qo'shimcha
> **🎲 Random sovg'a moduli** alohida (asosiy top-N chiqarib tashlangan
> ishtirokchilar orasidan, sha256-xesh bilan shaffof).

---

## 8. Rassilka (Broadcast)

### Kim qila oladi
Admin va Superadmin (`/broadcast` buyrug'i).

### Vaughli-variantlar
| Birlik | Tavsif |
|---|---|
| ⭐ Barcha foydalanuvchilar | Botni bir marta ham ishlatgan hamma |
| 🎪 Muayyan Expo ishtirokchilari | Tanlangan Expo'ga qo'shilganlar |
| ✅ Faqat tasdiqlanganlar | Videolari qabul qilinganlar |
| ⏳ Kutilayotganlar | Moderatsiyada turganlar |
| 🏆 TOP-N / g'oliblar | Reytingdagi tanlanganlar |
| 🎯 Bitta foydalanuvchi | ID yoki `@username` orqali — **alohida** aloqa |

### Jarayon
1. Admin xabarni tayyorlaydi (matn + rasm/video/qo'llanma).
2. **Ko'rib chiqish (preview)** — xabar adminning o'ziga keladi.
3. Tasdiqlash → navbatga qo'yiladi.
4. Telegram limiti (≈25-30 msg/s) ga rioya qilinib, xatoliklar
   (`bot blokland`) alohida hisoblanadi.
5. Natila: yuborildi / yetib bormadi / bloklash — real vaqt statistikasi.

---

## 9. Statistika va Analitika

### Har bir Expo uchun
- Ro'yxatdan o'tganlar → video yuborganlar → tasdiqlanganlar **funnel**.
- Kutilayotgan / tasdiqlangan / rad etilgan nisbatlari.
- Kunlik ro'yxatdan o'tish dinamikasi (grafik ko'rinishda PNG yaratish —
  `matplotlib` yoki shunchaki matn jadvalida).
- Umumiy prosmotrlar yig'indisi, o'rtacha prosmotr.
- Eng faol kun/vaqt.

### Umumiy bot uchun
- Jami foydalanuvchilar, yangi foydalanuvchilar (kunlik/haftalik).
- Botni bloklagan foydalanuvchilar soni.
- Rassilka natijalari tarixi.

### Format
- `/stats` — tezkor matn ko'rinishi.
- `/export` — CSV/Excel fayl (`pandas` bilan).

---

## 10. Ma'lumotlar bazasi (PostgreSQL)

```
users
 ├── id, tg_id (unique), username, full_name, phone
 ├── instagram_handle, language, is_blocked
 └── created_at, last_active_at

expos
 ├── id, title, description, rules_text
 ├── prizes (jsonb: [{place: 1, prize: "iPhone 16"}])
 ├── start_at, end_at, status (draft/active/finished)
 └── created_by

participants
 ├── id, user_id → users, expo_id → expos
 ├── agreed_rules (bool), joined_at
 └── UNIQUE(user_id, expo_id)

submissions
 ├── id, participant_id, video_url (unique per expo)
 ├── status (pending/approved/rejected/changes_requested)
 ├── reject_reason, reviewed_by, reviewed_at
 └── submitted_at

view_reports          ← prosmotr TARIXI shu yerda
 ├── id, submission_id, screenshot_file_id
 ├── views_count, status (pending/approved/rejected)
 ├── flags (jsonb: ["SUSPECT_JUMP", ...])
 ├── reviewed_by, reviewed_at, submitted_at

broadcasts
 ├── id, admin_id, target_type, expo_id
 ├── payload (jsonb: matn/file_id/knokki)
 ├── status (draft/sending/done), sent_count, failed_count
 └── created_at, finished_at

broadcast_logs
 ├── id, broadcast_id, user_id, status (sent/failed), error

admins
 ├── id, tg_id (unique), role (admin/moderator/superadmin)

audit_log
 ├── id, actor_id, action, payload (jsonb), created_at
```

---

## 11. Texnologiyalar va papka strukturasi

| Qatlam | Tanlov |
|---|---|
| Bot framework | **aiogram 3.x** |
| Baza | **PostgreSQL** (Fly.io Managed Postgres) |
| ORM / migratsiya | SQLAlchemy 2.0 (async) + Alembic |
| Rassilka navbati | asyncio queue + per-message delay (30 msg/s) |
| Grafiklar | matplotlib (PNG → Telegram) |
| Deploy | Docker → **fly.io** |
| Health-check | aiohttp kichik endpoint (`/health`) |

```
expo-chellenge/
├── bot/
│   ├── main.py              # entry point (long polling)
│   ├── config.py            # env o'zgaruvchilari
│   ├── handlers/
│   │   ├── start.py         # /start, ro'yxatdan o'tish
│   │   ├── submission.py    # video + skrinshot yuborish
│   │   ├── leaderboard.py   # reyting, mening o'rningim
│   │   └── admin/
│   │       ├── review.py    # guruhda review tugmalari
│   │       ├── broadcast.py
│   │       ├── stats.py
│   │       └── expo_mgmt.py # expo yaratish/yakunlash/g'olib
│   ├── keyboards/           # inline tugmalar
│   ├── states/              # FSM holatlari
│   ├── middlewares/         # i18n, auth, throttling
│   ├── services/
│   │   ├── views.py         # prosmotr tariхи, flag logikasi
│   │   ├── ranking.py       # reyting hisoblash
│   │   └── broadcast.py     # rassilka worker
│   └── db/
│       ├── models.py
│       └── repo.py          # CRUD so'rovlar
├── alembic/                 # migratsiyalar
├── Dockerfile
├── fly.toml
├── requirements.txt
└── README.md
```

---

## 12. Fly.io deploy rejasi

1. `fly launch` — Dockerfile orqali build.
2. `fly postgres create` → `fly postgres attach` → `DATABASE_URL`
   avtomatik secret bo'ladi.
3. Kerakli **secret** lar:
   - `BOT_TOKEN` — BotFather'dan
   - `REVIEW_GROUP_ID` — moderatsiya guruhining ID si
   - `SUPERADMIN_IDS` — dastlabki superadminlar ro'yxati
4. Bot **long polling** rejimida ishlaydi (ochiq port shart emas).
   Lekin tiny `/health` HTTP endpoint qo'yamiz, chunki fly.io health
   check bindini va mashinani uyg'oq tutishini `fly.toml` da
   belgilaymiz:
   ```toml
   [http_service]
     internal_port = 8080
     auto_stop_machines = false
     min_machines_running = 1
   ```
5. Alembic migratsiyalar `release_command` orqali avtomatik yuritariladi:
   ```toml
   [deploy]
     release_command = "alembic upgrade head"
   ```

---

## 13. Yol xaritasi (bosqichlar)

| Bosqich | Ish | Natija |
|---|---|---|
| 1 | Loyia skeleti: config, DB, models, `/start` | Bot javob beradi |
| 2 | Ro'yxatdan o'tish + qoidalar + FSM | Ishtirokchi tayyor |
| 3 | Video+skrinshot qabul qilish → guruhga yuborish | Moderatsiya ishlaydi |
| 4 | Tasdiqlash/rad etish tugmalari + foydalanuvchi xabari | Filter yopildi |
| 5 | Prosmotr yangilash + tarix + anti-fraud flaglar | Haqoniylik |
| 6 | Reyting + "Mening o'rningim" | Leaderboard |
| 7 | Rassilka (barcha/saralangan/aloеxtra) | Aloqa kanali |
| 8 | Challenge yakunlash + final tekshiruv + g'olib | Natija mexanizmi |
| 9 | Statistika + eksport | Analitika |
| 10 | Fly.io deploy + migratsiya + sinonim-testlar | Prodanshn |

---

## 14. Qabul qilingan qarorlar

1. ✅ **Expo'lar ketma-ket** — bir vaqtda FAQAT bitta faol expo.
   Yangisini faollashtirishdan oldin joriy exponi yakunlash shart.
2. Skrinshotda prosmotr + akkaunt nomi ko'rinishi shart (moderator
   solishtiradi).
3. Sovg'alar ro'yxatini admin har Expo uchun o'zi kiritadi
   (nechta o'rin bo'lsa).
4. Telefon tasdig'i kifoya (passport kerak emas).
5. ✅ **Rassilka jadvali (scheduled)** ham amalga oshirildi — Toshkent
   vaqtida belgilab qo'yiladi, ichki scheduler o'zi yuboradi.
6. Bir ishtirokchida **bitta faol video** (prosmotrlar esa cheksiz
   yangilanadi) — adolat uchun.
7. ✅ **Guruh ichida tezkor statistika** — review guruhida `/stats` va
   `/top` buyruqlari (guruh a'zolari — hay'at — ham ishlatadi).
8. ✅ **Vaqt zonasi** — hamma sanalar Toshkent (UTC+5) da kiritiladi va
   ko'rsatiladi, bazada UTC saqlanadi.

---

*Ushbu reja tasdiqlangandan so'ng bosqichma-bosqich quramiz.*
