import uasyncio as asyncio
import time

from gshock_api.connection import Connection
from gshock_api.gshock_api import GshockAPI
from gshock_api.iolib.button_pressed_io import WatchButton
from gshock_api.logger import logger
from gshock_api.watch_info import watch_info
# from args import args
from gshock_api.exceptions import GShockConnectionError


__author__ = "Ivo Zivkov"
__copyright__ = "Ivo Zivkov"
__license__ = "MIT"


async def main():
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
            connected = await connection.connect(excluded_watches)
            if not connected:
                logger.info("Connect attempt failed; retrying...")
                await asyncio.sleep(1)
                continue

            logger.info("Connected...")

            api = GshockAPI(connection)
            pressed_button = await api.get_pressed_button()

            if (pressed_button != WatchButton.LOWER_RIGHT
                    and pressed_button != WatchButton.NO_BUTTON
                    and pressed_button != WatchButton.LOWER_LEFT):
                continue

            logger.info("Pressed button: {}".format(pressed_button))

            watch_name = await api.get_watch_name()
            logger.info("Watch name: {}".format(watch_name))

            # Apply fine adjustment to the time
            # fine_adjustment_secs = args.get().fine_adjustment_secs
            fine_adjustment_secs = 0

            await api.set_time(offset=fine_adjustment_secs)

            now_tuple = time.localtime()
            now_str = "{}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
                now_tuple[0], now_tuple[1], now_tuple[2], now_tuple[3], now_tuple[4], now_tuple[5]
            )
            logger.info("Time set at {} on {}".format(now_str, watch_info.name))

            watch_name = await api.get_watch_name()
            logger.info("Watch name: {}".format(watch_name))

            if watch_info.alwaysConnected == False:
                await connection.disconnect()

        except GShockConnectionError as e:
            logger.error("Got error: {}".format(e))
            continue

# Start the main loop
asyncio.run(main())
