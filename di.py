"""
A simple Dependency Injection (DI) module to manage which modules should be imported depending on certain conditions.
For example, if some devices do not have a display, we can import a dummy display module instead.

However, we cannot distinguish programmatically between the two supported boards, "Super Mini ESP32" 
and "ESP32-C6-Touch-LCD-1.47", so we just pass the imports as they are.
"""

from lib.display.display import display
from lib.display.touch import touch
from lib.display.led import led, LEDController

import os

info = os.uname()
print("os.uname", info)

