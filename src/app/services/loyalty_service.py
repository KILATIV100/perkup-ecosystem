# src/app/services/loyalty_service.py
# Асинхронний клієнт для Poster POS API

import httpx
from loguru import logger
from typing import Dict, Any, Optional
from src.app.config import settings

# Додайте httpx до requirements.txt: httpx==0.27.*

class PosterLoyaltyService:
    """
    Клієнт для Poster POS API (Loyalty та Clients endpoints).
    Вся комунікація Poster відбувається через цей клас.
    """
    def __init__(self):
        self._base_url = settings.POSTER_API_BASE_URL
        self._access_token = settings.POSTER_ACCESS_TOKEN
        self._domain = settings.POSTER_ACCOUNT_DOMAIN
        
        # Використовуємо httpx для асинхронних HTTP-запитів
        self._client = httpx.AsyncClient(
            base_url=f"{self._base_url}/{self._domain}",
            params={"token": self._access_token},
            timeout=10.0
        )

    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Загальний метод для виконання HTTP-запитів до API."""
        try:
            response = await self._client.request(method, endpoint, **kwargs)
            response.raise_for_status() # Генерує виняток для 4xx/5xx статусів
            
            data = response.json()
            if data.get("response"):
                return data["response"]
            
            logger.warning(f"Poster API returned empty or unexpected response for {endpoint}: {data}")
            return None
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Poster API HTTP error on {endpoint}: {e.response.status_code}, {e.response.text}")
            return None
        except httpx.RequestError as e:
            logger.error(f"Poster API Request error on {endpoint}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in Poster API call to {endpoint}: {e}")
            return None

    # --- 1. Керування Клієнтами (Loyalty ID, Balance) ---
    
    async def get_client_info(self, phone_number: str) -> Optional[Dict[str, Any]]:
        """
        Знаходить клієнта за номером телефону та повертає його дані, включаючи баланс бонусів.
        API Endpoint: /clients.getClient (припускаючи, що Poster підтримує пошук за телефоном)
        :param phone_number: Номер телефону у форматі Poster (напр., +380991234567)
        """
        # Очищуємо номер телефону для пошуку
        cleaned_phone = re.sub(r'\D', '', phone_number).lstrip('38')
        
        endpoint = "clients.getClient"
        data = await self._make_request(
            "GET", endpoint, params={"phone": cleaned_phone}
        )

        if data and data.get("client"):
            # Припускаємо, що API повертає баланс бонусів
            client_data = data["client"]
            return {
                "is_registered": True,
                "client_id": client_data.get("client_id"),
                "bonus_balance": int(client_data.get("points", 0)), # 'points' - умовна назва поля
                "full_name": client_data.get("name")
            }
        
        return {"is_registered": False, "bonus_balance": 0}

    # --- 2. Операції Лояльності (Імітація) ---
    
    async def spend_points(self, phone_number: str, amount: int) -> bool:
        """
        Списання бонусів через Poster API.
        API Endpoint: loyalty.spendPoints (Умовний)
        """
        logger.info(f"Attempting to SPEND {amount} points for client {phone_number} via Poster API.")
        
        # У реальній інтеграції це вимагає: 
        # 1. Створення замовлення (order.createOrder). 
        # 2. Передача client_id та discount/bonus amount у Payload.
        # 3. Закриття замовлення (order.closeOrder).
        
        # Для MVP: Припускаємо успіх, якщо кількість > 0
        if amount > 0:
            return True
        return False

    async def accrue_points(self, phone_number: str, total_amount: float) -> bool:
        """
        Нарахування бонусів через Poster API.
        API Endpoint: loyalty.accruePoints (Умовний)
        """
        logger.info(f"Attempting to ACCRUE points for client {phone_number} after purchase of {total_amount}.")
        # У реальній інтеграції це відбувається автоматично при закритті замовлення,
        # якщо клієнт ID був переданий.
        return True
    
    # --- 3. Керування Замовленням ---
    
    async def create_poster_order(self, order_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Створення замовлення в Poster POS.
        API Endpoint: /incomingOrders.createIncomingOrder
        """
        endpoint = "incomingOrders.createIncomingOrder"
        # order_data має містити Spot ID, Cash Drawer ID, список продуктів, ID клієнта, тощо.
        
        # Додаємо обов'язкові поля з конфігурації
        order_data["spot_id"] = settings.POSTER_SPOT_ID
        order_data["cash_register_id"] = settings.POSTER_CASH_DRAWER_ID
        
        response = await self._make_request("POST", endpoint, json=order_data)
        
        if response and response.get("order_id"):
            logger.success(f"Poster Order created with ID: {response['order_id']}")
            return response
        return None
