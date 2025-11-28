
from time import localtime

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
    def __init__(self, max_size=10):
        self.logs = []               # FIFO queue of unsent logs
        self.max_size = max_size
        self._on_add = None

    def set_on_add(self, callback):
        """Register callback (e.g. BLE sender)."""
        print("ActivityLog: setting on_add callback")
        self._on_add = callback

    async def add_log(self, activity_name, status_code, message, watch_name, datetime=None):
        if datetime is None:
            datetime = localtime()[:6]

        log_message = LogMessage(datetime, activity_name, status_code, watch_name, message)
        self.logs.append(log_message)

        # Keep logs within max_size (oldest first)
        if len(self.logs) > self.max_size:
            self.logs.pop(0)

        # Trigger callback
        if self._on_add:
            await self._on_add(log_message)

    def get_logs(self):
        """Return a copy of all unsent logs (for initial sync)."""
        return self.logs[:]

    def pop_log(self):
        """Pop the oldest log (FIFO). Returns None if empty."""
        if self.logs:
            return self.logs.pop(0)
        return None

    def clear_logs(self):
        """Clear all logs (used if BLE client requests wipe)."""
        self.logs.clear()

activity_log = ActivityLog(max_size=10)