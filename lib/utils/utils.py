def format_time(t):
    # Format: Weekday, Month Day Year, HH:MM:SS
    formatted_time = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
        t[0], t[1], t[2],  # year, month, day
        t[3], t[4], t[5]   # hour, minute, second
    )

    return formatted_time

