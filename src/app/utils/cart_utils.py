# src/app/utils/cart_utils.py

from typing import List, Dict, Tuple
from src.app.domain.models import ConfigurableProductDTO, OptionDTO, CartItemDTO

def calculate_item_price(product: ConfigurableProductDTO, selected_option_ids: List[int]) -> Tuple[float, List[OptionDTO]]:
    """
    Обчислює фінальну ціну одиниці товару з урахуванням базової ціни та вибраних опцій.
    Повертає фінальну ціну та список DTO вибраних опцій.
    """
    final_price = product.base_price
    selected_options_dtos: List[OptionDTO] = []
    
    # Мапа ID опції до DTO об'єкта
    available_options_map = {opt.id: opt for opt in product.available_options}
    
    for option_id in selected_option_ids:
        option = available_options_map.get(option_id)
        if option:
            final_price += option.extra_cost
            selected_options_dtos.append(option)
            
    # Гарантуємо, що ціна не менша за 0
    return max(0.00, final_price), selected_options_dtos

def get_selected_options_summary(options: List[OptionDTO]) -> str:
    """
    Формує текстове резюме вибраних опцій для відображення у повідомленні.
    Формат: [• Група: Опція (+ціна)]
    """
    if not options:
        return "Без додаткових опцій"
        
    grouped_options: Dict[str, List[str]] = {}
    
    for option in options:
        if option.option_group not in grouped_options:
            grouped_options[option.option_group] = []
        
        # Додаємо назву опції та її вартість (якщо вона не 0)
        cost_str = f" (+{option.extra_cost:.2f} грн)" if option.extra_cost > 0 else ""
        grouped_options[option.option_group].append(f"{option.name}{cost_str}")
        
    
    summary = []
    for group, names in grouped_options.items():
        summary.append(f"• **{group}**: {', '.join(names)}")
        
    return "\n".join(summary)
