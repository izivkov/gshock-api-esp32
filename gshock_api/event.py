import json
import time

class EventDate:
    def __init__(self, year, month, day):
        self.year = year
        self.month = month
        self.day = day

    def to_json(self):
        return {"year": self.year, "month": self.month, "day": self.day}

    def equals(self, event_date):
        return (
            event_date.year == self.year and
            event_date.month == self.month and
            event_date.day == self.day
        )

    def __str__(self):
        return "year: {}, month: {}, day: {}".format(self.year, self.month, self.day)

class RepeatPeriod:
    NEVER = "NEVER"
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    YEARLY = "YEARLY"

class Event:
    def __init__(self):
        self.title = ""
        self.start_date = None
        self.end_date = None
        self.repeat_period = RepeatPeriod.NEVER
        self.days_of_week = None
        self.enabled = False
        self.incompatible = False
        self.selected = False

    def __str__(self):
        return (
            "Title: {}, startDate: {}, endDate: {}, repeatPeriod: {}, daysOfWeek: {},"
            " enabled: {}, incompatible: {}, selected: {}".format(
                self.title,
                str(self.start_date),
                str(self.end_date),
                self.repeat_period,
                self.days_of_week,
                self.enabled,
                self.incompatible,
                self.selected
            )
        )

    def create_event(self, event_json):
        def string_to_repeat_period(repeat_period_str):
            rp = repeat_period_str.lower()
            if rp == "daily":
                return RepeatPeriod.DAILY
            elif rp == "weekly":
                return RepeatPeriod.WEEKLY
            elif rp == "monthly":
                return RepeatPeriod.MONTHLY
            elif rp == "yearly":
                return RepeatPeriod.YEARLY
            else:
                return RepeatPeriod.NEVER

        time_obj = event_json.get("time", {})
        self.title = event_json.get("title", "")
        
        # Expecting start_date and end_date as dicts with year, month, day
        sd = time_obj.get("start_date")
        if sd:
            self.start_date = EventDate(sd.get("year"), sd.get("month"), sd.get("day"))
        else:
            self.start_date = None

        ed = time_obj.get("end_date")
        if ed:
            self.end_date = EventDate(ed.get("year"), ed.get("month"), ed.get("day"))
        else:
            self.end_date = self.start_date

        self.days_of_week = time_obj.get("daysOfWeek")  # Keep as-is
        self.enabled = bool(time_obj.get("enabled", False))
        self.incompatible = bool(time_obj.get("incompatible", False))
        self.selected = bool(time_obj.get("selected", True))
        self.repeat_period = string_to_repeat_period(time_obj.get("repeat_period", "never"))
        return self

    def to_json(self):
        time_json = {
            "repeat_period": self.repeat_period,
            "daysOfWeek": self.days_of_week,
            "enabled": self.enabled,
            "incompatible": self.incompatible,
            "selected": self.selected,
            "start_date": self.start_date.to_json() if self.start_date else None,
            "end_date": self.end_date.to_json() if self.end_date else None
        }
        event_json = {
            "title": self.title,
            "time": time_json
        }
        return event_json

def create_event_date(time_s, zone=None):
    # MicroPython datetime is limited; ignoring zone
    tm = time.localtime(time_s)
    return EventDate(tm[0], tm[1], tm[2])
