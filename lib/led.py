from machine import Pin
import neopixel
import time

# Initialize NeoPixel on GPIO 8 with 1 LED
np = neopixel.NeoPixel(Pin(8), 1)

def set_color(r, g, b):
    np[0] = (r, g, b)
    np.write()

colors = [
    (255, 0, 0),    # Red
    (0, 255, 0),    # Green
    (0, 0, 255),    # Blue
    (255, 255, 0),  # Yellow
    (0, 255, 255),  # Cyan
    (255, 0, 255),  # Magenta
    (255, 255, 255) # White
]

while True:
    for color in colors:
        set_color(*color)
        time.sleep(1)
