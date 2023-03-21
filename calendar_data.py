import calendar
import datetime

calendar.setfirstweekday(calendar.SUNDAY)

def get_today_date_string():
    today = datetime.date.today()
    return [today.year, today.month, today.day]

def get_month_names():
    return calendar.month_name

def get_days_of_month_of_year(year, month):
    """Return a matrix representing a month's calendar. 
    Each row represents a week; days outside this month are zero.

    Args:
        year (int): year of month
        month (int): month in question

    Returns:
        list: list of lists
    """
    return calendar.monthcalendar(year, month)

def get_first_week(year, month):
    """Get list of the week which includes the first of the supplied month where
    days outside the month are 0.  i.e. if the first is on tuesday, would return
    [0, 0, 1, 2, 3, 4, 5]

    Args:
        year (int): year
        month (int): month

    Returns:
        list: list of days of the week containing the 1st of the month
    """
    return calendar.monthcalendar(year, month)[0]

def get_last_week(year, month):
    """Return list of the week which includes the last day of the supplied month
    where days outside the month are 0.

    Args:
        year (int): year
        month (int): month

    Returns:
        list: list of days of the week containing the last day of the month
    """
    return calendar.monthcalendar(year, month).pop()

def get_adj_months(year, month):
    """Return list containing (previous month and year) and (next month and year)

    Args:
        year (int): current year
        month (int): current month

    Returns:
        list: [(year of previous month, previous month), 
        (year of next month, next month)]
    """
    prev_y = year
    prev_m = month - 1
    next_y = year
    next_m = month + 1
    if month == 1:
        prev_m = 12
        prev_y - 1
    elif month == 12:
        next_m = 1
        next_y + 1
    return [(prev_y, prev_m), (next_y, next_m)]