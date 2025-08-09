import uasyncio as asyncio
from gshock_api.exceptions import GShockConnectionError

class CancelableResult:
    def __init__(self, timeout=10.0):
        self._timeout = timeout
        self._result = None
        self._done = False
        self._event = asyncio.Event()

    async def get_result(self):
        try:
            await asyncio.wait_for(self._event.wait(), self._timeout)
            return self._result
        except asyncio.TimeoutError as e:
            if not self._done:
                self._result = ''
                self._done = True
            raise GShockConnectionError("Timeout occurred waiting for response from the watch") from e

    def set_result(self, result):
        if not self._done:
            self._result = result
            self._done = True
            self._event.set()
