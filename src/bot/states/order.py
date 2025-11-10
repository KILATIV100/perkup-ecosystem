# src/bot/states/order.py

from aiogram.fsm.state import State, StatesGroup

class OrderState(StatesGroup):
    """
    Стани для FSM (Finite State Machine) процесу оформлення замовлення.
    Використовується для зберігання поточного кошика.
    """
    # Стан, коли користувач переглядає категорії
    in_menu = State() 
    
    # Стан, коли користувач знаходиться в конкретній категорії
    in_category = State() 
    
    # Стан, коли користувач налаштовує напій/товар (вибір опцій)
    configuring_item = State() 
    
    # Стан, коли користувач переглядає та підтверджує кошик
    reviewing_cart = State() 
    
    # Стан, коли користувач вибирає час та спосіб оплати
    finalizing_order = State()
