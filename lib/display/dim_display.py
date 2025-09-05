import uasyncio as asyncio
from machine import PWM, Pin
import time
from lib.display.display import display

class DimDisplay:

    timeout_dim = 5 * 60      # 5 minutes to dim
    timeout_off = 30 * 60     # 30 minutes to turn off

    def __init__(self, display, touch):
        self.display = display                     # Display object with set_brightness method
        self.touch = touch                         # Touch object or callback
        self._task = None                          # The main asyncio task
        self._dimmed = False
        self._off = False

    async def _run(self):
        while True:
            # Start full brightness
            self.display.set_brightness(100)
            self._dimmed = False
            self._off = False

            dim_at = time.time() + self.timeout_dim          # 5 minutes
            off_at = time.time() + self.timeout_off        # 30 minutes

            while True:
                await asyncio.sleep(0.1)
                # Check for touch
                if self.touch.read():
                    if self._dimmed or self._off:
                        self.display.set_brightness(100)
                        self._dimmed = False
                        self._off = False
                    dim_at = time.time() + self.timeout_dim
                    off_at = time.time() + self.timeout_off
                now = time.time()
                if not self._dimmed and now >= dim_at:
                    self.display.set_brightness(10)  # Dimmed (set brightness as needed)
                    self._dimmed = True
                if not self._off and now >= off_at:
                    self.display.set_brightness(0)   # Off
                    self._off = True
                # If backlight is off, only power on at touch
                if self._off and self.touch.read():
                    self.display.set_brightness(100)
                    self._dimmed = False
                    self._off = False
                    dim_at = time.time() + self.timeout_dim
                    off_at = time.time() + self.timeout_off

    def start(self):
        """Start the dimming task. Set threshold based on your touch hardware."""
        if self._task is None:
            self._task = asyncio.create_task(self._run())

    def stop(self):
        if self._task:
            self._task.cancel()
            self._task = None

