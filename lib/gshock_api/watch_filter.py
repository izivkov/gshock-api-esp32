import time

import time

class WatchFilter:
    def __init__(self, time_constrained_watches=None):
        if time_constrained_watches is None:
            time_constrained_watches = []
        # Sanitize input on initialization, lower case and strip whitespace
        self.excluded_names = set(name.strip().lower() for name in time_constrained_watches)
        self.last_connected_times = {}

    def connection_filter(self, watch_name):
        watch_name = watch_name.strip().lower()
        print(f"---> connection_filter: watch_name: [{watch_name}], excluded_names: {self.excluded_names}")

        if watch_name not in self.excluded_names:
            print(f"----> WatchFilter: {watch_name} not in excluded list, allow")
            return True

        last_time = self.last_connected_times.get(watch_name)
        now = time.time()

        if last_time is None:
            print(f"----> WatchFilter: {watch_name} connected for the first time, allow")
            return True

        elapsed = now - last_time
        if elapsed > 6 * 3600:
            print(f"----> WatchFilter: {watch_name} connected {elapsed} seconds ago - allow")
            return True

        print(f"----> WatchFilter: {watch_name} connected {elapsed} seconds ago - deny")
        return False

    def update_connection_time(self, watch_name):
        self.last_connected_times[watch_name.strip()] = time.time()
