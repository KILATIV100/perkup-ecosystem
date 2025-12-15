# PerkUP Ecosystem

Digital loyalty ecosystem for coffee shops with gamification, Telegram Mini App, and web integration.

## Features

- **Telegram Mini App** - Main platform for users
- **Gamified Loyalty System** - Points, levels, achievements
- **Check-in System** - GPS-based location check-ins
- **Games** - Coffee Jump, Coffee Match, Barista Rush, Coffee Quiz, Spin the Wheel
- **Events & Promotions** - Tournaments, challenges, offline events
- **Leaderboard** - Daily, weekly, monthly rankings

## Tech Stack

### Backend
- Python 3.11+
- FastAPI
- PostgreSQL 15
- Redis 7
- SQLAlchemy 2.0 (async)
- Alembic (migrations)
- python-telegram-bot

### Frontend (Telegram Mini App)
- React 18
- TypeScript
- Vite
- Tailwind CSS
- Zustand (state management)
- @twa-dev/sdk

### Infrastructure
- Railway.com (Backend hosting)
- nic.ua (Static website hosting)
- Cloudflare (DNS)

## Project Structure

```
perkup-ecosystem/
├── backend/           # FastAPI application
│   ├── app/
│   │   ├── api/       # API endpoints
│   │   ├── core/      # Config, security
│   │   ├── db/        # Database session
│   │   ├── models/    # SQLAlchemy models
│   │   ├── schemas/   # Pydantic schemas
│   │   ├── services/  # Business logic
│   │   ├── bot/       # Telegram bot
│   │   └── utils/     # Utilities
│   ├── alembic/       # Database migrations
│   └── Dockerfile
├── frontend/          # React Telegram Mini App
│   ├── src/
│   │   ├── api/       # API client
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── pages/
│   │   ├── store/     # Zustand stores
│   │   └── types/
│   └── Dockerfile
├── website/           # Static landing page
│   ├── css/
│   ├── js/
│   └── index.html
└── docker-compose.yml
```

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 20+
- Python 3.11+

### Development

1. Clone the repository:
```bash
git clone https://github.com/your-org/perkup-ecosystem.git
cd perkup-ecosystem
```

2. Start with Docker Compose:
```bash
docker-compose up -d
```

3. Access the services:
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Frontend: http://localhost:5173
- PostgreSQL: localhost:5432
- Redis: localhost:6379

### Manual Setup

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your settings
alembic upgrade head
uvicorn app.main:app --reload
```

#### Frontend
```bash
cd frontend
npm install
cp .env.example .env
# Edit .env with your settings
npm run dev
```

## API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Environment Variables

### Backend
| Variable | Description | Default |
|----------|-------------|---------|
| DATABASE_URL | PostgreSQL connection string | - |
| REDIS_URL | Redis connection string | - |
| SECRET_KEY | Application secret key | - |
| JWT_SECRET_KEY | JWT signing key | - |
| TELEGRAM_BOT_TOKEN | Telegram bot token | - |
| TELEGRAM_WEBAPP_URL | Mini App URL | - |

### Frontend
| Variable | Description | Default |
|----------|-------------|---------|
| VITE_API_URL | Backend API URL | http://localhost:8000/api/v1 |

## Deployment

### Railway (Backend)
1. Connect your GitHub repository to Railway
2. Set environment variables
3. Deploy from the `backend` directory

### Vercel (Frontend)
1. Connect your GitHub repository to Vercel
2. Set build directory to `frontend`
3. Set environment variables
4. Deploy

### Static Website
Upload `website/` contents to your hosting via FTP/cPanel.

## Telegram Bot Setup

1. Create a bot via [@BotFather](https://t.me/BotFather)
2. Get the bot token
3. Set up the Mini App URL in bot settings
4. Configure webhook URL

## Locations

| Name | Address | Coordinates |
|------|---------|-------------|
| Mark Mall | Київська, 239, Бровари | 50.514794, 30.782308 |
| Парк Приозерний | вул. Фіалковського, 27а, Бровари | 50.501265, 30.754011 |

## License

MIT License - see LICENSE file for details.

## Contact

- Telegram: [@perkup_ua_bot](https://t.me/perkup_ua_bot)
- Channel: [@perkup_news](https://t.me/perkup_news)
- Instagram: [@perk_up_bro](https://instagram.com/perk_up_bro)
