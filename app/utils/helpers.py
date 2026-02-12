def format_date(value, format='%B %d, %Y'):
    """Custom helper to format date objects or strings."""
    if value:
        return value.strftime(format)
    return ""
