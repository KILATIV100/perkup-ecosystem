# Dockerfile

# 1. ВИПРАВЛЕНО: Змінено базовий образ на підтримуваний (Debian Bookworm)
FROM python:3.11-slim

# Встановлюємо необхідні системні залежності для компіляції (asyncpg)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Встановлюємо робочу директорію
WORKDIR /app

# 2. ВИПРАВЛЕНО: Явно встановлюємо PYTHONPATH
# Це ГАРАНТУЄ, що 'src' буде знайдено при імпорті 'from src.app...'
ENV PYTHONPATH=/app

# Копіюємо requirements.txt та встановлюємо Python залежності
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо решту коду
COPY . .

# 3. КОМАНДА ЗАПУСКУ: Використовуємо '-m' для коректної роботи з пакетами
CMD ["python", "-m", "src.main"]
