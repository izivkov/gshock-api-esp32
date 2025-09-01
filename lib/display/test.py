from machine import Pin, SPI
import display.st7789_ext as st7789
import time

spi = SPI(1, baudrate=40000000, polarity=1, phase=1, sck=Pin(7), mosi=Pin(6))
rst = Pin(22, Pin.OUT)
rst.off()
time.sleep_ms(50)
rst.on()
time.sleep_ms(50)
tft = st7789.ST7789(
    spi, 172, 320,
    reset=rst, dc=Pin(15, Pin.OUT), cs=Pin(14, Pin.OUT),
)
tft.init(landscape=True, inversion=True)  # Remove all mirroring for test
bl = Pin(23, Pin.OUT)
bl.on()
time.sleep_ms(100)
tft.fill(tft.color(255,0,0))  # Red background – should always show on first run
