import uasyncio as asyncio
import time

from gshock_api.connection import Connection
from gshock_api.gshock_api import GshockAPI
from gshock_api.iolib.button_pressed_io import WatchButton
from gshock_api.logger import logger
from gshock_api.watch_info import watch_info
from gshock_api.exceptions import GShockConnectionError, GShockIgnorableException
from config import network_time_setter
from config.config_manager import config_manager
from lib.display.led import led, LEDController

__author__ = "Ivo Zivkov"
__copyright__ = "Ivo Zivkov"
__license__ = "MIT"


async def main():    
    config_manager.load()
    
    if not config_manager.get("ssid") or not config_manager.get("password"):
        logger.error(f" {config_manager.get_instructions()}")
        led.red_on()
        # return
    
    await run_time_server()

def prompt():
    logger.info("==============================================================================================")
    logger.info("Short-press lower-right button on your watch to set time...")
    logger.info("")
    logger.info("If Auto-time set on watch, the watch will connect and run automatically up to 4 times per day.")
    logger.info("==============================================================================================")
    logger.info("")

async def run_time_server():
    excluded_watches = [
        "DW-H5600", "OCW-S400", "OCW-S400SG", "OCW-T200SB",
        "ECB-30", "ECB-20", "ECB-10", "ECB-50", "ECB-60", "ECB-70"
    ]

    prompt()

    while True:
        try:
            logger.info("Waiting for connection...")
            connection = Connection()
            led.set_mode(LEDController.MODE_BLINK_GREEN)
            connected = await connection.connect(excluded_watches)
            led.set_mode(LEDController.MODE_SMOOTH)

            if not connected:
                logger.info("Connect attempt failed; retrying...")
                await asyncio.sleep(1)
                continue

            api = GshockAPI(connection)
            pressed_button = await api.get_pressed_button()

            if (pressed_button != WatchButton.LOWER_RIGHT
                    and pressed_button != WatchButton.NO_BUTTON
                    and pressed_button != WatchButton.LOWER_LEFT):
                continue

            # Apply fine adjustment to the time
            # fine_adjustment_secs = args.get().fine_adjustment_secs
            fine_adjustment_secs = 0

            await api.set_time(offset=fine_adjustment_secs)

            now_tuple = time.localtime()
            now_str = "{}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
                now_tuple[0], now_tuple[1], now_tuple[2], now_tuple[3], now_tuple[4], now_tuple[5]
            )
            logger.info("Time set at {} on {}".format(now_str, watch_info.name))

            if watch_info.alwaysConnected == False:
                await connection.disconnect()

        except (GShockConnectionError, GShockIgnorableException) as e:
            led.set_mode(LEDController.MODE_BLINK_RED)
            logger.error("Got error: {}".format(e))
            continue

        except Exception as e: # Just in case
            led.set_mode(LEDController.MODE_BLINK_RED)
            logger.error("Unknown error: {}".format(e))
            continue

# Start the main loop
asyncio.run(main())
