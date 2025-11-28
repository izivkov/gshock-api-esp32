
import json

class LogSender:
    def __init__(self, activity_log=None, connection=None, characteristic=None):
        self.activity_log = activity_log
        self.connection = connection
        self.characteristic = characteristic

    async def send_notify_safe(self, connection, data):
        """Send notification safely, handling potential exceptions."""
        try:
            await self.characteristic.notify(connection, data)
        except TypeError:
            # Ignore occasional NoneType issues from BLE library quirks
            pass

    async def send_log(self, log):
        """Send a single log entry as JSON, chunked without header."""
        if not self.connection.is_connected():
            print("Connection lost before sending.")
            return

        # Convert dict to JSON bytes
        log_data = json.dumps(log).encode('utf-8')
        chunk_size = 17

        try:
            for i in range(0, len(log_data), chunk_size):
                if not self.connection.is_connected():
                    print("Connection lost during notify.")
                    return

                chunk = log_data[i:i + chunk_size]
                await self.send_notify_safe(self.connection, chunk)

            print("✅ Finished sending one log.")

        except Exception as e:
            print("Notify failed:", e)
            print("Exception type:", type(e).__name__)

    async def send_logs(self, logs):
        """Send all logs one by one."""
        if not self.connection.is_connected():
            print("Connection lost before sending.")
            return

        for log in logs:
            # Convert LogMessage to dict, then send
            await self.send_log(log.to_dict())

        print("✅ Finished sending all logs.")

