# Dockerfile

# ВИПРАВЛЕНО: Змінено базовий образ на підтримуваний 
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

# Копіюємо requirements.txt та встановлюємо Python залежності
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо решту коду
COPY . .

# КОМАНДА ЗАПУСКУ: Використовуємо '-m' для запуску як модуля, 
# що вирішує проблему імпорту 'src'
CMD ["python", "-m", "src.main"]
