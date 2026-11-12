"""Helper functions for K&G Farms"""
from datetime import datetime, date
import random
import string


def generate_receipt_number():
    """Generate unique receipt number like KGF-20240115-A3B7"""
    date_part = datetime.now().strftime('%Y%m%d')
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"KGF-{date_part}-{random_part}"


def generate_tag_id(prefix="KG"):
    """Generate unique animal tag ID"""
    random_part = ''.join(random.choices(string.digits, k=6))
    return f"{prefix}-{random_part}"


def format_currency(amount, symbol="NGN"):
    """Format number as currency"""
    if amount is None:
        return f"{symbol} 0.00"
    return f"{symbol} {amount:,.2f}"


def format_date(dt):
    """Format date nicely"""
    if not dt:
        return "-"
    if isinstance(dt, datetime):
        return dt.strftime("%b %d, %Y %I:%M %p")
    return dt.strftime("%b %d, %Y")


def calculate_age_display(months):
    """Convert months to readable age"""
    if not months:
        return "Unknown"
    if months < 12:
        return f"{months} month{'s' if months != 1 else ''}"
    years = months // 12
    rem_months = months % 12
    if rem_months == 0:
        return f"{years} year{'s' if years != 1 else ''}"
    return f"{years}y {rem_months}m"


def calculate_weeks_display(weeks):
    """Convert weeks to readable age"""
    if not weeks:
        return "Unknown"
    if weeks < 4:
        return f"{weeks} week{'s' if weeks != 1 else ''}"
    months = weeks // 4
    rem_weeks = weeks % 4
    if rem_weeks == 0:
        return f"{months} month{'s' if months != 1 else ''}"
    return f"{months}mo {rem_weeks}w"
