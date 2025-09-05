import uasyncio as asyncio

class PeriodicTaskRunner:
    """
    Runs a provided function periodically in the background.
    Optionally blocks until the first execution completes.
    """
    def __init__(self, func, interval_sec=86400, run_immediately=True):
        self.func = func
        self.interval_sec = interval_sec
        self.run_immediately = run_immediately
        self._task = None
        self._first_run_done = asyncio.Event()

    async def _run(self):
        if self.run_immediately:
            await self._maybe_await(self.func)
            self._first_run_done.set()
        else:
            self._first_run_done.set()
        while True:
            await asyncio.sleep(self.interval_sec)
            await self._maybe_await(self.func)

    async def _maybe_await(self, func):
        result = func()
        if hasattr(result, "__await__"):
            await result

    async def start(self, block_until_first_run=False):
        if self._task is None:
            self._task = asyncio.create_task(self._run())
        if block_until_first_run:
            await self._first_run_done.wait()

    def stop(self):
        if self._task:
            self._task.cancel()
            self._task = None