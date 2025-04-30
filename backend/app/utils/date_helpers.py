"""
Date helper utilities for report generation.
"""
from datetime import date, datetime, time, timedelta
from typing import List, Optional, Tuple


def get_date_range(days: int) -> Tuple[datetime, datetime]:
    """
    Get date range from today going back specified number of days.
    
    Args:
        days: Number of days to go back
        
    Returns:
        Tuple[datetime, datetime]: Start and end datetime
    """
    end_date = datetime.combine(date.today(), time.max)
    start_date = datetime.combine(date.today() - timedelta(days=days), time.min)
    return start_date, end_date


def get_week_date_range() -> Tuple[datetime, datetime]:
    """
    Get date range for the current week (Monday to Sunday).
    
    Returns:
        Tuple[datetime, datetime]: Start and end datetime
    """
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    
    start_datetime = datetime.combine(start_of_week, time.min)
    end_datetime = datetime.combine(end_of_week, time.max)
    
    return start_datetime, end_datetime


def get_month_date_range() -> Tuple[datetime, datetime]:
    """
    Get date range for the current month.
    
    Returns:
        Tuple[datetime, datetime]: Start and end datetime
    """
    today = date.today()
    start_of_month = date(today.year, today.month, 1)
    
    # Calculate end of month
    if today.month == 12:
        end_of_month = date(today.year + 1, 1, 1) - timedelta(days=1)
    else:
        end_of_month = date(today.year, today.month + 1, 1) - timedelta(days=1)
    
    start_datetime = datetime.combine(start_of_month, time.min)
    end_datetime = datetime.combine(end_of_month, time.max)
    
    return start_datetime, end_datetime


def format_date_for_display(date_obj: date) -> str:
    """
    Format date for display in reports.
    
    Args:
        date_obj: Date object
        
    Returns:
        str: Formatted date string
    """
    return date_obj.strftime("%B %d, %Y")


def format_datetime_for_display(datetime_obj: datetime) -> str:
    """
    Format datetime for display in reports.
    
    Args:
        datetime_obj: Datetime object
        
    Returns:
        str: Formatted datetime string
    """
    return datetime_obj.strftime("%B %d, %Y %I:%M %p")


def get_date_ranges_for_dropdown() -> List[dict]:
    """
    Get date range options for dropdown menus.
    
    Returns:
        List[dict]: List of date range options
    """
    today = date.today()
    
    return [
        {"label": "Today", "start": datetime.combine(today, time.min), "end": datetime.combine(today, time.max)},
        {"label": "Yesterday", "start": datetime.combine(today - timedelta(days=1), time.min), "end": datetime.combine(today - timedelta(days=1), time.max)},
        {"label": "Last 7 days", "start": datetime.combine(today - timedelta(days=6), time.min), "end": datetime.combine(today, time.max)},
        {"label": "Last 30 days", "start": datetime.combine(today - timedelta(days=29), time.min), "end": datetime.combine(today, time.max)},
        {"label": "This week", "start": get_week_date_range()[0], "end": get_week_date_range()[1]},
        {"label": "This month", "start": get_month_date_range()[0], "end": get_month_date_range()[1]},
    ]


def parse_date_string(date_string: str) -> Optional[date]:
    """
    Parse date string in various formats.
    
    Args:
        date_string: Date string
        
    Returns:
        Optional[date]: Parsed date or None if invalid
    """
    formats = [
        "%Y-%m-%d",       # 2023-11-15
        "%d/%m/%Y",       # 15/11/2023
        "%m/%d/%Y",       # 11/15/2023
        "%B %d, %Y",      # November 15, 2023
        "%d %B %Y",       # 15 November 2023
        "%Y%m%d",         # 20231115
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_string, fmt).date()
        except ValueError:
            continue
    
    return None