import json
import os
from time import localtime

LOG_FILE = "activity_log.json"

class LogMessage:
    def __init__(self, datetime, activity_name, status_code, watch_name, message):
        self.datetime = datetime
        self.activity_name = activity_name
        self.status_code = status_code
        self.message = message
        self.watch_name = watch_name

    def to_dict(self):
        return {
            'datetime': self.datetime,
            'activity_name': self.activity_name,
            'status_code': self.status_code,
            'message': self.message,
            'watch_name': self.watch_name
        }

class ActivityLog:
    def __init__(self, max_size=50, filepath=LOG_FILE):
        self.logs = []
        self.max_size = max_size
        self.filepath = filepath
        self._on_add = None
        self._load()

    def _file_exists(self, path):
        try:
            os.stat(path)
            return True
        except OSError:
            return False

    def _load(self):
        try:
            if self._file_exists(self.filepath):
                with open(self.filepath, 'r') as f:
                    data = json.load(f)
                self.logs = [LogMessage(**entry) for entry in data]
                print("Loaded {} log entries from flash.".format(len(self.logs)))
        except Exception as e:
            print("Failed to load activity log: {}".format(e))
            self.logs = []

    def _save(self):
        try:
            with open(self.filepath, 'w') as f:
                json.dump([log.to_dict() for log in self.logs], f)
        except Exception as e:
            print("Failed to save activity log: {}".format(e))

    def set_on_add(self, callback):
        """Register callback (e.g. BLE sender)."""
        print("ActivityLog: setting on_add callback")
        self._on_add = callback

    async def add_log(self, activity_name, status_code, message, watch_name, datetime=None):
        if datetime is None:
            datetime = localtime()[:6]

        log_message = LogMessage(datetime, activity_name, status_code, watch_name, message)
        self.logs.append(log_message)

        if len(self.logs) > self.max_size:
            self.logs.pop(0)

        self._save()

        if self._on_add:
            await self._on_add(log_message)

    def get_logs(self):
        """Return a copy of all logs."""
        return self.logs[:]

    def pop_log(self):
        """Pop the oldest log (FIFO). Returns None if empty."""
        if self.logs:
            return self.logs.pop(0)
        return None

    def clear_logs(self):
        """Clear all logs."""
        self.logs.clear()
        self._save()

activity_log = ActivityLog()
