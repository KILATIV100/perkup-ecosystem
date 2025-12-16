# Детальна інструкція з розгортання PerkUP

## 1. Railway.com (Рекомендовано для Backend)

### 1.1 Реєстрація та створення проекту

1. Зареєструйтесь на [railway.app](https://railway.app)
2. Натисніть **"New Project"**
3. Виберіть **"Deploy from GitHub repo"**
4. Підключіть GitHub та виберіть репозиторій `perkup-ecosystem`

### 1.2 Налаштування PostgreSQL

1. В проекті натисніть **"+ New"** → **"Database"** → **"PostgreSQL"**
2. Railway автоматично створить базу даних
3. Скопіюйте `DATABASE_URL` з вкладки **Variables**

### 1.3 Налаштування Redis

1. Натисніть **"+ New"** → **"Database"** → **"Redis"**
2. Скопіюйте `REDIS_URL` з вкладки **Variables**

### 1.4 Деплой Backend

1. Натисніть **"+ New"** → **"GitHub Repo"**
2. Виберіть репозиторій
3. В налаштуваннях вкажіть:
   - **Root Directory**: `backend`
   - **Build Command**: (залишити пустим, використовується Dockerfile)

4. Додайте **Environment Variables**:
```
APP_NAME=PerkUP
APP_ENV=production
DEBUG=false
SECRET_KEY=<генеруйте-випадковий-рядок-32-символи>
JWT_SECRET_KEY=<генеруйте-інший-випадковий-рядок>
JWT_ALGORITHM=HS256
JWT_EXPIRATION_DAYS=30
TELEGRAM_BOT_TOKEN=<ваш-токен-від-botfather>
TELEGRAM_WEBAPP_URL=https://tma.perkup.com.ua
CORS_ORIGINS=https://perkup.com.ua,https://tma.perkup.com.ua
```

5. Railway автоматично підставить `DATABASE_URL` та `REDIS_URL`

6. Налаштуйте домен:
   - **Settings** → **Networking** → **Generate Domain**
   - Або підключіть власний: `api.perkup.com.ua`

### 1.5 Деплой Frontend (TMA)

1. Натисніть **"+ New"** → **"GitHub Repo"**
2. Виберіть той самий репозиторій
3. В налаштуваннях:
   - **Root Directory**: `frontend`

4. Додайте **Environment Variables**:
```
VITE_API_URL=https://api.perkup.com.ua/api/v1
```

5. Налаштуйте домен: `tma.perkup.com.ua`

---

## 2. Vercel (Альтернатива для Frontend)

### 2.1 Деплой на Vercel

1. Зайдіть на [vercel.com](https://vercel.com)
2. **"Add New Project"** → Імпортуйте з GitHub
3. Налаштування:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

4. Environment Variables:
```
VITE_API_URL=https://api.perkup.com.ua/api/v1
```

5. Підключіть домен `tma.perkup.com.ua`

---

## 3. nic.ua (Статичний сайт)

### 3.1 Завантаження через cPanel

1. Увійдіть в cPanel вашого хостингу на nic.ua
2. Відкрийте **"Диспетчер файлів"** (File Manager)
3. Перейдіть в `public_html`
4. Завантажте файли з папки `website/`:
   - `index.html`
   - `css/style.css`
   - `js/main.js`
   - `images/coffee-icon.svg`

### 3.2 Через FTP

```bash
# Підключення через FTP
Host: ftp.perkup.com.ua
Username: <ваш-логін>
Password: <ваш-пароль>
Port: 21

# Завантажте вміст папки website/ в public_html/
```

### 3.3 Структура на хостингу
```
public_html/
├── index.html
├── css/
│   └── style.css
├── js/
│   └── main.js
└── images/
    └── coffee-icon.svg
```

---

## 4. Cloudflare (DNS налаштування)

### 4.1 Додайте DNS записи

| Type | Name | Content | Proxy |
|------|------|---------|-------|
| A | @ | IP nic.ua хостингу | Yes |
| A | www | IP nic.ua хостингу | Yes |
| CNAME | api | your-backend.up.railway.app | Yes |
| CNAME | tma | your-frontend.up.railway.app | Yes |

### 4.2 SSL налаштування

1. **SSL/TLS** → **Overview** → **Full (strict)**
2. **Edge Certificates** → **Always Use HTTPS**: On

---

## 5. Telegram Bot налаштування

### 5.1 Створення бота

1. Відкрийте [@BotFather](https://t.me/BotFather)
2. Надішліть `/newbot`
3. Введіть назву: `PerkUP Coffee`
4. Введіть username: `perkup_ua_bot`
5. Збережіть токен

### 5.2 Налаштування Mini App

1. В BotFather: `/mybots` → виберіть бота
2. **Bot Settings** → **Menu Button**
3. Встановіть URL: `https://tma.perkup.com.ua`

### 5.3 Налаштування Webhook

```bash
# Встановлення webhook
curl -X POST "https://api.telegram.org/bot<TOKEN>/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://api.perkup.com.ua/webhooks/telegram"}'
```

### 5.4 Команди бота

В BotFather: `/setcommands`
```
start - Головне меню
balance - Перевірити баланс
checkin - Зробити check-in
play - Грати в ігри
events - Активні івенти
leaderboard - Таблиця лідерів
help - Довідка
settings - Налаштування
```

---

## 6. Перша міграція бази даних

Після деплою backend, виконайте міграції:

```bash
# Через Railway CLI
railway run alembic upgrade head

# Або через SSH/Console в Railway Dashboard
alembic upgrade head
```

---

## 7. Перевірка працездатності

### API Health Check
```bash
curl https://api.perkup.com.ua/health
# Очікувана відповідь: {"status": "healthy", "app": "PerkUP"}
```

### API Documentation
- Swagger: https://api.perkup.com.ua/docs
- ReDoc: https://api.perkup.com.ua/redoc

### Telegram Bot
1. Відкрийте https://t.me/perkup_ua_bot
2. Натисніть /start
3. Перевірте, що Mini App відкривається

---

## 8. Моніторинг та логи

### Railway
- **Deployments** → Виберіть деплой → **View Logs**
- **Metrics** → CPU, Memory, Network

### Cloudflare
- **Analytics** → Трафік та запити
- **Security** → Blocked threats

---

## 9. Корисні команди

### Railway CLI
```bash
# Встановлення
npm install -g @railway/cli

# Логін
railway login

# Підключення до проекту
railway link

# Запуск команди в контексті проекту
railway run <command>

# Перегляд логів
railway logs
```

### Docker локально
```bash
# Запуск всього стеку
docker-compose up -d

# Перегляд логів
docker-compose logs -f backend

# Зупинка
docker-compose down
```

---

## 10. Безпека (Важливо!)

1. **Ніколи не комітьте** `.env` файли з секретами
2. Використовуйте **різні SECRET_KEY** для dev та prod
3. Увімкніть **HTTPS** для всіх сервісів
4. Налаштуйте **rate limiting** на Cloudflare
5. Регулярно **оновлюйте** залежності

---

## Контакти підтримки

- Railway: https://railway.app/help
- Vercel: https://vercel.com/help
- Cloudflare: https://support.cloudflare.com
- nic.ua: https://nic.ua/uk/support
