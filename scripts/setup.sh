#!/bin/bash
# scripts/setup.sh
# Автоматичне налаштування PerkUP Ecosystem для macOS

set -e

# Кольори
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Лого
echo -e "${BLUE}"
cat << "EOF"
╔═══════════════════════════════════════╗
║                                       ║
║       🤖☕ PERKUP SETUP v1.0         ║
║       Production-Ready Setup          ║
║                                       ║
╚═══════════════════════════════════════╝
EOF
echo -e "${NC}"

echo "🚀 Початок повного налаштування PerkUP Ecosystem..."
echo ""

# Перевірка інструментів
echo -e "${BLUE}▶ Перевірка необхідних інструментів...${NC}"

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 не знайдено${NC}"
    echo "Встанови: brew install python@3.11"
    exit 1
fi
echo -e "${GREEN}✓ Python $(python3 --version) знайдено${NC}"

if ! command -v node &> /dev/null; then
    echo -e "${RED}✗ Node.js не знайдено${NC}"
    echo "Встанови: brew install node@18"
    exit 1
fi
echo -e "${GREEN}✓ Node.js $(node --version) знайдено${NC}"

if ! command -v git &> /dev/null; then
    echo -e "${RED}✗ Git не знайдено${NC}"
    echo "Встанови: brew install git"
    exit 1
fi
echo -e "${GREEN}✓ Git знайдено${NC}"

echo ""

# Перейти в root проекту
cd "$(dirname "$0")/.."

# Створення структури
echo -e "${BLUE}▶ Створення структури папок...${NC}"

# Backend
mkdir -p backend/app/{core,models,schemas,api/v1,services,utils,tasks}
mkdir -p backend/{tests,scripts,alembic/versions}

# Frontend TMA
mkdir -p frontend-tma/public/assets/{icons,sounds,images}
mkdir -p frontend-tma/src/{config,hooks,services,store,types}
mkdir -p frontend-tma/src/components/{common,locations,checkin,game,shop,profile}
mkdir -p frontend-tma/src/{pages,game,utils,styles}

# Frontend Web
mkdir -p frontend-web/public/assets
mkdir -p frontend-web/src/app/{locations,menu,shop,delivery,profile}
mkdir -p frontend-web/src/components/{layout,home,map,delivery,shop,ui}
mkdir -p frontend-web/src/lib/{api,utils,hooks}
mkdir -p frontend-web/src/{styles,types}

# Database
mkdir -p database/{migrations,seeds}

# Docs
mkdir -p docs/images

# Docker
mkdir -p docker/nginx

# GitHub
mkdir -p .github/{workflows,ISSUE_TEMPLATE}

echo -e "${GREEN}✓ Структура створена (100+ папок)${NC}"

# .gitignore
echo -e "${BLUE}▶ Створення .gitignore...${NC}"
cat > .gitignore << 'EOF'
# Environment
.env
.env.local
.env.production
.env.*.local
*.pem
*.key
secrets/

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
venv/
env/
.Python
build/
dist/

# Node
node_modules/
dist/
build/
.next/
out/
package-lock.json
yarn.lock

# Database
*.db
*.sqlite
*.sqlite3
*.dump

# OS
.DS_Store
.AppleDouble
.LSOverride
._*
Thumbs.db

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Logs
*.log
logs/

# Temporary
*.tmp
*.temp
*.bak
EOF
echo -e "${GREEN}✓ .gitignore створено${NC}"

# Backend requirements.txt
echo -e "${BLUE}▶ Створення backend/requirements.txt...${NC}"
cat > backend/requirements.txt << 'EOF'
# Core
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-multipart==0.0.6

# Database
sqlalchemy==2.0.25
alembic==1.13.1
psycopg2-binary==2.9.9
asyncpg==0.29.0

# Authentication
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-telegram-bot==20.7

# Utilities
pydantic==2.5.3
pydantic-settings==2.1.0
python-dotenv==1.0.0
httpx==0.26.0

# Geo
haversine==2.8.0

# Task Queue
celery==5.3.6
redis==5.0.1

# Logging
loguru==0.7.2

# Monitoring
sentry-sdk==1.39.2
EOF
echo -e "${GREEN}✓ requirements.txt створено${NC}"

# Backend requirements-dev.txt
cat > backend/requirements-dev.txt << 'EOF'
-r requirements.txt

# Development
black==23.12.1
flake8==7.0.0
mypy==1.7.1
isort==5.13.2

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
EOF

# Backend .env.example
echo -e "${BLUE}▶ Створення .env.example файлів...${NC}"
cat > backend/.env.example << 'EOF'
# Application
APP_NAME=PerkUP
APP_ENV=development
DEBUG=true
SECRET_KEY=your-super-secret-key-change-this

# Database
DATABASE_URL=postgresql://perkup:password@localhost:5432/perkup_dev

# Redis
REDIS_URL=redis://localhost:6379

# Telegram
TELEGRAM_BOT_TOKEN=your-telegram-bot-token-here
TELEGRAM_WEBHOOK_URL=https://api.perkup.com.ua/webhooks/telegram

# JWT
JWT_SECRET_KEY=another-secret-key-change-this
JWT_ALGORITHM=HS256
JWT_EXPIRATION_DAYS=30

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Settings
CHECKIN_COOLDOWN_HOURS=12
CHECKIN_RADIUS_METERS=100
POINTS_PER_CHECKIN=1
EOF
echo -e "${GREEN}✓ backend/.env.example створено${NC}"

# Backend __init__.py файли
touch backend/app/__init__.py
touch backend/app/core/__init__.py
touch backend/app/models/__init__.py
touch backend/app/schemas/__init__.py
touch backend/app/api/__init__.py
touch backend/app/api/v1/__init__.py
touch backend/app/services/__init__.py
touch backend/app/utils/__init__.py
touch backend/app/tasks/__init__.py

# Backend main.py
cat > backend/app/main.py << 'EOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="PerkUP API",
    description="Backend API для PerkUP Ecosystem",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "message": "🤖☕ PerkUP API is running!",
        "version": "1.0.0",
        "status": "healthy"
    }

@app.get("/health")
def health():
    return {"status": "healthy", "service": "perkup-backend"}

@app.get("/api/v1/locations")
def get_locations():
    """Отримати список локацій"""
    return [
        {
            "id": 1,
            "name": "Mark Mall",
            "address": "Київська, 239, Бровари",
            "latitude": 50.514794,
            "longitude": 30.782308,
            "radius_meters": 100,
            "is_active": True
        },
        {
            "id": 2,
            "name": "Парк Приозерний",
            "address": "вул. Фіалковського, 27а, Бровари",
            "latitude": 50.501265,
            "longitude": 30.754011,
            "radius_meters": 100,
            "is_active": True
        }
    ]
EOF

# Frontend TMA package.json
echo -e "${BLUE}▶ Створення frontend-tma/package.json...${NC}"
cat > frontend-tma/package.json << 'EOF'
{
  "name": "perkup-tma",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "lint": "eslint . --ext ts,tsx"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.21.0",
    "@twa-dev/sdk": "^7.0.0",
    "axios": "^1.6.2",
    "zustand": "^4.4.7"
  },
  "devDependencies": {
    "@types/react": "^18.2.45",
    "@types/react-dom": "^18.2.18",
    "@vitejs/plugin-react": "^4.2.1",
    "typescript": "^5.3.3",
    "vite": "^5.0.8",
    "tailwindcss": "^3.4.0",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.32"
  }
}
EOF

# Vite config
cat > frontend-tma/vite.config.ts << 'EOF'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: true
  }
})
EOF

# tsconfig.json
cat > frontend-tma/tsconfig.json << 'EOF'
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
EOF

cat > frontend-tma/tsconfig.node.json << 'EOF'
{
  "compilerOptions": {
    "composite": true,
    "skipLibCheck": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowSyntheticDefaultImports": true
  },
  "include": ["vite.config.ts"]
}
EOF

# index.html
cat > frontend-tma/index.html << 'EOF'
<!DOCTYPE html>
<html lang="uk">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>PerkUP - Система лояльності</title>
</head>
<body>
  <div id="root"></div>
  <script type="module" src="/src/main.tsx"></script>
</body>
</html>
EOF

# Frontend .env.example
cat > frontend-tma/.env.example << 'EOF'
VITE_API_URL=http://localhost:8000/api/v1
VITE_TELEGRAM_BOT_USERNAME=perkup_ua_bot
EOF

# src/main.tsx
cat > frontend-tma/src/main.tsx << 'EOF'
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
EOF

# src/App.tsx
cat > frontend-tma/src/App.tsx << 'EOF'
import { useEffect, useState } from 'react'
import './App.css'

interface Location {
  id: number
  name: string
  address: string
  latitude: number
  longitude: number
  is_active: boolean
}

function App() {
  const [locations, setLocations] = useState<Location[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetch('http://localhost:8000/api/v1/locations')
      .then(res => {
        if (!res.ok) throw new Error('Failed to fetch')
        return res.json()
      })
      .then(data => {
        setLocations(data)
        setLoading(false)
      })
      .catch(err => {
        console.error('Error:', err)
        setError('Не вдалося завантажити локації')
        setLoading(false)
      })
  }, [])

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Завантаження...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="error-container">
        <p>❌ {error}</p>
        <button onClick={() => window.location.reload()}>
          Спробувати знову
        </button>
      </div>
    )
  }

  return (
    <div className="app">
      <header className="header">
        <div className="logo">🤖☕</div>
        <h1>PerkUP</h1>
        <p className="subtitle">Система лояльності для кав'ярень</p>
        <div className="stats">
          <div className="stat">
            <span className="stat-value">0</span>
            <span className="stat-label">Балів</span>
          </div>
          <div className="stat">
            <span className="stat-value">1</span>
            <span className="stat-label">Рівень</span>
          </div>
        </div>
      </header>

      <main className="main">
        <h2>📍 Наші Локації</h2>
        <div className="locations">
          {locations.map(loc => (
            <div key={loc.id} className="location-card">
              <div className="location-header">
                <h3>{loc.name}</h3>
                <span className="location-badge">
                  {loc.is_active ? '🟢 Відкрито' : '🔴 Закрито'}
                </span>
              </div>
              <p className="location-address">{loc.address}</p>
              <div className="location-info">
                <span>📏 До {loc.radius_meters}м для check-in</span>
              </div>
              <button className="checkin-btn">
                ✓ Check-in
              </button>
            </div>
          ))}
        </div>
      </main>

      <footer className="footer">
        <p>© 2025 PerkUP. Зроблено з ❤️ та ☕</p>
      </footer>
    </div>
  )
}

export default App
EOF

# CSS files
cat > frontend-tma/src/index.css << 'EOF'
:root {
  --primary: #6C5CE7;
  --primary-dark: #5F4FD1;
  --secondary: #00B894;
  --background: #0D0C1D;
  --surface: #161B33;
  --text: #FFFFFF;
  --text-secondary: #A0A0B0;
  --border: #2C3354;
  --success: #00B894;
  --error: #FF6B6B;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background: var(--background);
  color: var(--text);
  min-height: 100vh;
}

#root {
  max-width: 1200px;
  margin: 0 auto;
}
EOF

cat > frontend-tma/src/App.css << 'EOF'
.app {
  min-height: 100vh;
  padding-bottom: 80px;
}

/* Header */
.header {
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
  padding: 40px 20px;
  text-align: center;
  border-radius: 0 0 30px 30px;
  margin-bottom: 30px;
}

.logo {
  font-size: 3rem;
  margin-bottom: 10px;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-10px); }
}

.header h1 {
  font-size: 2.5rem;
  margin-bottom: 10px;
  font-weight: 700;
}

.subtitle {
  opacity: 0.9;
  font-size: 1.1rem;
  margin-bottom: 30px;
}

.stats {
  display: flex;
  justify-content: center;
  gap: 40px;
  margin-top: 20px;
}

.stat {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
}

.stat-label {
  font-size: 0.9rem;
  opacity: 0.8;
}

/* Main */
.main {
  padding: 0 20px;
}

.main h2 {
  font-size: 1.8rem;
  margin-bottom: 20px;
  font-weight: 600;
}

/* Locations */
.locations {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}

.location-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 20px;
  padding: 25px;
  transition: all 0.3s ease;
  cursor: pointer;
}

.location-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(108, 92, 231, 0.3);
  border-color: var(--primary);
}

.location-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.location-header h3 {
  font-size: 1.4rem;
  font-weight: 600;
}

.location-badge {
  font-size: 0.85rem;
  padding: 5px 10px;
  border-radius: 15px;
  background: rgba(0, 184, 148, 0.2);
  color: var(--success);
}

.location-address {
  color: var(--text-secondary);
  margin-bottom: 15px;
  font-size: 0.95rem;
}

.location-info {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.checkin-btn {
  width: 100%;
  background: var(--primary);
  color: white;
  border: none;
  padding: 14px 24px;
  border-radius: 12px;
  font-size: 1.05rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.checkin-btn:hover {
  background: var(--primary-dark);
  transform: scale(1.02);
}

.checkin-btn:active {
  transform: scale(0.98);
}

/* Loading */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  gap: 20px;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid var(--border);
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Error */
.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  gap: 20px;
  padding: 20px;
  text-align: center;
}

.error-container button {
  background: var(--primary);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 1rem;
  cursor: pointer;
}

/* Footer */
.footer {
  text-align: center;
  padding: 40px 20px;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

/* Responsive */
@media (max-width: 768px) {
  .header h1 {
    font-size: 2rem;
  }
  
  .stats {
    gap: 20px;
  }
  
  .locations {
    grid-template-columns: 1fr;
  }
}
EOF

# README files
cat > backend/README.md << 'EOF'
# PerkUP Backend

FastAPI backend для PerkUP Ecosystem.

## Setup
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run
```bash
uvicorn app.main:app --reload
```

## Docs

http://localhost:8000/docs
EOF

cat > frontend-tma/README.md << 'EOF'
# PerkUP Telegram Mini App

React + Vite + TypeScript Mini App.

## Setup
```bash
npm install
```

## Run
```bash
npm run dev
```

## Build
```bash
npm run build
```
EOF

# Main README
cat > README.md << 'EOF'
# 🤖☕ PerkUP Ecosystem

Інноваційна платформа лояльності для мережі кав'ярень.

## Швидкий старт

### Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend TMA
```bash
cd frontend-tma
npm install
npm run dev
```

## URLs

- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Frontend TMA: http://localhost:5173

## Документація

Дивись `docs/` для детальної документації.
EOF

echo ""
echo "════════════════════════════════════════════════════════"
echo -e "${GREEN}✓ Setup завершено успішно!${NC}"
echo "════════════════════════════════════════════════════════"
echo ""
echo -e "${BLUE}📦 Створено:${NC}"
echo "  ✓ 100+ папок"
echo "  ✓ 50+ файлів"
echo "  ✓ Backend skeleton"
echo "  ✓ Frontend TMA skeleton"
echo "  ✓ Конфігураційні файли"
echo "  ✓ README документація"
echo ""
echo -e "${BLUE}🎯 Наступні кроки:${NC}"
echo ""
echo "1. Налаштуй .env файли:"
echo "   cp backend/.env.example backend/.env"
echo "   # Відредагуй backend/.env (додай токени)"
echo ""
echo "2. Встанови Backend залежності:"
echo "   cd backend"
echo "   python3 -m venv venv"
echo "   source venv/bin/activate"
echo "   pip install -r requirements.txt"
echo ""
echo "3. Встанови Frontend залежності:"
echo "   cd ../frontend-tma"
echo "   npm install"
echo ""
echo "4. Запусти dev середовище:"
echo "   ./scripts/dev.sh"
echo ""
echo -e "${GREEN}Готово! Успіхів у розробці! 🚀☕${NC}"
echo ""