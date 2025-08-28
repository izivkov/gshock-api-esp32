import sys
current_path = sys.path[0]
sys.path.append(current_path + '/lib/config')
sys.path.append(current_path + '/lib/gshock_api')
sys.path.append(current_path + '/lib/display')
sys.path.append(current_path + '/lib/utils')

from config_manager import config_manager
from network_time_setter import network_time_setter
from logger import logger

def set_time_on_board():
    config_manager.load()

    if not config_manager.get("ssid") or not config_manager.get("password"):
        logger.error(f" {config_manager.get_instructions()}")
        return

    time_set = network_time_setter.set_time(config_manager.get("ssid"), config_manager.get("password"), config_manager.get("timezone"))
    if not time_set:
        logger.error("Failed to set time. Please check your configuration.")
    else:
        logger.error("Time SET!")

set_time_on_board()