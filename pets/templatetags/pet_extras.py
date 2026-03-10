from django import template

register = template.Library()

@register.filter
def is_equal(value, arg):
    """
    Compares two values as strings and returns True if they are equal.
    Used to bypass IDE formatters that aggressively strip spaces around '=='.
    Treats None as an empty string for form matching.
    """
    val_str = '' if value is None else str(value)
    arg_str = '' if arg is None else str(arg)
    return val_str == arg_str
