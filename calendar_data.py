import calendar
import datetime

calendar.setfirstweekday(calendar.SUNDAY)

def get_today_date_string():
    today = datetime.date.today()
    return [today.year, today.month, today.day]

def get_month_names():
    return calendar.month_name

def get_days_of_month_of_year(year, month):
    return calendar.monthcalendar(year, month)