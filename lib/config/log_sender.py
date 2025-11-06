import uasyncio as asyncio
import json

class LogSender:
    def __init__(self, activity_log=None, connection=None):
        self.activity_log = activity_log
        self.activity_log.set_on_change(self.on_new_log)
        self.connection = connection
        self._send_requested = False  # flag used instead of Queue
        self._sending = False         # to avoid overlapping sends

    async def start(self):
        """Background coroutine that waits for send requests."""
        while True:
            if self._send_requested and not self._sending:
                self._send_requested = False
                await self._send_logs_internal()
            await asyncio.sleep_ms(100)  # avoid busy loop

    def on_new_log(self):
        """Callback when a new log entry is added."""
        print("New log added, scheduling send_logs...")
        self._send_requested = True  # set flag; main loop picks it up

    async def _send_logs_internal(self):
        """Performs the BLE write safely in one async context."""
        self._sending = True
        try:
            log_data = self.activity_log.to_json()
            log_bytes = log_data.encode('utf-8')

            length_bytes = len(log_bytes).to_bytes(4, 'big')
            print("Sending log length:", len(log_bytes))

            await self.connection.write_logs(0xAA, length_bytes)

            start = 0
            chunk_size = 17
            while start < len(log_bytes):
                chunk = log_bytes[start:start + chunk_size]
                print("Sending chunk:", chunk)
                await self.connection.write_logs(0xAA, chunk)
                start += chunk_size
        except Exception as e:
            print("Error while sending logs:", e)
        finally:
            self._sending = False
