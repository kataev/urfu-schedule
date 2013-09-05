import datetime


def get_date_point(date=None):
    if date is None:
        date = datetime.datetime.utcnow()
    if 6 <= date.month <= 12:
        semester = 1
    else:
        semester = 2
    semi = 1
    week, day = date.isocalendar()[1:]
    return semester, semi, week, day