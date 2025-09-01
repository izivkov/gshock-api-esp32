from machine import Pin, SPI
import display.st7789_ext as st7789
import time

"""ESP32-C6-Touch-LCD-1.47": {
        "width": 320,
        "height": 240,
        "sck": 1,
        "mosi": 2,
        "miso": 3,
        "cs": 14,
        "dc": 15,
        "reset": 22,
        "backlight": 23,
        "spi_polarity": 1,
        "spi_phase": 1,
    }
"""

spi = SPI(1, baudrate=40000000, polarity=1, phase=1, sck=Pin(1), mosi=Pin(2), miso=Pin(3))
rst = Pin(22, Pin.OUT)
rst.off()
time.sleep_ms(50)
rst.on()
time.sleep_ms(50)

tft = st7789.ST7789(
    spi, 172, 320,
    reset=rst, dc=Pin(15, Pin.OUT), cs=Pin(14, Pin.OUT),
)
tft.init(landscape=True, mirror_x=True, mirror_y=True, inversion=False)
tft.init(landscape=True, mirror_x=True, mirror_y=True, inversion=False)

bl = Pin(23, Pin.OUT)

bl.on()
time.sleep_ms(100)
tft.fill(tft.color(255,0,0))  
# Red background – should always show on first run
