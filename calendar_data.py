import calendar
import datetime

calendar.setfirstweekday(calendar.SUNDAY)

def get_today_date():
    return datetime.date.today()

def get_month_names():
    month_names = []
    for month in range(1, 13):
        month_names.append(calendar.month_name[month])
    return month_names

def get_month_data(year, month):
    return calendar.monthcalendar(year, month)

def get_month_range(year, month):
    # returns (weekday of first day of month, days in the month)
    # the weekday numbers are: 0 = MONDAY, 1 = TUESDAY, ..., 6 = SUNDAY
    return calendar.monthrange(year, month)

def get_day_names():
    day_names = []
    for day in range(0, 7):
        day_names.append(calendar.day_name[day])
    day_names.insert(0, day_names.pop(6))
    return day_names