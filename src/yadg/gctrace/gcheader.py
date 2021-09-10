import datetime

def _coerceDateTime(ds):
#    11/29/2018 4:30:24 PM
    date, time, noon = ds.split()
    month, day, year = [int(each) for each in date.split("/")]
    hour, minute, second = [int(each) for each in time.split(":")]
    if noon == "PM":
        hour += 12
    dt = datetime.datetime(year, month, day, hour=hour, minute=minute, second=second)
    return(dt.timestamp())

def process(fn):
    lines = open(fn, "r", encoding="utf8",  errors='ignore').read lines()
    ver = lines.pop(0).split(":")[1].strip()
    channels = int(lines.pop(0).split(":")[1].strip())
    ID = lines.pop(0).split(":")[1].strip()
    origfn = lines.pop(0)
    method = lines.pop(0)
    user = lines.pop(0)
    timedate = lines.pop(0)
    print(timedate)
    print(user)
    timedate = timedate.split("Time:")[1]
    samplerate = lines.pop(0).split(":")[1].split()[0:-1]
    ndet = len(samplerate)
    points = [int(each) for each in lines.pop(0).split(":")[1].split()[0:-1]]
    xunits = [each.strip() for each in lines.pop(0).split(":")[1].split()]
    yunits = lines.pop(0)
    xmuls = [float(each) for each in lines.pop(0).split(":")[1].split()]
    ymuls = [float(each) for each in lines.pop(0).split(":")[1].split()]
    if len(points) != len(xunits) != len(xmuls) != len(ymuls) != ndet:
        print("Wrong number of detectors in GC ascii file: \n{0:s} \nAborting.".format(fn))
    data = {"version": ver, "channels": channels, "ID": ID, "fn": origfn,
            "method": method, "user": user,
            "uts": _coerceDateTime(timedate)}
    print(timedate)
    print(_coerceDateTime(timedate))
    for i in range(ndet):
        x = []
        y = []
        dt = 60 if xunits[i] == "Minutes" else 1
        for ii in range(points[i]):
            x.append(ii * xmuls[i] * dt / samplerate[i])
            y.append(float(lines.pop(0).strip()) * ymuls[i])
        data["det_{0:d}".format(i+1)] = {"samplerate": samplerate[i],
                                         "points": points[i],
                                         "xmult": xmuls[i],
                                         "ymult": ymuls[i],
                                         "x": x, "y": y}
    return(data)
        
