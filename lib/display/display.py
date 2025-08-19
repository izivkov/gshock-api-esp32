import display.st7789py as st7789
import display.tft_config as tft_config
import display.vga2_8x16 as font_small
import display.vga2_bold_16x32 as font_big  # larger font for title
import gc

class Display:
    def __init__(self):
        self.tft = tft_config.config(tft_config.WIDE)
        self.tft.rotation(3)  # 0=0°, 1=90°, 2=180°, 3=270°
        self.tft.fill(0)  # clear screen

        self.fg = st7789.color565(255, 255, 255)
        self.bg = st7789.color565(0, 0, 0)
        
    # --------------------------------------------------------------------
    def display_data(self, data):
        """
        Display a list of (key, value) tuples on the screen.
        If a key is empty, the value is centered and uses a bigger font.
        """

        # Clear display
        self.tft.fill(self.bg)  # fill with background color
        gc.collect()

        # layout parameters
        line_gap = 6
        top_margin = 50
        left_margin = 20
        right_margin = 20

        current_y = top_margin

        for key, value in data:
            if key == "":
                # Title row: centered, large font
                font = font_big
                value_width = len(value) * font.WIDTH
                x = (self.tft.width - value_width) // 2
                self.tft.text(font, value, x, current_y, self.fg, self.bg)
                current_y += font.HEIGHT + line_gap
            else:
                # Regular key/value row: left/right-aligned
                font = font_small
                self.tft.text(font, key, left_margin, current_y, self.fg, self.bg)

                value_width = len(value) * font.WIDTH
                val_x = self.tft.width - right_margin - value_width
                self.tft.text(font, value, val_x, current_y, self.fg, self.bg)

                current_y += font.HEIGHT + line_gap
        
    def draw_battery_icon(self, percent, width=20, height=10, top_margin=50, right_margin=20):
        """
        Draws a battery icon at the bottom-right corner with a margin.
        - percent: battery fill percentage (0–100)
        - width, height: battery size
        - margin: space from edges
        """

        # Compute bottom-right coordinates
        x = self.tft.width - width - 3 - right_margin  
        y = self.tft.height - height - top_margin

        # --- Battery outline ---
        self.tft.rect(x, y, width, height, self.fg)

        # --- Battery terminal (on right side) ---
        terminal_width = 3
        terminal_height = height // 2
        self.tft.fill_rect(
            x + width,
            y + (height - terminal_height) // 2,
            terminal_width,
            terminal_height,
            self.fg
        )

        # --- Battery fill ---
        fill_width = int((width - 2) * max(0, min(percent, 100)) / 100)

        if fill_width > 0:
            self.tft.fill_rect(x + 1, y + 1, fill_width, height - 2, self.fg)

        if fill_width < (width - 2):
            self.tft.fill_rect(x + 1 + fill_width, y + 1, (width - 2) - fill_width, height - 2, self.bg)
            
    def draw_temperature(self, temperature, font=font_small, height=10, top_margin=50, left_margin=20):
        """
        Draws the temperature with degree symbol at the bottom-left corner.
        - temperature: numeric temperature value
        - font: font to use for text
        - bottom_margin: space from bottom edge
        - left_margin: space from left edge
        """
        # temp_str = "{}\u00B0C".format(temperature)  # Unicode degree symbol
        temp_str = "{}C".format(temperature)  # Unicode not supported by this simple font.

        # Compute position
        x = left_margin
        y = self.tft.height - height - top_margin

        self.tft.text(font, temp_str, x, y, self.fg, self.bg)

    def show_welcome_screen(self, message, watch_name=None, last_sync=None):
        """
        Display a multi-line welcome message directly on ST7789 screen.
        Lines are horizontally centered, stacked from bottom upwards.
        If watch_name and last_sync are provided, they appear above the message.
        Each line can store its own font.
        """
        margin_bottom = 40       # Bottom margin in pixels
        line_spacing = 4         # Pixels between lines

        # Compose all lines (store as tuples: (text, font))
        lines = []
        if watch_name is not None:
            short_name = ' '.join(watch_name.strip().split()[1:])
            lines.append((f"{short_name}", font_big))  

        lines.append((f"", font_small))  
        lines.append(("Last Synced:", font_big)) 
        lines.append((last_sync, font_big)) 
        lines.append((f"", font_small))  
        lines.append((message, font_small)) 

        # Measure width/height of each line based on its font
        line_widths = [len(text) * f.WIDTH for text, f in lines]
        line_heights = [f.HEIGHT for _, f in lines]

        total_text_height = sum(line_heights) + line_spacing * (len(lines) - 1)

        # Compute vertical starting point (bottom-aligned)
        start_y = self.tft.height - total_text_height - margin_bottom

        # Clear screen first (black background)
        self.tft.fill(self.bg)

        # Draw all lines centered using their own font
        y = start_y
        for i, (text, f) in enumerate(lines):
            text_w = line_widths[i]
            x = (self.tft.width - text_w) // 2  # center horizontally
            self.tft.text(f, text, x, y, self.fg, self.bg)
            y += f.HEIGHT + line_spacing
        
    # --------------------------------------------------------------------
    # Example usage
    data = [
        ("", "GW-5600"),
        ("Next Alarm:", "6:45"),
        ("Rem:", "Meet for breakfast"),
        ("TimeZone:", "America/Toronto"),
        ("Last Update", "18:30"),
    ]

# display_data(data)
display = Display()
