# Expo Challenge Bot 🏆

Har bir Expo doirasida o'tkaziladigan video challenge uchun Telegram bot:
ishtirokchilar Instagram Reels video + prosmotr skrinshotini yuboradi, moderatorlar
guruhda tasdiqlaydi, bot reyting yuritadi va yakunda g'oliblarni e'lon qiladi.

**Stack:** Python 3.12 · aiogram 3 · SQLAlchemy 2 (async) · PostgreSQL/SQLite · Alembic · Docker/fly.io

Reja va mantiqiy xulosalar: [`PLAN.md`](PLAN.md)

---

## ⚡ Tezstart (lokal)

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt     # testlar uchun: -r requirements-dev.txt
cp .env.example .env                # va to'ldiring
python -m bot.main                  # alembic migratsialari avtomatik yuritiladi
```

### BotFather
1. `/newbot` — token oling → `BOT_TOKEN` ga yozing.
2. `/setprivacy` → **Disable** (review guruhida reply-sabablarni o'qishi uchun).
3. `/setcommands`:
   ```
   start - Boshlash
   join - Challenge'ga qo'shilish
   stats - Statistika (admin)
   admin - Admin panel
   ```

### Review guruhini sozlash
1. Guruh yarating, botni unga qo'shing (xabar yuborish ruxsati bilan).
2. Guruh **supergroup** bo'lishi kerak. ID ni olish:
   guruhga istalgan xabar yozing → `https://t.me/<bot>` orqali emas, balki
   `@userinfobot` yoki `https://api.telegram.org/bot<TOKEN>/getUpdates` dan
   `"chat":{"id": -100xxxxxxxxxx}` ko'rinishidagi ID ni oling.
3. `.env` ga `REVIEW_GROUP_ID=-100xxxxxxxxxx` yozing.
4. Superadmin: o'zingizning TG ID ngizni `SUPERADMIN_IDS` ga yozing
   (ID ni @userinfobot'dan bilib oling).
5. Moderator qo'shish: `/addadmin <tg_id> moderator`

## 📦 Fly.io deploy

```bash
fly launch --no-deploy --name expo-challenge-bot
fly postgres create                      # yoki mavjudiga attach
fly postgres attach <pg-app-name>        # DATABASE_URL secret bo'ladi
fly secrets set BOT_TOKEN=... REVIEW_GROUP_ID=-100... SUPERADMIN_IDS=111,222
# ixtiyoriy: g'oliblar e'loni uchun kanal
fly secrets set ANNOUNCE_CHAT_ID=-100...
fly deploy                               # migratsiya release_command da yuritiladi
```

> Bir mashina (MemoryStorage FSM + bitta polling) — `min_machines_running = 1`.

## 🎮 Foydalanuvchi oqimi

1. `/start` → til → ism → telefon → Instagram → qoidalar → ✅ qabul
2. `🎥 Video yuborish` → Reels havola → ko'ruv soni → skrinshot → tasdiqlash
3. Moderator guruhda ✅/❌/✏️ tanlaydi
4. `🔄 Prosmotrni yangilash` — har safar yangi skrinshot moderatsiyadan o'tadi
5. `📊 Mening o'rning` — kimdan oldin/orqada ekanini ko'radi
6. Yakunda TOP-10 → final tekshiruv (`🏁`) → g'oliblar e'loni

## ✨ Qo'shimcha imkoniyatlar

- **🎲 Random sovg'a** (admin panel): asosiy g'oliblardan tashqari ishtirokchilar
  orasida CSPRNG (`secrets.SystemRandom`) bilan tanlov. Nomzodlar ro'yxati
  **sha256 xesh** bilan qayd etiladi (`audit_log`) — e'lon bilan birga tekshiruv
  kodi chiqadi, ".random adolatli"ning isboti.
- **⏰ Jadval rassilkasi**: rassilkani kelajak vaqtga (Toshkent) qo'yish —
  ichki scheduler har 30 s da tekshirib o'zi yuboradi; paneldan bekor qilish
  ham mumkin.
- **👥 Guruhda tezkor statistika**: review guruhida `/stats` va `/top`.
- **🕐 Vaqt zonasi**: admin kiritadigan barcha sanalar **Toshkent (UTC+5)** da
  qabul qilinadi, bazada UTC saqlanadi.

## 🖥 Web-admin panel

Telegram'dagi `/admin` panelidan tashqari, brauzerda ishlaydigan to'liq boshqaruv paneli ham bor:

```
https://<app-nomi>.fly.dev/admin
```

Kirish uchun `ADMIN_PASSWORD` secret/env o'rnatilishi shart (bo'sh bo'lsa panel butunlay o'chirilgan
bo'ladi — `503`). Fly'da:

```bash
fly secrets set ADMIN_PASSWORD='kuchli-parol'
```

Panel imkoniyatlari: dashboard statistikasi, Expo yaratish/faollashtirish/yakunlash, topshiriqlarni
qidirish/filtrlash va tasdiqlash/rad etish (skrinshot bilan), reyting, rassilka, CSV eksport.

## 🛠 Admin

| Buyruq | Kim | Nima qiladi |
|---|---|---|
| `/admin` | admin+ | panel: Expo, rassilka, statistika, eksport |
| `/stats` | admin+ | tezkor statistika |
| `/export` | admin+ | CSV (users / leaderboard / view history) |
| `/addadmin <id> <rol>` | superadmin | moderator/admin qo'shish |
| `/deladmin <id>` | superadmin | o'chirish |

## 🧪 Testlar

```bash
pip install -r requirements-dev.txt
pytest tests/ -q
```

## 🗂 Struktura

```
bot/
├── config.py        # env sozlamalar (pydantic-settings)
├── i18n.py          # uz/ru matnlar
├── constants.py     # statuslar, rollar, callback prefikslar
├── keyboards.py     # barcha klaviaturalar
├── states.py        # FSM holatlar
├── middlewares.py   # DB sessiya + user/role/lang
├── health.py        # /health (fly.io)
├── db/              # models, session, repo (barcha SQL), migrate
├── services/        # flags (anti-fraud), ranking, utils, context
└── handlers/        # start, submission, leaderboard, review, admin,
                     # broadcast, stats
```
