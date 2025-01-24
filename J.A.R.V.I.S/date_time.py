import datetime
from greeting import get_day_suffix # type: ignore

def current_date():
    now = datetime.datetime.now()
    day = now.day
    day_suffix = get_day_suffix(day)
    return now.strftime(f"%A, the {day}{day_suffix} of %B, %Y")

def current_time():
    return datetime.datetime.now().strftime("%I:%M %p")