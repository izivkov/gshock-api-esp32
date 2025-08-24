
from machine import Pin, SPI, PWM
import display.st7789py as st7789


TFA = 0
BFA = 0
WIDE = 1
TALL = 0
SCROLL = 0      # orientation for scroll.py
FEATHERS = 1    # orientation for feathers.py

# POWER = Pin(46, Pin.OUT, value=1)

def config(rotation=0):
    """
    Configures and returns an instance of the ST7789 display driver.

    Args:
        rotation (int): The rotation of the display (default: 0).

    Returns:
        ST7789: An instance of the ST7789 display driver.
    """

    spi = SPI(
        1,
        baudrate=40_000_000,
        polarity=1,
        phase=1,
        sck=Pin(7),
        mosi=Pin(6),
        miso=None,
    )

    display = st7789.ST7789(
        spi,
        240, 320,                         # physical driver size
        reset=Pin(21, Pin.OUT),
        dc=Pin(15, Pin.OUT),
        cs=Pin(14, Pin.OUT),
    )

    backlight = PWM(Pin(22), freq=1000)
    backlight.duty_u16(65535)  # full brightness

    return display