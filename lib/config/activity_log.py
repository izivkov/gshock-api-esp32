import json
from time import localtime

class LogMessage:
    def __init__(self, datetime, activity_name, status_code, message):
        self.datetime = datetime  # tuple (year, month, day, hour, minute, second)
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

    def add_log(self, activity_name, status_code, message, datetime=None):
        if datetime is None:
            datetime = localtime()[:6]
        log_message = LogMessage(datetime, activity_name, status_code, message)
        self.logs.append(log_message)
        # Maintain FIFO, trim oldest if exceeded max_size

        if len(self.logs) > self.max_size:
            self.logs.pop(0)

    def get_logs(self):
        return self.logs

    def clear_logs(self):
        self.logs.clear()

    def to_json(self):
        dict_list = [log.to_dict() for log in self.logs]
        return json.dumps(dict_list)

activity_log = ActivityLog()
