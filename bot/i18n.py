"""Oddiy i18n: TEXTS[lang][key] -> matn. Ru tilida topilmasa uz'ga qaytadi."""

TEXTS: dict[str, dict[str, str]] = {
    "uz": {
        # ---- start / ro'yxatdan o'tish ----
        "welcome": (
            "👋 Assalomu alaykum! <b>Expo Video Challenge</b> botiga xush kelibsiz.\n\n"
            "Bu yerda siz o'z Instagram Reels videongiz bilan challenge'da qatnashasiz: "
            "eng ko'p tasdiqlangan ko'ruv yig'gan ishtirokchi g'olib bo'ladi. 🏆"
        ),
        "ask_lang": "Tilni tanlang / Выберите язык:",
        "ask_name": "Ism va familiyangizni yozing (toliq):",
        "ask_phone": "📱 Telefon raqamingizni tugma orqali yuboring yoki yozing (+998...):",
        "btn_share_contact": "📱 Kontaktni yuborish",
        "ask_insta": "Endi Instagram akkauntingiz nomini yuboring (masalan: <code>@username</code>).\n\n⚠️ Videoni aynan shu akkauntga joylaysiz — moderatorlar skrinshot bilan solishtiradi.",
        "invalid_insta": "❌ Instagram nomi noto'g'ri. Faqat lotin harflari, raqam, nuqta va pastki chiziq. Qayta yuboring:",
        "invalid_phone": "❌ Telefon raqam noto'g'ri ko'rinmoqda. Qayta yuboring:",
        "rules_title": "📜 <b>Challenge qoidalari</b>\n\n{rules}",
        "btn_agree": "✅ Qabul qilaman",
        "btn_decline": "❌ Rad etaman",
        "declined": "Qoidalarni qabul qilmasangiz challenge'da qatnasha olmaysiz. /start",
        "reg_done": "🎉 Rahmat {name}! Challenge'ga muvaffaqiyatli qo'shildingiz.\nEndi videongizni yuborishingiz mumkin 👇",
        "profile_done_no_expo": "✅ Profilingiz saqlandi. Hozircha faol challenge yo'q — boshlanganda xabar beramiz!",
        "err_generic": "⚠️ Xatolik yuz berdi, qayta urinib ko'ring yoki /start bosing.",

        # ---- menyu ----
        "btn_send_video": "🎥 Video yuborish",
        "btn_update_views": "🔄 Prosmotrni yangilash",
        "btn_my_rank": "📊 Mening o'rning",
        "btn_top": "🏆 Top-10",
        "btn_my_stats": "📈 Mening statistikam",
        "btn_rules": "ℹ️ Qoidalar",
        "btn_join": "🎯 Challenge'ga qo'shilish",
        "btn_admin": "⚙️ Admin panel",
        "btn_cancel": "❌ Bekor qilish",
        "menu_hint": "Quyidagi menyudan tanlang 👇",
        "no_active_expo": "😴 Hozircha faol challenge yo'q. Yangi challenge boshlanganda sizga xabar yuboramiz!",
        "not_participant": "Avval challenge'ga qo'shilishingiz kerak:",
        "expo_window": "⏳ Challenge hozir faol emas.\nBoshlanish: {start}\nTugash: {end}",

        # ---- video yuborish ----
        "ask_link": "🔗 Instagram Reels videongiz havolasini yuboring:\n(masalan: https://instagram.com/reel/...)",
        "invalid_link": "❌ Bu Instagram Reels havolasi emas. Qayta yuboring (instagram.com/reel/... ko'rinishida bo'lsin):",
        "link_taken": "❌ Bu video allaqachon boshqa ishtirokchi tomonidan yuborilgan. Faqat o'z videongizni yuboring!",
        "ask_views": "👁 Hozirda videoda nechta ko'ruv bor? Faqat raqam yozing (masalan: 12500):",
        "invalid_views": "❌ Son kiriting. Masalan: 12500",
        "ask_screen": "📸 Endi ko'ruvlar soni aniq ko'ringan <b>skrinshot</b>ni yuboring.\n\nSkrinshotda ko'rinib turishi shart:\n• ko'ruvlar soni\n• akkaunt nomingiz",
        "need_photo": "❌ Bu rasm emas. Skrinshotni rasm sifatida yuboring:",
        "btn_keep_link": "⤵️ Oldingi havolani olish",
        "confirm_block": (
            "🔎 <b>Tekshirib chiqing:</b>\n\n"
            "🔗 Havola: {url}\n👁 Ko'ruvlar: {views}\n📸 Skrinshot: ✅\n\n"
            "Hammasi to'g'rimi?"
        ),
        "btn_confirm": "✅ Tasdiqlash, yuborish",
        "cancelled": "❌ Bekor qilindi.",
        "submitted": "⏳ Arizangiz qabul qilindi! Moderatorlar tekshirishidan keyin natija haqida xabar beramiz.\nAriza raqami: <b>#{sub_id}</b>",
        "already_pending": "⏳ Sizda allaqachon tekshiruvda turgan ariza bor (#{sub_id}). Natijasini kuting.",
        "have_video": "🎥 Sizda allaqachon tasdiqlangan video bor (#{sub_id}). Ko'ruvlarni ko'paytirish uchun «🔄 Prosmotrni yangilash» tugmasidan foydalaning.",
        "update_ask_views": "🔄 Hozirgi tasdiqlangan ko'ruvlaringiz: <b>{current}</b>.\nYangi qiymatni yozing (kam bo'lishi mumkin emas):",
        "views_too_low": "❌ Yangi qiymat ({new}) hozirgi tasdiqlangan qiymatdan ({current}) kam bo'lishi mumkin emas. Bu — montaj gumoniga tushadi. Haqiqiy yangi sonni yozing:",
        "update_submitted": "⏳ Yangi ko'ruvlar skrinshot bilan moderatsiyaga yuborildi. Tasdiqlangach reyting yangilanadi.",
        "report_pending_exists": "⏳ Oldingi yangilash hali ko'rib chiqilmagan. Kuting.",
        "no_submission": "Sizda hali video yo'q. Avval «🎥 Video yuborish» orqali qatnashing.",
        "resub_notice": "Arizangizni qayta yuboring — havolani ham almashtirishingiz mumkin.",

        # ---- reyting ----
        "top_title": "🏆 <b>{expo}</b> — Top-10",
        "top_empty": "Hali hech kim tasdiqlanmagan.",
        "top_line": "{medal} <b>{name}</b> ({insta}) — 👁 {views}\n",
        "top_frozen": "\n🏁 Challenge yakunlangan, reyting muzlatilgan.",
        "rank_block": (
            "📊 <b>Sizning o'rningiz: #{rank}</b> / {total}\n"
            "👁 Sizning ko'ruvlaringiz: <b>{views}</b>\n\n{neighbors}"
        ),
        "rank_above": "👆 #{r} · {name} — {views} <i>(sizdan +{diff})</i>\n",
        "rank_you": "🫵 #{r} · <b>SIZ</b> — {views}\n",
        "rank_below": "👇 #{r} · {name} — {views} <i>(-{diff} ortda)</i>\n",
        "rank_last": "Siz reytingning oxiridasiz. 💪",
        "rank_first": "🥇 Siz birinchi o'rindasiz! Orqada: #{r} · {name} (-{diff}).",
        "no_rank": "Faol bo'lish uchun videongiz moderator tasdig'idan o'tishi kerak.",
        "my_stats": "📈 <b>Sizning ko'ruvlar tarixi:</b>\n{lines}",
        "my_stats_empty": "Hali tasdiqlangan ko'ruvlar yo'q.",
        "my_stats_line": "• {date} — 👁 {views}\n",

        # ---- review (moderator guruhida) ----
        "rev_new": "🆕 <b>YANGI ARIZA</b> (sub #{sub_id})",
        "rev_update": "🔄 <b>YANGILASH</b> (sub #{sub_id}): {old} → <b>{new}</b> ({sign}{pct}%)",
        "rev_final": "🏁 <b>FINAL TEKSHIRUV</b> (sub #{sub_id})",
        "rev_flags": "\n⚠️ FLAGS: {flags}",
        "rev_body": "👤 {name} — {insta}\n📱 {phone}\n🔗 <a href=\"{url}\">Video havolasi</a>\n👁 Kiritilgan ko'ruvlar: <b>{views}</b>",
        "btn_approve": "✅ Tasdiqlash",
        "btn_reject": "❌ Rad etish",
        "btn_changes": "✏️ Qayta ishlash",
        "rev_approved_mark": "\n\n✅ <b>TASDIQLANGAN</b> — {mod}",
        "rev_rejected_mark": "\n\n❌ <b>RAD ETILGAN</b> — {mod}. Sabab: {reason}",
        "rev_changes_mark": "\n\n✏️ <b>QAYTA ISHLASHGA</b> — {mod}. Sabab: {reason}",
        "rev_already": "Bu ariza allaqachon ko'rilgan.",
        "no_rights": "⛔ Sizda ko'rib chiqish huquqi yo'q — bu hay'at guruhining a'zosi bo'lishingiz kerak.",
        "choose_reason": "Sababni tanlang:",
        "rsn_wrong_screen": "Skrinshot xira/mos emas",
        "rsn_bad_link": "Havola ochilmayapti",
        "rsn_not_own": "Video sizniki emas",
        "rsn_edited": "Montaj/tahrir gumoni",
        "rsn_other": "Boshqa sabab (yoziladi)",
        "custom_reason_prompt": "✏️ Sababni yozing — shu xabarga <b>reply</b> qilib javob bering:",

        # ---- foydalanuvchi xabarnomalari ----
        "ntf_approved": "✅ Tabriklaymiz! Videongiz tasdiqlandi va reytingga kiritildi! 🎉\nKo'ruvlar: <b>{views}</b>. Endi ularni oshirib boring!",
        "ntf_rejected": "❌ Afsuski, arizangiz rad etildi.\nSabab: <b>{reason}</b>\n\nIstalgan vaqtda qayta yuborishingiz mumkin 👇",
        "ntf_changes": "✏️ Arizangizga o'zgartirish kiritish kerak.\nSabab: <b>{reason}</b>\n\nQayta yuboring 👇",
        "btn_resubmit": "🔄 Qayta yuborish",
        "ntf_update_approved": "✅ Ko'ruvlaringiz yangilandi: <b>{views}</b>. Reytingni tekshirib qo'ying!",
        "ntf_update_rejected": "❌ Ko'ruvlarni yangilash rad etildi.\nSabab: <b>{reason}</b>",

        # ---- final / g'olib ----
        "final_check_req": (
            "🏁 <b>Challenge yakunlandi!</b> Siz TOP-10 dasiz — g'olib bo'lish uchun "
            "{hours} soat ichida <b>final tekshiruv</b>ni yuboring: ko'ruvlar ko'ringan "
            "<b>yangi skrinshot</b> yoki ekran yozuvi kerak."
        ),
        "btn_final_send": "🏁 Final tekshiruvni yuborish",
        "final_late": "⏰ Final tekshiruv muddati o'tgan.",
        "winner_announce": "🏆 <b>{expo}</b> — challenge g'oliblari!\n\n{winners}\n\nTabriklaymiz! 🎉🎉🎉",
        "winner_line": "{medal} {name} ({insta}) — 👁 {views} — 🎁 {prize}\n",
        "winner_pm": "🥳 <b>Tabriklaymiz! Siz {place}-o'rin oldingiz!</b>\n🎁 Sovg'a: <b>{prize}</b>\n\nTashkilotchilar tez orada bog'lanishadi.",
        "results_frozen": "🏁 Challenge yakunlandi. Natijalar tez orada e'lon qilinadi!",

        # ---- admin ----
        "admin_denied": "⛔ Bu bo'lim faqat adminlar uchun.",
        "admin_menu": "⚙️ <b>Admin panel</b>",
        "abtn_new_expo": "🆕 Yangi Expo",
        "abtn_list": "📋 Expo'lar ro'yxati",
        "abtn_broadcast": "📢 Rassilka",
        "abtn_stats": "📊 Statistika",
        "abtn_export": "📤 Eksport (CSV)",
        "abtn_winners": "🏆 G'oliblarni e'lon qilish",
        "abtn_finish": "⏹ Challenge'ni yakunlash",
        "abtn_users": "👥 Adminlarni boshqarish",
        "expo_ask_title": "🆕 Yangi Expo. Nomini yozing:",
        "expo_ask_desc": "Qisqa tavsif yozing:",
        "expo_ask_rules": "Qoidalar matnini yozing (ro'yxatdan o'tishda ko'rinadi):",
        "expo_ask_prizes": "🎁 Sovg'alar ro'yxatini birma-bir yozing (masalan: <code>1 — iPhone 16</code>).\nBitgach «✅ Tayyor» ni bosing.",
        "expo_prizes_done": "✅ Tayyor",
        "expo_ask_start": "Boshlanish sanasini yozing (Toshkent vaqti, masalan: <code>01.10.2026 10:00</code>):",
        "expo_ask_end": "Tugash sanasini yozing:",
        "bad_date": "❌ Sana noto'g'ri. Format: <code>01.10.2026 10:00</code>",
        "expo_summary": (
            "📋 <b>{title}</b>\n\n{desc}\n\n📜 Qoidalar:\n{rules}\n\n🎁 Sovg'alar:\n{prizes}\n\n"
            "🗓 {start} → {end}\n\nSaqlaymizmi?"
        ),
        "btn_save": "💾 Saqlash",
        "expo_saved": "💾 Expo saqlandi (qoralama). Faollashtirish mumkin:",
        "btn_activate": "▶️ Faollashtirish",
        "expo_activated": "🚀 «{title}» faol! Ishtirokchilar qo'shilishi mumkin.",
        "expo_other_active": "⚠️ Avval «{title}» exponi yakunlang — Expo'lar ketma-ket o'tadi.",
        "list_empty": "Hali Expo yo'q.",
        "expo_line": "• <b>#{id} {title}</b> — {status} ({start} → {end})",
        "finish_confirm": "⏹ «{title}» yakunlansinmi? Reyting muzlaydi va TOP-10 ga final tekshiruv so'rovi ketadi.",
        "btn_finish_yes": "⏹ Ha, yakunlash",
        "finished": "🏁 Expo yakunlandi. TOP-10 ga final tekshiruv so'rovi yuborildi.",
        "winners_preview": "Hozirgi hisoblar bo'yicha g'oliblar:\n\n{winners}\nE'lon qilaylikmi?",
        "btn_announce": "📣 E'lon qilish",
        "winners_none": "Hali tasdiqlangan video yo'q.",
        "winners_done": "🏆 G'oliblar e'lon qilindi!",
        "no_finished": "Hozir ruxsat etilgan bosqichdagi Expo yo'q.",
        "need_super": "⛔ Faqat superadmin.",

        # ---- rassilka ----
        "bc_choose": "📢 Kimga yuboramiz?",
        "tgt_all": "👥 Barcha foydalanuvchilarga",
        "tgt_participants": "🎪 Faol expo ishtirokchilariga",
        "tgt_approved": "✅ Tasdiqlangan videolarga ega foydalanuvchilar",
        "tgt_pending": "⏳ Arizasi kutilayotganlarga",
        "tgt_top10": "🏆 TOP-10 ga",
        "tgt_single": "🎯 Bitta foydalanuvchiga",
        "bc_ask_single": "Foydalanuvchi TG ID yoki @username yuboring:",
        "user_not_found": "❌ Bunday foydalanuvchi topilmadi.",
        "bc_ask_msg": "✍️ Endi xabarni yuboring (matn yoki rasm+matn):",
        "bc_preview": "📣 Ko'rib chiqish. Qabul qiluvchilar: <b>{count}</b> ta.\nYuborilsinmi?",
        "btn_bc_send": "🚀 Yuborish",
        "bc_cancelled": "Rassilka bekor qilindi.",
        "bc_started": "🚀 Rassilka boshlandi: {count} ta qabul qiluvchi...",
        "bc_progress": "⏳ {sent}/{total} yuborildi...",
        "bc_done": "✅ Rassilka yakunlandi.\n\n✅ Yuborildi: <b>{sent}</b>\n❌ Yetmagan: <b>{failed}</b>\n🚫 Bot bloklagan: <b>{blocked}</b>",
        "bc_busy": "⏳ Boshqa rassilka ketyapti. Tugashini kuting.",

        # ---- statistika ----
        "stats_report": (
            "📊 <b>{expo}</b>\n\n"
            "👥 Jami foydalanuvchilar: <b>{users}</b>\n"
            "🎪 Ishtirokchilar: <b>{participants}</b>\n\n"
            "📥 Ariza yuborgan: <b>{submitted}</b>\n"
            "⏳ Kutilmoqda: <b>{pending}</b>\n"
            "✅ Tasdiqlangan: <b>{approved}</b>\n"
            "❌ Rad etilgan: <b>{rejected}</b>\n\n"
            "👁 Jami ko'ruvlar: <b>{views}</b>\n"
            "📈 O'rtacha: <b>{avg}</b>\n"
            "🚫 Botni bloklagan: <b>{blocked}</b>"
        ),
        "stats_daily": "\n\n📅 Oxirgi 14 kun (ro'yxatdan o'tishlar):\n{daily}",
        "stats_no_expo": "Hozircha Expo yo'q.",

        # ---- eksport ----
        "export_done": "📤 CSV fayllar tayyor.",

        # ---- random sovg'a ----
        "abtn_random": "🎲 Random sovg'a",
        "rnd_none": "⚠️ Yaroqli nomzod yo'q (hamma tasdiqlanganlar asosiy sovg'alar ro'yxatida yoki hech kim tasdiqlanmagan).",
        "rnd_choose_count": "🎲 Nechta g'olib tanlaymiz?",
        "rnd_ask_prize": "🎁 Random sovg'a nomini yozing (masalan: <code>AirPods Pro</code>):",
        "rnd_preview": (
            "🎲 <b>{expo}</b> — random sovg'a o'yini\n\n"
            "🎁 Sovg'a: <b>{prize}</b> × {count}\n"
            "👥 Yaroqli nomzodlar: <b>{total}</b>\n"
            "🔐 Nomzodlar ro'yxati xeshi: <code>{hash}</code>\n\n"
            "Boshlaymizmi? (xesh saqlanadi — haqoniylik isboti)"
        ),
        "rnd_btn_go": "🎲 Boshlash",
        "rnd_announce": (
            "🎲 <b>{expo}</b> — RANDOM SOVG'A g'oliblari!\n"
            "🎁 Sovg'a: <b>{prize}</b>\n\n{lines}\n"
            "🔐 Tekshiruv kodi: <code>{hash}</code>"
        ),
        "rnd_winner_pm": "🎉 Tabriklaymiz! Siz <b>{expo}</b> challenge'ining random sovg'asida yutdingiz!\n🎁 Sovg'a: <b>{prize}</b>",
        "rnd_line": "🎉 {i}. {name} ({insta})\n",
        "rnd_done": "✅ Random o'yin o'tkazildi. G'oliblar xabardor qilindi.",

        # ---- jadval rassilkasi ----
        "bc_btn_now": "🚀 Hozir yuborish",
        "bc_btn_sched": "⏰ Jadvalga qo'yish",
        "bc_ask_sched": "⏰ Qachon yuborilsin? Toshkent vaqtida yozing (masalan: <code>25.09.2026 20:30</code>):",
        "bc_scheduled_ok": "⏰ Rassilka jadvalga qo'yildi: <b>{when}</b> (Toshkent)",
        "bc_bad_time": "❌ Sana noto'g'ri yoki o'tib ketgan. Qayta yozing:",
        "abtn_scheduled": "🕐 Jadvaldagi rassilkalar ({n})",
        "sched_line": "• #{id} — {when} — {target}",
        "sched_empty": "Jadvalda rassilka yo'q.",
        "unsched_done": "❌ #{id} bekor qilindi",
        "group_top_title": "🏆 {expo} — TOP",
    },

    "ru": {
        "welcome": (
            "👋 Здравствуйте! Добро пожаловать в <b>Expo Video Challenge</b> бот.\n\n"
            "Здесь вы участвуете со своим Instagram Reels: побеждает тот, кто соберёт "
            "больше всех подтверждённых просмотров. 🏆"
        ),
        "ask_lang": "Tilni tanlang / Выберите язык:",
        "ask_name": "Напишите имя и фамилию (полностью):",
        "ask_phone": "📱 Отправьте номер телефона кнопкой ниже или впишите (+998...):",
        "btn_share_contact": "📱 Отправить контакт",
        "ask_insta": "Теперь отправьте имя вашего Instagram (например: <code>@username</code>).\n\n⚠️ Видео должно быть опубликовано именно с этого аккаунта — модераторы сверят со скриншотом.",
        "invalid_insta": "❌ Неверный Instagram. Только латиница, цифры, точка и подчёркивание:",
        "invalid_phone": "❌ Неверный номер телефона:",
        "rules_title": "📜 <b>Правила челленджа</b>\n\n{rules}",
        "btn_agree": "✅ Принимаю",
        "btn_decline": "❌ Не принимаю",
        "declined": "Без согласия с правилами нельзя участвовать. /start",
        "reg_done": "🎉 Спасибо {name}! Вы в челлендже.\nТеперь можете отправить видео 👇",
        "profile_done_no_expo": "✅ Профиль сохранён. Сейчас нет активного челленджа — сообщим, когда начнётся!",
        "err_generic": "⚠️ Ошибка. Попробуйте ещё раз или /start.",

        "btn_send_video": "🎥 Отправить видео",
        "btn_update_views": "🔄 Обновить просмотры",
        "btn_my_rank": "📊 Моё место",
        "btn_top": "🏆 Топ-10",
        "btn_my_stats": "📈 Моя статистика",
        "btn_rules": "ℹ️ Правила",
        "btn_join": "🎯 Участвовать в челлендже",
        "btn_admin": "⚙️ Админ панель",
        "btn_cancel": "❌ Отмена",
        "menu_hint": "Выберите в меню 👇",
        "no_active_expo": "😴 Пока нет активного челленджа. Напишем, когда начнётся!",
        "not_participant": "Сначала присоединитесь к челленджу:",
        "expo_window": "⏳ Челлендж сейчас не активен.\nСтарт: {start}\nФиниш: {end}",

        "ask_link": "🔗 Отправьте ссылку на ваш Instagram Reels:\n(например: https://instagram.com/reel/...)",
        "invalid_link": "❌ Это не Reels-ссылка. Нужна вида instagram.com/reel/...:",
        "link_taken": "❌ Это видео уже отправил другой участник. Отправьте своё!",
        "ask_views": "👁 Сколько просмотров сейчас? Только число (например: 12500):",
        "invalid_views": "❌ Введите число. Например: 12500",
        "ask_screen": "📸 Теперь отправьте <b>скриншот</b>, где видно число просмотров.\n\nНа скриншоте обязательно должны быть:\n• число просмотров\n• имя вашего аккаунта",
        "need_photo": "❌ Это не фото. Отправьте скриншот как фото:",
        "btn_keep_link": "⤵️ Оставить старую ссылку",
        "confirm_block": "🔎 <b>Проверьте:</b>\n\n🔗 Ссылка: {url}\n👁 Просмотры: {views}\n📸 Скриншот: ✅\n\nВсё верно?",
        "btn_confirm": "✅ Подтвердить и отправить",
        "cancelled": "❌ Отменено.",
        "submitted": "⏳ Заявка принята! После проверки модераторами сообщим результат.\nНомер: <b>#{sub_id}</b>",
        "already_pending": "⏳ У вас есть заявка на проверке (#{sub_id}). Дождитесь результата.",
        "have_video": "🎥 У вас есть подтверждённое видео (#{sub_id}). Чтобы наращивать просмотры, используйте «🔄 Обновить просмотры».",
        "update_ask_views": "🔄 Текущие подтверждённые просмотры: <b>{current}</b>.\nВведите новое значение (не меньше):",
        "views_too_low": "❌ Новое значение ({new}) меньше подтверждённого ({current}) — это подозрительно. Введите честное число:",
        "update_submitted": "⏳ Новые просмотры со скриншотом отправлены на модерацию. Рейтинг обновится после подтверждения.",
        "report_pending_exists": "⏳ Предыдущее обновление ещё не рассмотрено. Подождите.",
        "no_submission": "У вас пока нет видео. Отправьте через «🎥 Отправить видео».",
        "resub_notice": "Отправьте заявку заново — ссылку можно заменить.",

        "top_title": "🏆 <b>{expo}</b> — Топ-10",
        "top_empty": "Пока никто не подтверждён.",
        "top_line": "{medal} <b>{name}</b> ({insta}) — 👁 {views}\n",
        "top_frozen": "\n🏁 Челлендж завершён, рейтинг заморожен.",
        "rank_block": "📊 <b>Ваше место: #{rank}</b> / {total}\n👁 Ваши просмотры: <b>{views}</b>\n\n{neighbors}",
        "rank_above": "👆 #{r} · {name} — {views} <i>(+{diff} от вас)</i>\n",
        "rank_you": "🫵 #{r} · <b>ВЫ</b> — {views}\n",
        "rank_below": "👇 #{r} · {name} — {views} <i>(-{diff} позади)</i>\n",
        "rank_last": "Вы последний в рейтинге. 💪",
        "rank_first": "🥇 Вы первый! Позади: #{r} · {name} (-{diff}).",
        "no_rank": "Чтобы попасть в рейтинг, видео должно пройти модерацию.",
        "my_stats": "📈 <b>История ваших просмотров:</b>\n{lines}",
        "my_stats_empty": "Подтверждённых просмотров пока нет.",
        "my_stats_line": "• {date} — 👁 {views}\n",

        "rev_new": "🆕 <b>НОВАЯ ЗАЯВКА</b> (sub #{sub_id})",
        "rev_update": "🔄 <b>ОБНОВЛЕНИЕ</b> (sub #{sub_id}): {old} → <b>{new}</b> ({sign}{pct}%)",
        "rev_final": "🏁 <b>ФИНАЛЬНАЯ ПРОВЕРКА</b> (sub #{sub_id})",
        "rev_flags": "\n⚠️ ФЛАГИ: {flags}",
        "rev_body": "👤 {name} — {insta}\n📱 {phone}\n🔗 <a href=\"{url}\">Ссылка на видео</a>\n👁 Введённые просмотры: <b>{views}</b>",
        "btn_approve": "✅ Подтвердить",
        "btn_reject": "❌ Отклонить",
        "btn_changes": "✏️ На доработку",
        "rev_approved_mark": "\n\n✅ <b>ПОДТВЕРЖДЕНО</b> — {mod}",
        "rev_rejected_mark": "\n\n❌ <b>ОТКЛОНЕНО</b> — {mod}. Причина: {reason}",
        "rev_changes_mark": "\n\n✏️ <b>НА ДОРАБОТКУ</b> — {mod}. Причина: {reason}",
        "rev_already": "Заявка уже рассмотрена.",
        "no_rights": "⛔ Нет прав на рассмотрение — вы должны быть участником группы жюри.",
        "choose_reason": "Выберите причину:",
        "rsn_wrong_screen": "Скриншот нечитаем/не подходит",
        "rsn_bad_link": "Ссылка не открывается",
        "rsn_not_own": "Видео не ваше",
        "rsn_edited": "Подозрение на монтаж",
        "rsn_other": "Другая причина (написать)",
        "custom_reason_prompt": "✏️ Напишите причину ответом (reply) на это сообщение:",

        "ntf_approved": "✅ Поздравляем! Видео подтверждено и попало в рейтинг! 🎉\nПросмотры: <b>{views}</b>. Наращивайте!",
        "ntf_rejected": "❌ Заявка отклонена.\nПричина: <b>{reason}</b>\n\nМожно отправить заново 👇",
        "ntf_changes": "✏️ По вашей заявке нужны правки.\nПричина: <b>{reason}</b>\n\nОтправьте заново 👇",
        "btn_resubmit": "🔄 Отправить заново",
        "ntf_update_approved": "✅ Просмотры обновлены: <b>{views}</b>. Проверьте рейтинг!",
        "ntf_update_rejected": "❌ Обновление просмотров отклонено.\nПричина: <b>{reason}</b>",

        "final_check_req": (
            "🏁 <b>Челлендж завершён!</b> Вы в ТОП-10 — чтобы стать победителем, "
            "в течение {hours} ч. отправьте <b>финальную проверку</b>: свежий "
            "<b>скриншот</b> просмотров или запись экрана."
        ),
        "btn_final_send": "🏁 Отправить финальную проверку",
        "final_late": "⏰ Время финальной проверки вышло.",
        "winner_announce": "🏆 <b>{expo}</b> — победители челленджа!\n\n{winners}\n\nПоздравляем! 🎉🎉🎉",
        "winner_line": "{medal} {name} ({insta}) — 👁 {views} — 🎁 {prize}\n",
        "winner_pm": "🥳 <b>Поздравляем! Вы заняли {place}-е место!</b>\n🎁 Приз: <b>{prize}</b>\n\nОрганизаторы скоро свяжутся с вами.",
        "results_frozen": "🏁 Челлендж завершён. Результаты скоро объявят!",

        "admin_denied": "⛔ Только для админов.",
        "admin_menu": "⚙️ <b>Админ панель</b>",
        "abtn_new_expo": "🆕 Новое Expo",
        "abtn_list": "📋 Список Expo",
        "abtn_broadcast": "📢 Рассылка",
        "abtn_stats": "📊 Статистика",
        "abtn_export": "📤 Экспорт (CSV)",
        "abtn_winners": "🏆 Объявить победителей",
        "abtn_finish": "⏹ Завершить челлендж",
        "abtn_users": "👥 Админы",
        "expo_ask_title": "🆕 Новое Expo. Название:",
        "expo_ask_desc": "Краткое описание:",
        "expo_ask_rules": "Текст правил (виден при регистрации):",
        "expo_ask_prizes": "🎁 Призы по одному (например: <code>1 — iPhone 16</code>).\nКогда закончите — «✅ Готово».",
        "expo_prizes_done": "✅ Готово",
        "expo_ask_start": "Дата старта (по Ташкенту, напр.: <code>01.10.2026 10:00</code>):",
        "expo_ask_end": "Дата окончания:",
        "bad_date": "❌ Неверная дата. Формат: <code>01.10.2026 10:00</code>",
        "expo_summary": "📋 <b>{title}</b>\n\n{desc}\n\n📜 Правила:\n{rules}\n\n🎁 Призы:\n{prizes}\n\n🗓 {start} → {end}\n\nСохранить?",
        "btn_save": "💾 Сохранить",
        "expo_saved": "💾 Expo сохранено (черновик). Можно активировать:",
        "btn_activate": "▶️ Активировать",
        "expo_activated": "🚀 «{title}» активно! Участники могут присоединяться.",
        "expo_other_active": "⚠️ Сначала завершите «{title}» — Expo идут последовательно.",
        "list_empty": "Expo пока нет.",
        "expo_line": "• <b>#{id} {title}</b> — {status} ({start} → {end})",
        "finish_confirm": "⏹ Завершить «{title}»? Рейтинг заморозится, ТОП-10 получит запрос финальной проверки.",
        "btn_finish_yes": "⏹ Да, завершить",
        "finished": "🏁 Expo завершено. ТОП-10 получили запрос.",
        "winners_preview": "По текущим цифрам победители:\n\n{winners}\nОбъявляем?",
        "btn_announce": "📣 Объявить",
        "winners_none": "Подтверждённых видео пока нет.",
        "winners_done": "🏆 Победители объявлены!",
        "no_finished": "Нет Expo на подходящей стадии.",
        "need_super": "⛔ Только суперадмин.",

        "bc_choose": "📢 Кому отправить?",
        "tgt_all": "👥 Всем пользователям",
        "tgt_participants": "🎪 Участникам активного Expo",
        "tgt_approved": "✅ Тем, у кого подтверждено видео",
        "tgt_pending": "⏳ У кого заявка на проверке",
        "tgt_top10": "🏆 ТОП-10",
        "tgt_single": "🎯 Одному пользователю",
        "bc_ask_single": "Отправьте TG ID или @username:",
        "user_not_found": "❌ Пользователь не найден.",
        "bc_ask_msg": "✍️ Отправьте сообщение (текст или фото+текст):",
        "bc_preview": "📣 Предпросмотр. Получателей: <b>{count}</b>.\nОтправляем?",
        "btn_bc_send": "🚀 Отправить",
        "bc_cancelled": "Рассылка отменена.",
        "bc_started": "🚀 Рассылка началась: {count} получателей...",
        "bc_progress": "⏳ {sent}/{total} отправлено...",
        "bc_done": "✅ Рассылка завершена.\n\n✅ Ушло: <b>{sent}</b>\n❌ Не дошло: <b>{failed}</b>\n🚫 Заблокировали бота: <b>{blocked}</b>",
        "bc_busy": "⏳ Уже идёт другая рассылка. Дождитесь конца.",

        "stats_report": (
            "📊 <b>{expo}</b>\n\n"
            "👥 Всего пользователей: <b>{users}</b>\n"
            "🎪 Участников: <b>{participants}</b>\n\n"
            "📥 Отправили заявку: <b>{submitted}</b>\n"
            "⏳ На проверке: <b>{pending}</b>\n"
            "✅ Подтверждено: <b>{approved}</b>\n"
            "❌ Отклонено: <b>{rejected}</b>\n\n"
            "👁 Всего просмотров: <b>{views}</b>\n"
            "📈 В среднем: <b>{avg}</b>\n"
            "🚫 Заблокировали бота: <b>{blocked}</b>"
        ),
        "stats_daily": "\n\n📅 Последние 14 дней (регистрации):\n{daily}",
        "stats_no_expo": "Expo пока нет.",

        "export_done": "📤 CSV-файлы готовы.",

        # ---- случайный приз ----
        "abtn_random": "🎲 Случайный приз",
        "rnd_none": "⚠️ Нет подходящих кандидатов (все подтверждённые уже в призах или никто не подтверждён).",
        "rnd_choose_count": "🎲 Сколько победителей выбираем?",
        "rnd_ask_prize": "🎁 Название случайного приза (например: <code>AirPods Pro</code>):",
        "rnd_preview": (
            "🎲 <b>{expo}</b> — случайный розыгрыш\n\n"
            "🎁 Приз: <b>{prize}</b> × {count}\n"
            "👥 Подходящих кандидатов: <b>{total}</b>\n"
            "🔐 Хеш списка кандидатов: <code>{hash}</code>\n\n"
            "Начинаем? (хеш сохраняется — доказательство честности)"
        ),
        "rnd_btn_go": "🎲 Запустить",
        "rnd_announce": (
            "🎲 <b>{expo}</b> — победители СЛУЧАЙНОГО розыгрыша!\n"
            "🎁 Приз: <b>{prize}</b>\n\n{lines}\n"
            "🔐 Проверочный код: <code>{hash}</code>"
        ),
        "rnd_winner_pm": "🎉 Поздравляем! Вы выиграли случайный приз <b>{expo}</b>!\n🎁 Приз: <b>{prize}</b>",
        "rnd_line": "🎉 {i}. {name} ({insta})\n",
        "rnd_done": "✅ Розыгрыш проведён. Победители уведомлены.",

        # ---- отложенная рассылка ----
        "bc_btn_now": "🚀 Отправить сейчас",
        "bc_btn_sched": "⏰ Запланировать",
        "bc_ask_sched": "⏰ Когда отправить? Время Ташкента (например: <code>25.09.2026 20:30</code>):",
        "bc_scheduled_ok": "⏰ Рассылка запланирована: <b>{when}</b> (Ташкент)",
        "bc_bad_time": "❌ Неверная дата или уже прошла. Ещё раз:",
        "abtn_scheduled": "🕐 Запланированные рассылки ({n})",
        "sched_line": "• #{id} — {when} — {target}",
        "sched_empty": "Запланированных рассылок нет.",
        "unsched_done": "❌ #{id} отменена",
        "group_top_title": "🏆 {expo} — ТОП",
    },
}


def t(lang: str | None, key: str, **kw) -> str:
    lang = lang if lang in TEXTS else "uz"
    s = TEXTS[lang].get(key) or TEXTS["uz"].get(key) or key
    return s.format(**kw) if kw else s
