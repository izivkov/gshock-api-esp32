import time

class WatchFilter:
    def __init__(self, exclude_names):
        self.exclude_names = set(exclude_names)
        self.last_connected_times = {}

    def connection_filter(self, watch_name):
        if watch_name not in self.exclude_names:
            return True
        last_time = self.last_connected_times.get(watch_name, None)
        if last_time is None:
            return True
        now = time.time()
        if now - last_time > 6 * 3600:  # 6 hours
            self.update_connection_time(watch_name=watch_name)
            return True
        return False

    def update_connection_time(self, watch_name):
        self.last_connected_times[watch_name] = time.time()
