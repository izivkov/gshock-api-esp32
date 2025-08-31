
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
        pass 

    def set_color(self, r, g, b):
        pass

    def turn_off(self):
        pass
    def set_mode(self, mode):
        pass
    def red_on(self):
        pass
    def green_on(self):
        pass

    def blue_on(self):
        pass

    def white_on(self):
        pass

    async def _run(self):
        pass

led = LEDController(pin=8, num_leds=1)  # Initialize with pin 8 and 1 LED