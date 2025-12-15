"""Helper utilities"""

import random
import string


def generate_referral_code(length: int = 8) -> str:
    """
    Generate a unique referral code.

    Args:
        length: Length of the referral code

    Returns:
        Random alphanumeric string
    """
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=length))
