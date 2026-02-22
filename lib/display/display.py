from machine import Pin, SPI, PWM
import display.st7789_ext_small as st7789
import gc
import utime

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

        self._clock_x = None      # x position of the time on the current screen
        self._clock_y = None      # y position of the time on the current screen
        self._clock_active = False  # True when a live clock line is displayed

        # Fill display with background color
        self.tft.fill(self.bg)

    def set_colors(self, fg, bg):
        """
        Set foreground and background colors.
        Colors are RGB tuples (0-255).
        """
        self.fg = self.to_tft_color(*fg)
        self.bg = self.to_tft_color(*bg)
    
    def decimal_to_rgb(self, decimal_color):
        r = (decimal_color >> 16) & 0xFF
        g = (decimal_color >> 8) & 0xFF
        b = decimal_color & 0xFF
        return (r, g, b)
    

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

    def draw_temperature(self, temperature, temperature_unit, height=10, bottom_margin=50, left_margin=20):
        """
        Draw temperature value at bottom left.
        """
        try:
            if temperature_unit == "F":
                temp_str = "{}F".format(round(temperature + 32 * 9 / 5))
            else:   
                temp_str = "{}C".format(temperature)
            x = left_margin
            y = self.height - height - bottom_margin
            self.tft.text(x, y, temp_str, self.fg, self.bg)
        finally:
            gc.collect()

    def show_welcome_screen(self, message, watches=None, timezone=None, version=None, project_name=None):
        """
        Display welcome/status screen.
        - No watches yet: message split across two 2x lines, timezone on a third line, all centered.
          Version shown 1x right-aligned on the first line.
        - Watches present: compact 1x list with message header and version right-aligned.
        """
        try:
            self.tft.fill(self.bg)
            line_h = font_small.HEIGHT + 4  # 12px per row

            if not watches:
                # Split message at last space before midpoint
                mid = len(message) // 2
                split = message.rfind(" ", 0, mid + 1)
                if split == -1:
                    split = message.find(" ", mid)
                line1 = message[:split] if split != -1 else message
                line2 = message[split + 1:] if split != -1 else ""

                t = utime.localtime()
                time_str = "{:02}:{:02}".format(t[3], t[4])

                small_h = font_small.HEIGHT + 6
                row_h = font_small.HEIGHT * 2 + 6
                block_h = small_h + row_h * 2 + (small_h if timezone else 0) + (small_h if version else 0)
                y = (self.height - block_h) // 2

                # Current time — store position for live updates
                self._clock_x = (self.width - len(time_str) * font_small.WIDTH) // 2
                self._clock_y = y
                self._clock_active = True
                self.tft.text(self._clock_x, y, time_str, self.fg, self.bg)
                y += small_h

                for line in (line1, line2):
                    x = (self.width - len(line) * font_small.WIDTH * 2) // 2
                    self.tft.upscaled_text(x, y, line, self.fg, bgcolor=None, upscaling=2)
                    y += row_h

                if timezone:
                    x = (self.width - len(timezone) * font_small.WIDTH) // 2
                    self.tft.text(x, y, timezone, self.fg, self.bg)
                    y += small_h

                if version:
                    ver_str = "v{}".format(version)
                    x = (self.width - len(ver_str) * font_small.WIDTH) // 2
                    self.tft.text(x, y, ver_str, self.fg, self.bg)
            else:
                y = 40
                # Line 1: project name (left) | time (centre-right) | version (right)
                t = utime.localtime()
                time_str = "{:02}:{:02}".format(t[3], t[4])
                ver_str = "v{}".format(version) if version else ""
                ver_x = self.width - 10 - len(ver_str) * font_small.WIDTH
                time_x = ver_x - (len(time_str) + 1) * font_small.WIDTH
                self._clock_x = time_x
                self._clock_y = y
                self._clock_active = True
                if project_name:
                    self.tft.text(10, y, project_name, self.fg, self.bg)
                self.tft.text(time_x, y, time_str, self.fg, self.bg)
                if ver_str:
                    self.tft.text(ver_x, y, ver_str, self.fg, self.bg)
                y += line_h

                # Message on second line, centered
                msg_w = len(message) * font_small.WIDTH
                x = (self.width - msg_w) // 2
                self.tft.text(x, y, message, self.fg, self.bg)
                y += line_h + 2

                # Separator line
                self.fill_rect_manual(10, y, self.width - 20, 1, self.fg)
                y += 6

                # Watch list — most recent entries if too many to fit
                max_rows = (self.height - 20 - y) // line_h
                watch_items = list(watches.items())
                if len(watch_items) > max_rows:
                    watch_items = watch_items[-max_rows:]

                for name, sync_time in watch_items:
                    self.tft.text(10, y, name, self.fg, self.bg)
                    time_w = len(sync_time) * font_small.WIDTH
                    self.tft.text(self.width - 10 - time_w, y, sync_time, self.fg, self.bg)
                    y += line_h
        finally:
            gc.collect()

    def update_clock(self):
        """Redraw only the time at its stored position. No-op on any other screen."""
        if not self._clock_active or self._clock_y is None or self._clock_x is None:
            return
        t = utime.localtime()
        time_str = "{:02}:{:02}".format(t[3], t[4])
        self.tft.text(self._clock_x, self._clock_y, time_str, self.fg, self.bg)

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