import display.st7789py as st7789
import display.tft_config as tft_config
import display.vga2_8x16 as font_small
import display.vga2_bold_16x32 as font_big  # larger font for title

# --------------------------------------------------------------------
def display_data(data):
    """
    Display a list of (key, value) tuples on the screen.
    If a key is empty, the value is centered and uses a bigger font.
    """
    tft = tft_config.config(tft_config.WIDE)
    tft.rotation(3)  # 0=0°, 1=90°, 2=180°, 3=270°
    tft.fill(0)  # clear screen

    fg = st7789.color565(255, 255, 255)
    bg = st7789.color565(0, 0, 0)

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
            x = (tft.width - value_width) // 2
            tft.text(font, value, x, current_y, fg, bg)
            current_y += font.HEIGHT + line_gap
        else:
            # Regular key/value row: left/right-aligned
            font = font_small
            tft.text(font, key, left_margin, current_y, fg, bg)

            value_width = len(value) * font.WIDTH
            val_x = tft.width - right_margin - value_width
            tft.text(font, value, val_x, current_y, fg, bg)

            current_y += font.HEIGHT + line_gap


# --------------------------------------------------------------------
# Example usage
data = [
    ("", "GW-5600"),
    ("Next Alarm:", "6:45"),
    ("Rem:", "Meet for breakfast"),
    ("TimeZone:", "America/Toronto"),
    ("Last Update", "18:30"),
]

display_data(data)
