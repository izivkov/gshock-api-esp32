from machine import Pin, SPI,  PWM
import st7789_ext

# Example key-value data
data = [
    ('Temp', '25°C'),
    ('Pressure', '1013hPa'),
    ('Humidity', '60%'),
    ('Home Towen', 'Toronto'),
    ('Last Update', '18:30')
]

# Display dimensions (landscape)
WIDTH = 320
HEIGHT = 172

# Create an SPI object (update SPI id and pins as needed for your board)
spi = SPI(1, baudrate=40000000, polarity=0, phase=0,
          sck=Pin(18), mosi=Pin(23), miso=None)

# Initialize display (update pins as per your setup)
display = st7789_ext.ST7789(
    SPI(1, baudrate=40000000, phase=1, polarity=1, sck=Pin(7), mosi=Pin(6)),
    320, 320,
    reset=Pin(21, Pin.OUT),
    dc=Pin(15, Pin.OUT),
    cs=Pin(14, Pin.OUT),
)

display.init(landscape=True, mirror_y=True, inversion=True)

backlight = Pin(22, Pin.OUT)
backlight.on()
# backlight = Pin(5,Pin.OUT)
# backlight.on()

fgcolor = display.color(255,0,0)
bgcolor = display.color(0,0,0)

display.fill(bgcolor)  # Fill with black

font_height = 24
key_x = WIDTH // 2 - 10    # Adjust for font/length
val_x = WIDTH // 2 + 10
gap = 10 


def display_data(data):
    display.fill(bgcolor)  # Clear the display with background color
    for i, (key, value) in enumerate(data):
        y = i * font_height + 40
        key_width = len(key) * 8
        key_x = WIDTH // 2 - gap - key_width - 70  # Right-justify before center
        val_x = WIDTH // 2 + gap + 20               # Left-justify after center

        display.upscaled_text(key_x, y, key, fgcolor, bgcolor=None, upscaling=2)
        display.upscaled_text(val_x, y, value, fgcolor, bgcolor=None, upscaling=2)

