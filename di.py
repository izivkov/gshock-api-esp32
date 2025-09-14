# A simple Dependency Injection (DI) module to manage what modules to be imported depending on certain conditions.
# For example, if some devices do not have a display, we can import a duymmy display module instead.

import os

info = os.uname()
print("os.uname", info)

from lib.display.display import display
from lib.display.touch import touch
from lib.display.led import led, LEDController

