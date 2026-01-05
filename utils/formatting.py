def format_number(value, decimals=2):
    """Format a number with commas and specified decimals."""
    if value is None:
        return "-"
    try:
        return f"{float(value):,.{decimals}f}"
    except (ValueError, TypeError):
        return str(value)

def format_percentage(value, decimals=1):
    """Format a number as a percentage."""
    if value is None:
        return "-"
    try:
        return f"{float(value) * 100:.{decimals}f}%"
    except (ValueError, TypeError):
        return str(value)
