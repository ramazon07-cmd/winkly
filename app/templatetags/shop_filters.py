from django import template

register = template.Library()

@register.filter
def calc_discount(price, discount_price):
    try:
        price = float(price)
        discount_price = float(discount_price)
        if discount_price == 0 or discount_price >= price:
            return 0
        discount_percent = ((price - discount_price) / price) * 100
        return int(discount_percent)
    except (ValueError, TypeError):
        return 0

@register.filter
def split(value, delimiter):
    """
    Splits a string by the specified delimiter and returns a list.
    Usage: {{ value|split:"," }}
    """
    try:
        return value.split(delimiter)
    except (AttributeError, TypeError):
        return []
