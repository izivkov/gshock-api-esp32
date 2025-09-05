import machine
import time

# GPIO pin definitions for the touch controller
TP_INT_PIN = 21   # GPIO for the Touch Interrupt line
TP_RESET_PIN = 20 # GPIO for the Touch Reset line

class Touch:
    """A class to handle touch detection via GPIO interrupt for the AXS5106L."""
    
    def __init__(self):
        """Initializes the touch controller and the GPIO interrupt."""
        self._touch_event_occurred = False
        self._last_touch_time = 0
        self._reset_touch_controller()
        self._setup_interrupt()
        print("Touch module initialized and ready.")

    def _reset_touch_controller(self):
        """Performs a hardware reset on the touch controller."""
        print("Resetting touch controller...")
        reset = machine.Pin(TP_RESET_PIN, machine.Pin.OUT)
        reset.value(0)
        time.sleep_ms(10)
        reset.value(1)
        time.sleep_ms(100)
        print("Reset complete.")

    def _interrupt_handler(self, pin):
        """Interrupt service routine for the touch panel."""
        current_time = time.ticks_ms()
        # Use a debounce timer to avoid multiple triggers from a single touch
        if time.ticks_diff(current_time, self._last_touch_time) > 100:
            self._touch_event_occurred = True
            self._last_touch_time = current_time

    def _setup_interrupt(self):
        """Sets up the GPIO interrupt for the touch pin."""
        tp_int = machine.Pin(TP_INT_PIN, machine.Pin.IN, machine.Pin.PULL_UP)
        tp_int.irq(trigger=machine.Pin.IRQ_FALLING, handler=self._interrupt_handler)
    
    def read(self):
        """
        Reads the touch state.
        
        Returns:
            bool: True if a touch has been detected since the last read, otherwise False.
        """
        if self._touch_event_occurred:
            self._touch_event_occurred = False
            return True
        return False

touch = Touch()