# Dockerfile

# ВИПРАВЛЕНО: Змінено базовий образ на більш сучасний та підтримуваний 
# (наприклад, Debian Bullseye або Bookworm), щоб уникнути помилки 404
FROM python:3.11-slim

# Встановлюємо необхідні системні залежності для компіляції Python-пакетів з C-розширеннями (asyncpg, psycopg2):
# 1. build-essential: Містить gcc, g++ та make (компілятори).
# 2. libpq-dev: Бібліотека PostgreSQL.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Встановлюємо робочу директорію
WORKDIR /app

# Копіюємо requirements.txt та встановлюємо Python залежності
COPY requirements.txt .
# Використовуємо --break-system-packages (для Docker це нормально)
RUN pip install --no-cache-dir -r requirements.txt --break-system-packages

# Копіюємо решту коду
COPY . .

# Команда запуску (використовуємо команду з Procfile)
# CMD ["python", "src/main.py"] # Зазвичай, Railway сам визначає CMD/ENTRYPOINT з Procfile
ENTRYPOINT ["python", "src/main.py"]
