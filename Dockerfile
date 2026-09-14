FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# OpenCV (RapidOCR) uchun system kutubxonalar — libGL talab qilinadi
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# fly.io release_command orqali migratsiyalar yuritiladi (fly.toml),
# lekin startup'da ham auto-migrate bor — xavfsiz (idempotent).
CMD ["python", "-m", "bot.main"]
