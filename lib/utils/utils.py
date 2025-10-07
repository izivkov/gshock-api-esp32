def format_time(t):
    # Format: Weekday, Month Day Year, HH:MM:SS
    formatted_time = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
        t[0], t[1], t[2],  # year, month, day
        t[3], t[4], t[5]   # hour, minute, second
    )

    return formatted_time

def format_time(t, timeformat="24H"):
    hour = t[3]  # tm_hour
    minute = t[4]  # tm_min
    second = t[5]  # tm_sec

    if timeformat == "24H":  # 24-hour format
        if second == 0:
            return "{:02d}:{:02d}".format(hour, minute)
        else:
            return "{:02d}:{:02d}:{:02d}".format(hour, minute, second)
    else:  # 12-hour format
        postfix = 'AM'
        h = hour
        if hour == 0:
            h = 12
        elif hour == 12:
            postfix = 'PM'
        elif hour > 12:
            h = hour - 12
            postfix = 'PM'
        if second == 0:
            return "{}:{:02d} {}".format(h, minute, postfix)
        else:
            return "{}:{:02d}:{:02d} {}".format(h, minute, second, postfix)

def format_month_day(t, order="MM:DD"):
    month = t[1]  # tm_mon
    day = t[2]    # tm_mday

    if order == "MM/DD":
        return f"{month:02d}/{day:02d}"
    elif order == "DD/MM":
        return f"{day:02d}/{month:02d}"
    else:
        raise ValueError("order must be 'MM/DD' or 'DD/MM'")


