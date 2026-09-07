"""Bot konfiguratsiyasi — barcha sozlamalar env o'zgaruvchilardan o'qiladi."""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Majburiy
    bot_token: str = ""

    # Baza: lokalda sqlite, fly.io da postgres (fly postgres attach bergan URL)
    database_url: str = "sqlite+aiosqlite:///./data/app.db"

    # Rollar va guruhlar
    superadmin_ids_raw: str = ""   # "111,222"
    review_group_id: int | None = None
    announce_chat_id: int | None = None  # g'oliblar e'lon qilinadigan kanal/guruh

    # Texnik
    web_port: int = 8080
    default_lang: str = "uz"
    auto_migrate: bool = True

    # Rassilka
    max_msgs_per_sec: int = 25

    # Anti-fraud chegaralari
    suspect_jump_pct: int = 30     # 1 soat ichida o'sish % dan oshsa → flag
    suspect_jump_abs: int = 5000   # 1 soat ichida shuncha ko'ruv qo'shilsa → flag

    # Final tekshiruvga beriladigan vaqt (soat)
    final_check_hours: int = 24

    @property
    def superadmin_ids(self) -> list[int]:
        out = []
        for part in (self.superadmin_ids_raw or "").split(","):
            part = part.strip()
            if part.lstrip("-").isdigit():
                out.append(int(part))
        return out


@lru_cache
def get_settings() -> Settings:
    return Settings()
