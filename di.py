# A simple Dependency Injection (DI) module to manage what modules to be imported depending on certain conditions.
# For example, if some devices do not have a display, we can import a duymmy display module instead.

from lib.display.display import display
from lib.display.touch import touch

