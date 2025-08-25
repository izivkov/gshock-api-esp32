from machine import Pin, SPI
import display.st7789_ext as st7789
import gc

# If you want custom fonts, you should define their WIDTH and HEIGHT attributes.
# For this demo, we'll use the built-in 8x8 font. You can extend as needed.
class Font8x8:
    WIDTH = 8
    HEIGHT = 8

font_small = Font8x8  # Use 8x8 as small font
font_big = Font8x8    # Use upscaled_text for 'big' font effect

class Display:
    def __init__(self):
        print(f"Display:__init__ called...")

        # Set your display dimensions and SPI pins here:
        self.tft = st7789.ST7789(
            SPI(1, baudrate=40000000, phase=1, polarity=1, sck=Pin(7), mosi=Pin(6)),
            320, 320,
            reset=Pin(21, Pin.OUT),
            dc=Pin(15, Pin.OUT),
            cs=Pin(14, Pin.OUT),
        )

        self.tft.init(landscape=True, mirror_y=True, inversion=True)

        backlight = Pin(22, Pin.OUT)
        backlight.on()

        self.fg = self.tft.color(255, 255, 255)
        self.bg = self.tft.color(0, 0, 0)
        self.width = self.tft.width
        self.height = self.tft.height

        fgcolor = self.tft.color(255,0,0)
        bgcolor = self.tft.color(0,0,0)  

        self.tft.fill(bgcolor)  # Fill with black
        print(f"end of __init__...")

    def display_data(self, data):
        
        print("display_data called...")

        self.tft.fill(self.bg)
        gc.collect()
        print("Free memory:", gc.mem_free())
        line_gap = 6
        top_margin = 50
        left_margin = 20
        right_margin = 20
        current_y = top_margin

        for key, value in data:
            if key == "":
                # Title row: centered, large font with upscaling
                value_width = len(value) * font_big.WIDTH * 2  # expected upscaling
                x = (self.width - value_width) // 2
                
                # self.tft.upscaled_text(x, current_y, value, self.fg, bgcolor=self.bg, upscaling=2)

                self.tft.upscaled_text(x, current_y, value, self.fg, bgcolor=None, upscaling=2)
                # self.tft.upscaled_text(val_x, y, value, fgcolor, bgcolor=None, upscaling=2)

                current_y += font_big.HEIGHT * 2 + line_gap
            else:
                # Regular key/value row
                key_width = len(key) * font_small.WIDTH
                val_width = len(value) * font_small.WIDTH
                self.tft.text(left_margin, current_y, key, self.fg, self.bg)
                val_x = self.width - right_margin - val_width
                self.tft.text(val_x, current_y, value, self.fg, self.bg)
                current_y += font_small.HEIGHT + line_gap
        gc.collect()

    def draw_battery_icon(self, percent, width=20, height=10, top_margin=50, right_margin=20):
        # x = self.width - width - 3 - right_margin  
        # y = self.height - height - top_margin
        # # Battery outline
        # self.tft.rect(x, y, width, height, self.fg, fill=False)
        # # Battery terminal
        # terminal_width = 3
        # terminal_height = height // 2
        # self.tft.fill_rect(
        #     x + width,
        #     y + (height - terminal_height) // 2,
        #     terminal_width,
        #     terminal_height,
        #     self.fg
        # )
        # # Battery fill
        # fill_width = int((width - 2) * max(0, min(percent, 100)) / 100)
        # if fill_width > 0:
        #     self.tft.fill_rect(x + 1, y + 1, fill_width, height - 2, self.fg)
        # if fill_width < (width - 2):
        #     self.tft.fill_rect(x + 1 + fill_width, y + 1, (width - 2) - fill_width, height - 2, self.bg)
        # gc.collect()

        pass

    def draw_temperature(self, temperature, height=10, top_margin=50, left_margin=20):
        temp_str = "{}C".format(temperature)
        x = left_margin
        y = self.height - height - top_margin
        self.tft.text(x, y, temp_str, self.fg, self.bg)
        gc.collect()

    def show_welcome_screen(self, message, watch_name=None, last_sync=None):
        gc.collect()
        print("Free memory:", gc.mem_free())
        margin_bottom = 130
        line_spacing = 4
        lines = []
        if watch_name is not None:
            short_name = ' '.join(watch_name.strip().split()[1:])
            lines.append((f"{short_name}", 2))
        lines.append((f"", 1))
        lines.append(("Last Synced:", 2))
        lines.append((last_sync, 2))
        lines.append((f"", 1))
        lines.append((message, 1))
        line_heights = [font_small.HEIGHT * scale for _, scale in lines]
        total_text_height = sum(line_heights) + line_spacing * (len(lines) - 1)
        start_y = self.height - total_text_height - margin_bottom
        self.tft.fill(self.bg)
        y = start_y
        for i, (text, scale) in enumerate(lines):
            text_w = len(text) * font_small.WIDTH * scale
            x = (self.width - text_w) // 2
            if scale > 1:
                
                # self.tft.upscaled_text(x, y, text, self.fg, self.bg, upscaling=scale)
                self.tft.upscaled_text(x, y, text, self.fg, bgcolor=None, upscaling=2)

            else:
                self.tft.text(x, y, text, self.fg, self.bg)
            y += font_small.HEIGHT * scale + line_spacing
        gc.collect()

# Example usage
data = [
    ("", "GW-5600"),
    ("Next Alarm:", "6:45"),
    ("Rem:", "Meet for breakfast"),
    ("TimeZone:", "America/Toronto"),
    ("Last Update", "18:30"),
]

display = Display()
# display.display_data(data)
