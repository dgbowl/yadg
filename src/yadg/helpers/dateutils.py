import datetime

def coerceDashedDate(ds):
    dt = datetime.datetime.strptime(ds, "%Y-%m-%d-%H-%M-%S")
    #year, month, day, hour, minute, second = [int(j) for j in ds.split("-")]
    #dt = datetime.datetime(year, month, day, hour=hour, minute=minute, second=second)
    return dt.timestamp()

def coerceDateTime(ds):
    #dt = datetime.datetime.strptime(ds, "%m/%d/%Y %H:%M:%S %p")
    # print(ds)
    date, time, noon = ds.split()
    month, day, year = [int(each) for each in date.split("/")]
    hour, minute, second = [int(each) for each in time.split(":")]
    if noon == "PM" and hour < 12:
        hour += 12
    elif noon == "AM" and hour == 12:
        hour = 0
    dt = datetime.datetime(year, month, day, hour=hour, minute=minute, second=second)
    return dt.timestamp()

def coerceStringDate(ds):
    dt = datetime.datetime.strptime(ds, "%d %b %Y %H:%M")
    return dt.timestamp()

def now(asstr=False):
    dt = datetime.datetime.now()
    if asstr:
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    else:
        return dt.timestamp()
