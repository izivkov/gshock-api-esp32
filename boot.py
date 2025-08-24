from lib.config.config_manager import config_manager
from lib.config.network_time_setter import network_time_setter
from gshock_api.logger import logger
from lib.display.led import led, LEDController

def set_time_on_board():
    config_manager.load()

    if not config_manager.get("ssid") or not config_manager.get("password"):
        logger.error(f" {config_manager.get_instructions()}")
        led.set_mode(LEDController.MODE_SOLID_RED)
        return

    time_set = network_time_setter.set_time(config_manager.get("ssid"), config_manager.get("password"), config_manager.get("timezone"))
    if not time_set:
        logger.error("Failed to set time. Please check your configuration.")
        led.set_mode(LEDController.MODE_SOLID_RED)
        return

set_time_on_board()