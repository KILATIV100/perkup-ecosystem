# Dockerfile

# Використовуємо офіційний Python 3.11 Slim, 
# який зазвичай має менше залежностей, але підтримує Alpine/Debian base
# Якщо потрібен Python 3.13, використовуйте 3.13-slim або 3.13-bookworm.
# Використовуємо 3.11 як стабільну версію для aiogram 3.x
FROM python:3.11-slim-buster 

# Встановлюємо необхідні системні залежності для компіляції:
# 1. build-essential: Містить gcc, g++ та make (компілятори).
# 2. libpq-dev: Бібліотека PostgreSQL, необхідна для компіляції asyncpg та psycopg2.
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
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо решту коду
COPY . .

# Команда запуску (використовуємо команду з Procfile)
# Переконайтеся, що Procfile також присутній
CMD ["python", "src/main.py"]
