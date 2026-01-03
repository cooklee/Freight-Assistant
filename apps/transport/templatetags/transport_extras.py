from django import template

register = template.Library()


@register.filter
def minutes_to_hm(value):
    """
    Convert minutes to 'Xh Ym'.
    Usage: {{ minutes|minutes_to_hm }}
    """
    if value in (None, ""):
        return "0h 0m"

    try:
        minutes = int(value)
    except (TypeError, ValueError):
        return "0h 0m"

    hours = minutes // 60
    mins = minutes % 60
    return f"{hours}h {mins}m"
