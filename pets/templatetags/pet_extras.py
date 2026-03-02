from django import template

register = template.Library()

@register.filter
def is_equal(value, arg):
    """
    Compares two values as strings and returns True if they are equal.
    Used to bypass IDE formatters that aggressively strip spaces around '=='.
    """
    return str(value) == str(arg)
