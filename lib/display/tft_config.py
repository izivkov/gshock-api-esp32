
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

    # custom_rotations = (
    #     (0x00, 170, 320, 35, 0, False),
    #     (0x60, 320, 170, 0, 35, False),
    #     (0xC0, 170, 320, 35, 0, False),
    #     (0xA0, 320, 170, 0, 35, False),
    # )

    # return st7789.ST7789(
    #     SPI(2, baudrate=40000000, sck=Pin(12), mosi=Pin(11), miso=None),
    #     170,
    #     320,
    #     cs=Pin(10, Pin.OUT),
    #     dc=Pin(13, Pin.OUT),
    #     reset=Pin(9, Pin.OUT),
    #     backlight=Pin(15, Pin.OUT),
    #     custom_rotations=custom_rotations,
    #     rotation=rotation,
    #     color_order=st7789.BGR,
    # )

    spi = SPI(
        1,
        baudrate=40_000_000,
        polarity=1,
        phase=1,
        sck=Pin(7),
        mosi=Pin(6),
        miso=None,
    )

    display =  st7789.ST7789(
        spi,
        240, 320,                         # physical driver size
        reset=Pin(21, Pin.OUT),
        dc=Pin(15, Pin.OUT),
        cs=Pin(14, Pin.OUT),
    )

    backlight = PWM(Pin(22), freq=1000)
    backlight.duty_u16(65535)  # full brightness

    return display