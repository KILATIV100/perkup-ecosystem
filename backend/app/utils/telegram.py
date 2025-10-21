import hmac
import hashlib
import json
import time
from urllib.parse import parse_qs
from typing import Optional

def validate_telegram_init_data(init_data: str, bot_token: str) -> Optional[dict]:
    """
    Валідація initData від Telegram Web App
    https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app
    """
    try:
        parsed = parse_qs(init_data)
        hash_value = parsed.get('hash', [None])[0]
        
        if not hash_value:
            return None
        
        # Створюємо data_check_string
        check_items = []
        for key in sorted(parsed.keys()):
            if key != 'hash':
                check_items.append(f"{key}={parsed[key][0]}")
        data_check_string = '\n'.join(check_items)
        
        # Створюємо secret_key
        secret_key = hmac.new(
            "WebAppData".encode(),
            bot_token.encode(),
            hashlib.sha256
        ).digest()
        
        # Перевіряємо hash
        calculated_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        if calculated_hash != hash_value:
            return None
        
        # Перевіряємо auth_date (не старіше 24 годин)
        auth_date = int(parsed.get('auth_date', [0])[0])
        if time.time() - auth_date > 86400:
            return None
        
        # Парсимо user data
        user_data = json.loads(parsed.get('user', ['{}'])[0])
        return user_data
        
    except Exception as e:
        print(f"Validation error: {e}")
        return None