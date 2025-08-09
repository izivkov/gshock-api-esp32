import time

class Logger:
    def __init__(self, log_level=20):
        # log_level can be 10=DEBUG, 20=INFO, 30=WARNING, 40=ERROR
        self.log_level = log_level
        self.level_names = {
            10: "DEBUG",
            20: "INFO",
            30: "WARNING",
            40: "ERROR"
        }

    def _should_log(self, level):
        return level >= self.log_level

    def _print(self, level, *args):
        if self._should_log(level):
            t = time.localtime()
            timestamp = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
                t[0], t[1], t[2], t[3], t[4], t[5]
            )
            level_name = self.level_names.get(level, "INFO")
            print("{} LOGGER {}:".format(timestamp, level_name), *args)
    
    def error(self, *args):
        self._print(40, *args)

    def info(self, *args):
        self._print(20, *args)

    def debug(self, *args):
        self._print(10, *args)

    def warn(self, *args):
        self._print(30, *args)

    def warning(self, *args):
        self.warn(*args)

logger = Logger()
