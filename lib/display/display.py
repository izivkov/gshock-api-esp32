from machine import Pin, SPI, PWM
import display.st7789_ext as st7789
import gc

# Basic 8x8 font class for text rendering
class Font8x8:
    WIDTH = 8
    HEIGHT = 8

font_small = Font8x8  # Use 8x8 as small font
font_big = Font8x8    # Use upscaled_text for 'big' font effect

# Scaled font for larger text (1.5x)
class ScaledFont:
    WIDTH = int(Font8x8.WIDTH * 1.5)
    HEIGHT = int(Font8x8.HEIGHT * 1.5)

font_small_scaled = ScaledFont

# Display configuration for supported boards
DISPLAY_CONFIGS = {
    "ESP32-C6-LCD-1.47": {
        "width": 320,
        "height": 320,
        "sck": 7,
        "mosi": 6,
        "cs": 14,
        "dc": 15,
        "reset": 21,
        "backlight": 22,
        "spi_polarity": 1,
        "spi_phase": 1,
        "landscape": True,
        "mirror_x": True,
        "mirror_y": True,
        "inversion": False,
        "led_green": 12,
        "led_red": 13,
    },
    "ESP32-C6-Touch-LCD-1.47": {
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
        "landscape": True,
        "mirror_x": True,
        "mirror_y": True,
        "inversion": False,
        "led_green": 12,
        "led_red": 13,
    }
}

class Display:
    """
    Display driver and UI renderer for ESP32-C6 LCD boards.
    Supports text, battery, temperature, and status screens.
    """
    def __init__(self, board_type="ESP32-C6-Touch-LCD-1.47"):
        # Load configuration for selected board type
        cfg = DISPLAY_CONFIGS[board_type]

        # Initialize ST7789 TFT display with SPI and pin config
        self.tft = st7789.ST7789(
            SPI(1, baudrate=40000000, polarity=cfg["spi_polarity"], phase=cfg["spi_phase"],
                sck=Pin(cfg["sck"]), mosi=Pin(cfg["mosi"]), miso=Pin(cfg.get("miso")) if cfg.get("miso") else None),
            cfg["width"], cfg["height"],
            reset=Pin(cfg["reset"], Pin.OUT),
            dc=Pin(cfg["dc"], Pin.OUT),
            cs=Pin(cfg["cs"], Pin.OUT),
        )

        # Double initialization workaround for display after reboot
        self.tft.init(landscape=cfg["landscape"], mirror_x=cfg["mirror_x"], mirror_y=cfg["mirror_y"], inversion=cfg["inversion"])
        self.tft.init(landscape=cfg["landscape"], mirror_x=cfg["mirror_x"], mirror_y=cfg["mirror_y"], inversion=cfg["inversion"])

        # Backlight control via PWM
        backlight = Pin(cfg["backlight"], Pin.OUT)
        backlight.on()
        self.bl_pwm = PWM(backlight, freq=5000)

        # Foreground and background colors
        self.fg = self.to_tft_color(210, 230, 249)
        self.bg = self.to_tft_color(0, 0, 0)
        self.width = self.tft.width
        self.height = self.tft.height

        # Fill display with background color
        self.tft.fill(self.bg)

    def to_tft_color(self, r, g, b):
        """
        Convert RGB to TFT color format.
        """
        return self.tft.color(b, g, r)

    def set_brightness(self, percent):
        """
        Set backlight brightness (0-100%).
        """
        percent = max(0, min(100, percent))
        duty = int(percent * 1023 / 100)
        self.bl_pwm.duty(duty)

    def get_brightness(self):
        """
        Get current brightness as percent.
        """
        return int(self.bl_pwm.duty() * 100 / 1023)

    def display_data(self, data):
        """
        Display key/value pairs on the screen.
        Title row is centered and upscaled.
        """
        self.tft.fill(self.bg)
        gc.collect()
        line_gap = 6
        top_margin = 58
        left_margin = 20
        right_margin = 20
        current_y = top_margin

        try:
            for key, value in data:
                if key == "":
                    # Title row: centered, large font with upscaling
                    value_width = len(value) * font_big.WIDTH * 2  # expected upscaling
                    x = (self.width - value_width) // 2
                    self.tft.upscaled_text(x, current_y, value, self.fg, bgcolor=None, upscaling=2)
                    current_y += font_big.HEIGHT * 2 + line_gap
                else:
                    # Regular key/value row
                    key_width = len(key) * font_small.WIDTH
                    val_width = len(value) * font_small.WIDTH
                    self.tft.text(left_margin, current_y, key, self.fg, self.bg)
                    val_x = self.width - right_margin - val_width
                    self.tft.text(val_x, current_y, value, self.fg, self.bg)
                    current_y += font_small.HEIGHT + line_gap

        finally:
            gc.collect()

    def fill_rect_manual(self, x, y, width, height, color):
        """
        Draw a filled rectangle manually using horizontal lines.
        """
        for i in range(height):
            self.tft.hline(x, x + width - 1, y + i, color)

    def draw_battery_icon(self, percent, width=20, height=10, bottom_margin=50, right_margin=20):
        """
        Draw battery icon at bottom right, filled according to percent.
        """
        try:
            x = self.width - width - 3 - right_margin  
            y = self.height - height - bottom_margin
            # Battery outline
            self.tft.rect(x, y, width, height, self.fg, fill=False)
            # Battery terminal
            terminal_width = 3
            terminal_height = height // 2
            self.fill_rect_manual(
                x + width,
                y + (height - terminal_height) // 2,
                terminal_width,
                terminal_height,
                self.fg
            )
            # Battery fill
            fill_width = int((width - 2) * max(0, min(percent, 100)) / 100)
            if fill_width > 0:
                self.fill_rect_manual(x + 1, y + 1, fill_width, height - 2, self.fg)
            if fill_width < (width - 2):
                self.fill_rect_manual(x + 1 + fill_width, y + 1, (width - 2) - fill_width, height - 2, self.bg)
        finally:
            gc.collect()

    def draw_temperature(self, temperature, height=10, bottom_margin=50, left_margin=20):
        """
        Draw temperature value at bottom left.
        """
        try:
            temp_str = "{}C".format(temperature)
            x = left_margin
            y = self.height - height - bottom_margin
            self.tft.text(x, y, temp_str, self.fg, self.bg)
        finally:
            gc.collect()

    def show_welcome_screen(self, message, watch_name=None, last_sync=None):
        """
        Display welcome/status screen with watch name, last sync, and message.
        """
        try:
            margin_bottom = 80
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
                    # Upscaled text for emphasis
                    self.tft.upscaled_text(x, y, text, self.fg, bgcolor=None, upscaling=2)
                else:
                    self.tft.text(x, y, text, self.fg, self.bg)
                y += font_small.HEIGHT * scale + line_spacing
        finally:
            gc.collect()

    def show_message(self, message, max_line_len=20, bottom_margin=20):
        """
        Display a multi-line centered message, word-wrapped.
        """
        words = message.split()
        lines = []
        current_line = ""

        try:
            for word in words:
                # Check if adding word exceeds max length
                if len(current_line) + len(word) + (1 if current_line else 0) > max_line_len:
                    # Push current line and start new one
                    lines.append(current_line)
                    current_line = word
                else:
                    # Add word to current line
                    current_line = f"{current_line} {word}".strip()

            if current_line:
                lines.append(current_line)

            # Calculate total height for text block
            line_height = font_big.HEIGHT * 2  # upscaled 2x
            total_height = len(lines) * line_height + (len(lines) - 1) * 4  # 4 px line spacing

            # Center vertically with bottom margin respected
            y_start = (self.height - total_height - bottom_margin + 20) // 2

            self.tft.fill(self.bg)  # Clear display with background color

            # Draw each line centered horizontally and vertically spaced
            for i, line in enumerate(lines):
                line_width = len(line) * font_big.WIDTH * 2
                x = (self.width - line_width) // 2
                y = y_start + i * (line_height + 4)
                self.tft.upscaled_text(x, y, line, self.fg, bgcolor=None, upscaling=2)

        finally:
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