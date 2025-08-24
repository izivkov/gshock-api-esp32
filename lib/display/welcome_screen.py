import machine
import time
import gc
import lib.display.st7789_base as st7789_base

# Initialize SPI and control pins (adjust pins for your setup)
spi = machine.SPI(1, baudrate=40000000, polarity=1, phase=1,
                  sck=machine.Pin(7), mosi=machine.Pin(6))
reset_pin = machine.Pin(21, machine.Pin.OUT)
dc_pin = machine.Pin(15, machine.Pin.OUT)
cs_pin = machine.Pin(14, machine.Pin.OUT)

# Initialize ST7789 display driver instance (240x240 example)
tft = st7789_base.ST7789_base(spi, 240, 320, reset=reset_pin, dc=dc_pin, cs=cs_pin)

# Initialize the display
tft.init()

# Clear the display with black color
tft.fill(0)

# You can use FONT_Default, or load your own font compatible with the driver
font = tft.FONT_Default

# Define text lines to display
lines = [
    "Welcome to ST7789!",
    "MicroPython test",
    "antirez/st7789_mpy",
]

# Draw each line vertically spaced
y = 10
for line in lines:
    # Calculate width to center text horizontally
    text_width = len(line) * font.WIDTH
    x = (tft.width - text_width) // 2
    # Draw text: font, string, x, y, foreground color (white), background color (black)
    tft.text(font, line, x, y, 0xFFFF, 0x0000)
    y += font.HEIGHT + 5  # Move down for next line

# Show framebuffer on the display
tft.show()

gc.collect()

# Keep running so the display retains the image
while True:
    time.sleep(1)
