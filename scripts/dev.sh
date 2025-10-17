#!/bin/bash

echo "🚀 Запуск PerkUP Dev Environment..."

# Запуск backend
osascript -e 'tell app "Terminal"
    do script "cd ~/Documents/perkup-ecosystem/backend && source venv/bin/activate && uvicorn app.main:app --reload"
end tell'

# Невелика затримка
sleep 2

# Запуск frontend
osascript -e 'tell app "Terminal"
    do script "cd ~/Documents/perkup-ecosystem/frontend-tma && npm run dev"
end tell'

echo "✅ Сервіси запущені в нових Terminal вікнах!"
