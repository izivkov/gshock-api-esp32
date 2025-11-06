import json
import gc
import uasyncio as asyncio
from time import localtime
from bluetooth import UUID


class LogMessage:
    def __init__(self, datetime, activity_name, status_code, message):
        self.datetime = datetime
        self.activity_name = activity_name
        self.status_code = status_code
        self.message = message

    def to_dict(self):
        return {
            'datetime': self.datetime,
            'activity_name': self.activity_name,
            'status_code': self.status_code,
            'message': self.message
    }

class ActivityLog:
    def __init__(self, max_size=10):
        self.logs = []
        self.max_size = max_size
        self._on_change = None  # callback function

    def set_on_change(self, callback):
        """Register callback (e.g. LogSender.on_new_log)."""
        print("ActivityLog: setting on_change callback")
        self._on_change = callback

    def add_log(self, activity_name, status_code, message, datetime=None):
        print(f"ActivityLog: adding log - {activity_name}, {status_code}, {message}, {datetime} on_change={self._on_change}")   
        if datetime is None:
            datetime = localtime()[:6]
        log_message = LogMessage(datetime, activity_name, status_code, message)
        self.logs.append(log_message)

        if len(self.logs) > self.max_size:
            self.logs.pop(0)

        # Notify LogSender if a callback is set
        if self._on_change:
            self._on_change()

    def clear_logs(self):
        self.logs.clear()
        if self._on_change:
            self._on_change()

    def to_json(self):
        dict_list = [log.to_dict() for log in self.logs]
        return json.dumps(dict_list)
    
activity_log = ActivityLog()
