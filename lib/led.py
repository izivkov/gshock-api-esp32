import uasyncio as asyncio
from machine import Pin
import neopixel

class LEDController:
    MODE_OFF = 0
    MODE_SMOOTH = 1
    MODE_BLINK_GREEN = 2
    MODE_BLINK_RED = 3
    MODE_SOLID_RED = 4
    MODE_SOLID_GREEN = 5
    MODE_SOLID_BLUE = 6
    MODE_SOLID_WHITE = 7

    def __init__(self, pin=8, num_leds=1):
        self.np = neopixel.NeoPixel(Pin(pin), num_leds)
        self.mode = self.MODE_OFF
        self.running = True

        # Define the colors in **RGB order**
        rgb_colors = [
            (255, 0, 0),    # Red
            (0, 255, 0),    # Green
            (0, 0, 255),    # Blue
            (255, 255, 0),  # Yellow
            (0, 255, 255),  # Cyan
            (255, 0, 255),  # Magenta
            (255, 255, 255) # White
        ]

        # Convert RGB -> GRB for the NeoPixel
        self.colors = [(g, r, b) for (r, g, b) in rgb_colors]

        # Named colors
        self.red_color = self.colors[0]
        self.green_color = self.colors[1]
        self.blue_color = self.colors[2]
        self.white_color = self.colors[6]

        # Start the internal async loop automatically
        asyncio.create_task(self._run())

    def set_color(self, r, g, b):
        self.np[0] = (r, g, b)
        self.np.write()

    def turn_off(self):
        self.set_color(0, 0, 0)

    def set_mode(self, mode):
        """Set LED mode from outside"""
        self.mode = mode

    # ------------------------------
    # NEW helper methods for manual solid colors
    # ------------------------------
    def red_on(self):
        """Force red solid, ignores mode loop"""
        self.set_color(*self.red_color)

    def green_on(self):
        self.set_color(*self.green_color)

    def blue_on(self):
        self.set_color(*self.blue_color)

    def white_on(self):
        self.set_color(*self.white_color)

    # ------------------------------
    # Async mode runner
    # ------------------------------
    async def _run(self):
        step_time = 0.02  # Smooth transition time per step

        while self.running:
            if self.mode == self.MODE_OFF:
                self.turn_off()
                await asyncio.sleep(0.1)

            elif self.mode == self.MODE_SMOOTH:
                # Smooth transition between colors
                for i in range(len(self.colors)):
                    start = self.colors[i]
                    end = self.colors[(i + 1) % len(self.colors)]
                    steps = int(1 / step_time)  # 1 second per transition
                    for step in range(steps):
                        if self.mode != self.MODE_SMOOTH:
                            break
                        r = int(start[0] + (end[0] - start[0]) * step / steps)
                        g = int(start[1] + (end[1] - start[1]) * step / steps)
                        b = int(start[2] + (end[2] - start[2]) * step / steps)
                        self.set_color(r, g, b)
                        await asyncio.sleep(step_time)

            elif self.mode == self.MODE_BLINK_GREEN:
                self.set_color(*self.green_color)
                await asyncio.sleep(0.01)
                self.turn_off()
                await asyncio.sleep(2.99)

            elif self.mode == self.MODE_BLINK_RED:
                self.set_color(*self.red_color)
                await asyncio.sleep(0.1)
                self.turn_off()
                await asyncio.sleep(0.1)

            elif self.mode == self.MODE_SOLID_RED:
                self.set_color(*self.red_color)

            elif self.mode == self.MODE_SOLID_GREEN:
                self.set_color(*self.green_color)

            elif self.mode == self.MODE_SOLID_BLUE:
                self.set_color(*self.blue_color)

            elif self.mode == self.MODE_SOLID_WHITE:
                self.set_color(*self.white_color)

led = LEDController(pin=8, num_leds=1)  # Initialize with pin 8 and 1 LED