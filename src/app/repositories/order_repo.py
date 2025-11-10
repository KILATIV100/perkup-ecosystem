# src/app/repositories/order_repo.py

from sqlalchemy.ext.asyncio import AsyncSession
from src.app.repositories.base_repo import BaseRepo
from src.db.models import Order, OrderItem
from src.app.domain.models import ShoppingCartDTO, CartItemDTO
from datetime import datetime

class OrderRepository(BaseRepo[Order]):
    """
    Репозиторій для роботи з сутністю Замовлення (Order) та його деталями.
    """
    def __init__(self, session: AsyncSession):
        super().__init__(session, Order)

    async def create_full_order(
        self, 
        cart: ShoppingCartDTO, 
        user_id: int, 
        pickup_time: datetime,
        payment_method: str,
        points_used: int = 0,
        points_earned: int = 0
    ) -> Order:
        """
        Створює та зберігає повний об'єкт Замовлення (Order)
        разом з усіма позиціями (OrderItems).
        """
        
        # 1. Створення основного об'єкта Order
        new_order = Order(
            user_id=user_id,
            location_id=cart.location_id,
            status='NEW',
            payment_method=payment_method,
            total_amount=cart.total_amount,
            total_paid=cart.total_amount, # Припустимо, що вся сума сплачена (без бонусів/знижок поки що)
            points_used=points_used,
            points_earned=points_earned,
            pickup_time=pickup_time
        )
        self.session.add(new_order)
        await self.session.flush() # Отримуємо ID нового замовлення
        
        # 2. Створення об'єктів OrderItem
        order_items = []
        for item in cart.items:
            # Формуємо рядок з ID опцій для фіксації в БД
            selected_options_ids_str = ",".join(str(opt.id) for opt in item.selected_options)
            
            order_item = OrderItem(
                order_id=new_order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.unit_price,
                selected_options=selected_options_ids_str,
            )
            order_items.append(order_item)

        self.session.add_all(order_items)
        
        # 3. commit має бути виконано на рівні Application Service або хендлера
        
        return new_order
