# src/bot/states/order.py

from aiogram.fsm.state import State, StatesGroup

class OrderState(StatesGroup):
    """
    Стани для FSM (Finite State Machine) процесу оформлення замовлення.
    """
    in_menu = State() 
    in_category = State() 
    configuring_item = State() 
    reviewing_cart = State() 
    finalizing_order = State()
    
class ProfileState(StatesGroup):
    """
    Стани для FSM процесу керування профілем.
    """
    # Стан для відображення профілю
    main = State() 
    # Стан очікування введення або кнопки "Поділитися контактом"
    waiting_for_phone = State()
