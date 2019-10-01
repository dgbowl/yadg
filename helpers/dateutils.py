import datetime

def coerceDashedDate(ds):
    year, month, day, hour, minute, second = [int(j) for j in ds.split("-")]
    dt = datetime.datetime(year, month, day, hour=hour, minute=minute, second=second)
    return dt.timestamp()

def coerceDateTime(ds):
    date, time, noon = ds.split()
    month, day, year = [int(each) for each in date.split("/")]
    hour, minute, second = [int(each) for each in time.split(":")]
    if noon == "PM" and hour < 12:
        hour += 12
    elif noon == "AM" and hour == 12:
        hour = 0
    dt = datetime.datetime(year, month, day, hour=hour, minute=minute, second=second)
    return dt.timestamp()

def now():
    dt = datetime.datetime.now()
    return dt.timestamp()
